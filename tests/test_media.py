import asyncio
import io
import json
import shutil
import struct
import threading
import wave
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

import media
import media_worker
import player
from config import FFMPEG_OPTIONS, YDL_OPTIONS, Settings
from media import Media, MediaError, validate_query
from models import Track


def test_working_options_unchanged():
    assert YDL_OPTIONS == {
        "format": "m4a/bestaudio/best",
        "noplaylist": False,
        "extract_flat": False,
        "ignoreerrors": True,
    }
    assert FFMPEG_OPTIONS == {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }


@pytest.mark.parametrize(
    "query,target",
    [
        ("go blackpink", "ytsearch:go blackpink"),
        ("https://youtu.be/2GJfWMYCWY0", "https://youtu.be/2GJfWMYCWY0"),
    ],
)
def test_worker_full_extraction_preserves_first_stream(monkeypatch, capfd, query, target):
    calls, options = [], []

    class YDL:
        def __init__(self, opts):
            options.append(opts)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, query, download):
            calls.append(query)
            return {
                "entries": [{"id": "original", "title": "Song", "url": "exact-original-stream"}]
            }

    monkeypatch.setattr(media_worker, "YoutubeDL", YDL)
    media_worker.extract({"query": query, "limit": 25})
    output = [json.loads(line) for line in capfd.readouterr().out.splitlines()]
    assert calls == [target]
    assert output[1]["source"] == "exact-original-stream"
    assert "cookiefile" not in options[0]
    assert "extractor_args" not in options[0]
    assert "js_runtimes" not in options[0]


def test_worker_partial_playlist(monkeypatch, capfd):
    class YDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, *args, **kwargs):
            return {
                "title": "Mix",
                "entries": iter([None, {"id": "a", "title": "A", "url": "stream"}]),
            }

    monkeypatch.setattr(media_worker, "YoutubeDL", YDL)
    media_worker.extract({"query": "https://youtube.com/playlist?list=x", "limit": 25})
    output = [json.loads(line) for line in capfd.readouterr().out.splitlines()]
    assert output[-1]["count"] == output[-1]["failed"] == 1


@pytest.mark.parametrize("capture", ["capsys", "capfd"])
def test_worker_protocol_respects_active_stdout_and_separates_status(monkeypatch, request, capture):
    captured = request.getfixturevalue(capture)
    original_console = io.StringIO()
    monkeypatch.setattr(media_worker.sys, "__stdout__", original_console)

    class YDL:
        def __init__(self, options):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, *args, **kwargs):
            print("extractor status, not a protocol message")
            return {"id": "example", "title": "Example", "url": "fake-stream"}

    monkeypatch.setattr(media_worker, "YoutubeDL", YDL)
    media_worker.extract({"query": "example", "limit": 1})
    output = captured.readouterr()
    assert original_console.getvalue() == ""
    messages = [json.loads(line) for line in output.out.splitlines()]
    assert [message["type"] for message in messages] == ["header", "track", "done"]
    assert messages[1]["source"] == "fake-stream"
    assert "extractor status" in output.err


@pytest.mark.parametrize(
    "text,code",
    [
        ("HTTP Error 403", "audio_forbidden"),
        ("HTTP 429", "rate_limited"),
        ("Sign in to confirm you're not a bot", "bot_verification"),
        ("does not look like a Netscape format cookies file", "cookies_invalid"),
        ("cookies have expired", "cookies_expired"),
        ("age-restricted", "age_restricted"),
        ("Sign in to confirm your age", "age_restricted"),
        ("private video", "unavailable"),
        ("login required", "authentication_required"),
        ("not available in your country", "region_restricted"),
        ("Requested format is not available. Use --list-formats", "format_unavailable"),
        ("No video formats found", "format_unavailable"),
        ("An optional feature is not available", "extraction_failed"),
        ("unknown", "extraction_failed"),
    ],
)
def test_classification_without_raw_exception(text, code):
    assert media_worker.classify(text) == code
    assert str(MediaError(code)) == code


@pytest.mark.parametrize("warning,hint", media_worker.WARNING_HINTS)
def test_warning_diagnostics_are_fixed_codes(warning, hint):
    logger = media_worker.QuietLogger()
    logger.warning(warning + " https://example.test/audio?signature=secret")
    assert logger.diagnostics == {hint}
    assert logger.code == "extraction_failed"


def test_diagnostics_drop_unrecognized_or_sensitive_values():
    error = MediaError("bot_verification", ["signature_challenge_failed", "secret-cookie-path"])
    assert error.diagnostics == ("signature_challenge_failed",)
    assert "secret" not in str(error)


def test_worker_preserves_safe_hints_on_failure(monkeypatch, capfd):
    class FailedYDL:
        def __init__(self, options):
            self.logger = options["logger"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, *args, **kwargs):
            self.logger.warning("Signature solving failed: https://secret.example/signed-audio")
            self.logger.error("Sign in to confirm you're not a bot")
            return None

    monkeypatch.setattr(media_worker, "YoutubeDL", FailedYDL)
    with pytest.raises(MediaError) as failure:
        media_worker.extract({"query": "example", "limit": 1})
    assert failure.value.code == "bot_verification"
    assert failure.value.diagnostics == ("signature_challenge_failed",)
    assert "secret.example" not in capfd.readouterr().out


def test_real_ytdlp_cookie_updates_do_not_rewrite_operator_file(tmp_path):
    path = tmp_path / "operator.cookies.txt"
    contents = "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tTRUE\t2147483647\tTEST_ONLY\tfake-value\n"
    path.write_text(contents, encoding="utf-8")
    from yt_dlp import YoutubeDL

    with media_worker.cookie_input(path) as stream:
        with YoutubeDL({"cookiefile": stream, "logger": media_worker.QuietLogger()}) as ydl:
            assert any(cookie.name == "TEST_ONLY" for cookie in ydl.cookiejar)
            ydl.cookiejar.clear()  # Simulate a session update; close saves it to RAM.
        assert "TEST_ONLY" not in stream.getvalue()
        assert path.read_text(encoding="utf-8") == contents
    assert stream.closed


@pytest.mark.parametrize("authenticated", [False, True])
def test_real_extractor_recognizes_fake_auth_cookie_presence_offline(tmp_path, authenticated):
    path = tmp_path / "test.cookies.txt"
    contents = "# Netscape HTTP Cookie File\n"
    if authenticated:
        contents += ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tLOGIN_INFO\tfake-login\n"
        contents += ".youtube.com\tTRUE\t/\tTRUE\t2147483647\tSAPISID\tfake-session\n"
    path.write_text(contents, encoding="utf-8")
    from yt_dlp import YoutubeDL

    with media_worker.cookie_input(path) as stream:
        with YoutubeDL({"cookiefile": stream, "logger": media_worker.QuietLogger()}) as ydl:
            assert ydl.get_info_extractor("Youtube").is_authenticated is authenticated
    assert path.read_text(encoding="utf-8") == contents


def test_cookie_input_missing_file_has_safe_recoverable_error(tmp_path):
    path = tmp_path / "private-path-that-must-not-be-logged.txt"
    with pytest.raises(MediaError) as failure:
        with media_worker.cookie_input(path):
            pass
    assert failure.value.code == "cookies_invalid"
    assert str(path) not in str(failure.value)


def test_cookie_input_stream_closes_on_failure(tmp_path):
    path = tmp_path / "test.cookies.txt"
    path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        with media_worker.cookie_input(path) as stream:
            raise RuntimeError("test failure")
    assert stream.closed


@pytest.mark.parametrize("authenticated", [False, True])
def test_cookie_diagnostics_distinguish_missing_auth_without_network(
    monkeypatch, tmp_path, authenticated
):
    path = tmp_path / "test.cookies.txt"
    path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

    class YDL:
        def __init__(self, options):
            self.logger = options["logger"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get_info_extractor(self, name):
            return SimpleNamespace(is_authenticated=authenticated)

        def extract_info(self, *args, **kwargs):
            self.logger.error("Sign in to confirm your age")
            return None

    monkeypatch.setattr(media_worker, "YoutubeDL", YDL)
    with pytest.raises(MediaError) as failure:
        media_worker.extract({"query": "test", "limit": 1, "cookies": str(path)})
    assert failure.value.code == "age_restricted"
    assert failure.value.diagnostics == (
        "auth_cookies_recognized" if authenticated else "auth_cookies_missing",
    )
    assert str(path) not in str(failure.value)


@pytest.mark.parametrize(
    "query",
    [
        "name",
        "https://youtu.be/id",
        "https://www.youtube.com/watch?v=id",
        "www.youtube.com/watch?v=id",
    ],
)
def test_supported_queries(query):
    validate_query(query)


@pytest.mark.parametrize(
    "query", ["https://evil.example/a", "https://youtube.com.evil/a", "", "a" * 501, "a\nb"]
)
def test_unsupported_queries(query):
    with pytest.raises(MediaError, match="invalid_query"):
        validate_query(query)


async def test_empty_audio_never_looks_like_success(monkeypatch):
    cleaned = threading.Event()

    class Empty:
        def __init__(self, url, **kwargs):
            kwargs["stderr"].write(b"Server returned 403 Forbidden")

        def read(self):
            return b""

        def cleanup(self):
            cleaned.set()

    monkeypatch.setattr(player.discord, "FFmpegPCMAudio", Empty)
    with pytest.raises(MediaError, match="audio_forbidden"):
        await player.open_audio(Track("A", "original", "signed-stream"), "ffmpeg")
    assert cleaned.is_set()


async def test_cancel_blocked_pcm_read_kills_source(monkeypatch):
    entered, release = threading.Event(), threading.Event()

    class Blocked:
        def __init__(self, *args, **kwargs):
            pass

        def read(self):
            entered.set()
            release.wait()
            return b""

        def cleanup(self):
            release.set()

    monkeypatch.setattr(player.discord, "FFmpegPCMAudio", Blocked)
    task = asyncio.create_task(player.open_audio(Track("A", "original", "stream"), "ffmpeg"))
    await asyncio.to_thread(entered.wait)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert release.is_set()


async def test_real_offline_pcm_decoding(tmp_path):
    executable = shutil.which("ffmpeg") or (
        "C:/ffmpeg/bin/ffmpeg.exe"
        if __import__("os").path.isfile("C:/ffmpeg/bin/ffmpeg.exe")
        else None
    )
    if not executable:
        pytest.skip("FFmpeg not installed")
    path = tmp_path / "tone.wav"
    with wave.open(str(path), "wb") as output:
        output.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
        output.writeframes(
            b"".join(struct.pack("<hh", 1000 if i % 20 else -1000, 1000) for i in range(4800))
        )
    content = path.read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/tone.wav"
    source = None
    try:
        source = await player.open_audio(Track("Tone", url, url), executable)
        frame = source.read()
        assert len(frame) == 3840
        assert any(frame)
    finally:
        if source:
            source.cleanup()
        await asyncio.to_thread(server.shutdown)
        server.server_close()
        thread.join()


def test_ffmpeg_failure_after_first_frame_is_not_normal_completion():
    class FailedAudio:
        def read(self):
            return b""

        _process = SimpleNamespace(wait=lambda **kwargs: 1)

        def cleanup(self):
            pass

    source = player.PrefetchedPCM(FailedAudio(), b"first-frame", io.BytesIO(b"HTTP 403 Forbidden"))
    assert source.read() == b"first-frame"
    assert source.read() == b""
    assert source.failure.code == "audio_forbidden"
    source.cleanup()


class Process:
    def __init__(self):
        self.returncode = None
        self.reading = asyncio.Event()
        self.stdout = self
        self.stdin = SimpleNamespace(write=lambda data: None, drain=self.drain, close=lambda: None)

    async def drain(self):
        pass

    async def readline(self):
        self.reading.set()
        await asyncio.Event().wait()


async def test_process_permit_retained_until_real_cleanup(monkeypatch):
    created, cleaning, release = asyncio.Queue(), asyncio.Event(), asyncio.Event()

    async def spawn(*args, **kwargs):
        process = Process()
        created.put_nowait(process)
        return process

    async def cleanup(process):
        cleaning.set()
        await release.wait()
        process.returncode = -9

    monkeypatch.setattr(media.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(media, "terminate_tree", cleanup)
    service = Media(replace(Settings(), workers=1))

    async def consume():
        async for _ in service.extract("song", 1):
            pass

    first = asyncio.create_task(consume())
    process = await created.get()
    await process.reading.wait()
    first.cancel()
    await cleaning.wait()
    assert service.capacity._value == 0
    second = asyncio.create_task(consume())
    await asyncio.sleep(0)
    assert created.empty()  # A real worker is still being reaped.
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await first
    other = await created.get()
    await other.reading.wait()
    second.cancel()
    with pytest.raises(asyncio.CancelledError):
        await second


async def test_external_timeout_reaps_worker(monkeypatch):
    process = Process()

    async def spawn(*args, **kwargs):
        return process

    async def cleanup(process):
        process.returncode = -9

    monkeypatch.setattr(media.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(media, "terminate_tree", cleanup)
    service = Media(replace(Settings(), extraction_timeout=0.02, workers=1))
    with pytest.raises(MediaError, match="timeout"):
        async for _ in service.extract("song", 1):
            pass
    assert process.returncode == -9
    assert service.capacity._value == 1
