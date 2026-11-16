import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import media_worker
import player
from media import Media, MediaError
from models import State
from music_commands import MusicCommands
from tests.conftest import entry, started


@pytest.mark.parametrize("forced", [False, True])
async def test_working_queued_stream_is_tried_before_any_refresh(session, monkeypatch, forced):
    song = entry("A")
    song.track.resolved_at = None if forced else player.time.monotonic() - 121
    sources = []

    async def refresh(track, guild_id):
        track.source = "rejected-refresh"

    async def audio(track, executable):
        sources.append(track.source)
        if track.source == "rejected-refresh":
            raise MediaError("audio_forbidden")
        return SimpleNamespace(cleanup=lambda: None)

    session.media.refresh = AsyncMock(side_effect=refresh)
    monkeypatch.setattr(player, "open_audio", audio)
    session.pending = [song, entry("B")]
    session.start_playing()
    await started(session)
    assert sources == ["stream:A"]
    assert session.current is song
    assert [item.title for item in session.pending] == ["B"]
    session.media.refresh.assert_not_awaited()


async def test_forbidden_audio_gets_one_verified_retry_of_same_video(session, monkeypatch):
    song = entry("A")
    sources = []

    async def refresh(track, guild_id, *, verify_audio=False):
        track.source = "verified-stream" if verify_audio else "rejected-refresh"

    async def audio(track, executable):
        sources.append(track.source)
        if track.source != "verified-stream":
            raise MediaError("audio_forbidden")
        return SimpleNamespace(cleanup=lambda: None)

    session.media.refresh = AsyncMock(side_effect=refresh)
    monkeypatch.setattr(player, "open_audio", audio)
    session.pending = [song, entry("B")]
    session.start_playing()
    await started(session)
    assert sources == ["stream:A", "verified-stream"]
    assert session.current is song
    session.media.refresh.assert_awaited_once_with(song.track, session.guild_id, verify_audio=True)


async def test_saved_url_failure_goes_directly_to_format_check(session, monkeypatch, caplog):
    song = entry("A")
    steps = []

    async def refresh(track, guild_id, *, verify_audio=False):
        assert track is song.track
        assert verify_audio
        steps.append("check-formats")
        track.source = "renewed"

    async def audio(track, executable):
        steps.append("open:" + track.source)
        if track.source == "stream:A":
            raise MediaError("audio_forbidden")
        return SimpleNamespace(cleanup=lambda: None)

    session.media.refresh = AsyncMock(side_effect=refresh)
    monkeypatch.setattr(player, "open_audio", audio)
    session.pending = [song, entry("B")]
    with caplog.at_level("INFO"):
        session.start_playing()
        await started(session)
    assert steps == ["open:stream:A", "check-formats", "open:renewed"]
    session.media.refresh.assert_awaited_once_with(song.track, session.guild_id, verify_audio=True)
    retries = [
        record
        for record in caplog.records
        if record.getMessage().startswith("Checking playable formats for the same video |")
    ]
    assert len(retries) == 1
    assert "attempt=1" in retries[0].getMessage()
    assert "Refreshing rejected audio URL" not in caplog.text
    assert session.current is song
    assert [item.title for item in session.pending] == ["B"]


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
async def test_repeated_forbidden_holds_queue_and_resume_retries(session, monkeypatch, ctx, mode):
    attempts = []
    blocked = True

    async def audio(track, executable):
        attempts.append(track.title)
        if blocked:
            raise MediaError("audio_forbidden")
        return SimpleNamespace(cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    session.media.refresh = AsyncMock()
    songs = [entry(name) for name in "ABC"]
    session.pending = songs.copy()
    session.loop_mode = mode
    session.start_playing()
    await session.driver
    await asyncio.sleep(0)
    assert attempts == ["A", "A"]
    assert session.queue == songs
    assert session.state == State.PAUSED
    assert session.playback_blocked
    assert not session.voice_client.is_playing()
    session.start_playing()
    assert session.driver is None
    blocked = False
    cog = MusicCommands(None, session.manager)
    await cog.resume.callback(cog, ctx)
    await started(session)
    assert session.current is songs[0]
    assert session.queue == songs
    assert not session.playback_blocked


@pytest.mark.parametrize("action", ["skip", "remove", "jump", "clear"])
async def test_controls_work_while_audio_access_is_blocked(session, monkeypatch, action):
    async def audio(track, executable):
        if track.title == "A":
            raise MediaError("audio_forbidden")
        return SimpleNamespace(cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    session.media.refresh = AsyncMock()
    session.pending = [entry(name) for name in "ABC"]
    session.start_playing()
    await session.driver
    await asyncio.sleep(0)
    if action == "clear":
        await session.clear()
        assert not session.queue
    else:
        if action == "skip":
            session.skip()
        elif action == "remove":
            session.remove(1)
        else:
            session.jump(2)
        await started(session)
        assert session.current.title == "B"
    assert not session.playback_blocked


async def test_clear_during_verified_recovery_cannot_restart_old_track(session, monkeypatch):
    entered = asyncio.Event()

    async def audio(track, executable):
        raise MediaError("audio_forbidden")

    async def refresh(*args, **kwargs):
        entered.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(player, "open_audio", audio)
    session.media.refresh = refresh
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await entered.wait()
    await session.clear()
    assert not session.queue
    assert not session.playback_blocked
    assert session.voice_client.starts.empty()


async def test_refresh_is_atomic_and_preserves_diagnostics_on_failure(session):
    song = entry("A")
    service = Media(session.settings)

    async def extract(*args, **kwargs):
        yield {"type": "track", "source": "partial-worker-result"}
        raise MediaError("bot_verification", ["auth_cookies_recognized"])

    service.extract = extract
    with pytest.raises(MediaError, match="bot_verification"):
        await service.refresh(song.track, 1)
    assert song.track.source == "stream:A"


@pytest.mark.parametrize("verify", [False, True])
async def test_refresh_uses_same_canonical_url_and_opt_in_verification(session, caplog, verify):
    song = entry("A")
    service = Media(session.settings)
    calls = []

    async def extract(query, guild_id, **kwargs):
        calls.append((query, guild_id, kwargs))
        yield {"type": "header", "diagnostics": ["auth_cookies_recognized", "secret-value"]}
        yield {"type": "track", "source": "renewed"}
        yield {"type": "done"}

    service.extract = extract
    with caplog.at_level("INFO"):
        await service.refresh(song.track, 1, verify_audio=verify)
    assert calls == [
        (song.track.original_url, 1, {"limit": 1, **({"verify_audio": True} if verify else {})})
    ]
    assert song.track.source == "renewed"
    assert "auth_cookies_recognized" in caplog.text
    assert "secret-value" not in caplog.text


def test_recovery_checks_selected_formats_without_changing_selector(monkeypatch, capsys):
    options = []

    class YDL:
        def __init__(self, opts):
            options.append(opts)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def extract_info(self, target, download):
            assert target == "https://youtu.be/A"
            return {"id": "A", "title": "A", "url": "verified"}

    monkeypatch.setattr(media_worker, "YoutubeDL", YDL)
    media_worker.extract({"query": "https://youtu.be/A", "limit": 1, "verify_audio": True})
    assert options[0]["check_formats"] == "selected"
    assert options[0]["format"] == "m4a/bestaudio/best"


def test_real_ytdlp_selector_falls_back_within_same_video_offline(monkeypatch):
    from yt_dlp import YoutubeDL

    checked = []

    def check_formats(self, formats, **kwargs):
        for fmt in formats:
            checked.append(fmt["format_id"])
            if fmt["format_id"] != "rejected-m4a":
                yield fmt

    monkeypatch.setattr(YoutubeDL, "_check_formats", check_formats)
    with YoutubeDL({**media_worker.YDL_OPTIONS, "check_formats": "selected", "quiet": True}) as ydl:
        info = ydl.process_ie_result(
            {
                "id": "same-video",
                "title": "Same video",
                "extractor": "generic",
                "webpage_url": "https://youtu.be/same-video",
                "formats": [
                    {
                        "format_id": "working-webm",
                        "ext": "webm",
                        "acodec": "opus",
                        "vcodec": "none",
                        "url": "https://example.test/audio.webm",
                    },
                    {
                        "format_id": "rejected-m4a",
                        "ext": "m4a",
                        "acodec": "aac",
                        "vcodec": "none",
                        "url": "https://example.test/audio.m4a",
                    },
                ],
            },
            download=False,
        )
    assert "rejected-m4a" in checked
    assert info["id"] == "same-video"
    assert info["format_id"] == "working-webm"


async def test_exhausted_formats_after_403_preserve_queue(session, monkeypatch):
    async def audio(*args):
        raise MediaError("audio_forbidden")

    monkeypatch.setattr(player, "open_audio", audio)
    session.media.refresh = AsyncMock(side_effect=MediaError("format_unavailable"))
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await session.driver
    await asyncio.sleep(0)
    assert session.playback_blocked
    assert [song.title for song in session.queue] == ["A", "B"]
