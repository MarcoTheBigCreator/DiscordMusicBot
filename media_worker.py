"""Disposable yt-dlp process. JSON protocol on stdin/stdout; no dotenv loading."""

import contextlib
import io
import json
import sys

from discord.ext import commands
from yt_dlp import YoutubeDL

from config import YDL_OPTIONS

WARNING_HINTS = (
    ("signature solving failed", "signature_challenge_failed"),
    ("n challenge solving failed", "n_challenge_failed"),
    ("no supported javascript runtime", "javascript_runtime_missing"),
    ("remote components", "solver_components_warning"),
    ("po token", "po_token_warning"),
    ("cookies are no longer valid", "cookies_expired_warning"),
    ("cookies have expired", "cookies_expired_warning"),
)
HINT_CODES = frozenset(hint for _, hint in WARNING_HINTS) | {
    "auth_cookies_recognized",
    "auth_cookies_missing",
}


class MediaError(commands.CommandError):
    def __init__(self, code, diagnostics=()):
        self.code = code
        self.diagnostics = tuple(sorted(set(diagnostics) & HINT_CODES))
        super().__init__(code)


def classify(error):
    text = str(error).lower()
    for needles, code in [
        (("netscape", "cookies file", "cookiefile"), "cookies_invalid"),
        (("429", "too many requests"), "rate_limited"),
        (("403", "forbidden"), "audio_forbidden"),
        (("not a bot", "confirm you are human", "bot verification"), "bot_verification"),
        (("cookies are no longer valid", "cookies have expired"), "cookies_expired"),
        (("confirm your age", "age-restricted"), "age_restricted"),
        (("sign in", "login required", "members-only"), "authentication_required"),
        (("not available in your country", "geo-restricted"), "region_restricted"),
        (
            ("requested format is not available", "no video formats found", "no formats found"),
            "format_unavailable",
        ),
        (
            ("private video", "video unavailable", "video has been removed", "video was removed"),
            "unavailable",
        ),
    ]:
        if any(needle in text for needle in needles):
            return code
    return "extraction_failed"


class QuietLogger:
    def __init__(self):
        self.code = "extraction_failed"
        self.diagnostics = set()

    def debug(self, *args):
        pass

    def warning(self, message, *args):
        # Only known, fixed hints cross the process boundary. Never forward
        # yt-dlp's original text, which may contain signed URLs or cookie paths.
        text = str(message).lower()
        for needle, hint in WARNING_HINTS:
            if needle in text:
                self.diagnostics.add(hint)

    def error(self, message):
        self.code = classify(message)


def emit(payload, *, stream=None):
    print(json.dumps(payload, ensure_ascii=True), file=stream, flush=True)


@contextlib.contextmanager
def cookie_input(path):
    """Let yt-dlp update its in-memory jar without rewriting operator secrets."""
    if not path:
        yield None
        return
    try:
        with open(path, encoding="utf-8") as handle:
            contents = handle.read()
    except (OSError, UnicodeError):
        raise MediaError("cookies_invalid") from None
    # yt-dlp supports file-like cookie inputs and writes the jar back on close.
    # This writable memory stream protects the original file across workers.
    with io.StringIO(contents) as stream:
        yield stream


def extract(request):
    # Preserve the active protocol stream before redirecting extractor chatter.
    # sys.__stdout__ bypasses pytest capture and Windows console redirection.
    protocol_stream = sys.stdout

    def output(payload):
        emit(payload, stream=protocol_stream)

    logger = QuietLogger()
    options = dict(
        YDL_OPTIONS,
        logger=logger,
        socket_timeout=10,
        retries=1,
        extractor_retries=1,
        playlistend=request["limit"],
        lazy_playlist=True,
    )
    if request.get("verify_audio"):
        # Recovery only: test matching formats before returning another URL.
        # Keep the original selector and the exact same video.
        options["check_formats"] = "selected"
    query = request["query"]
    target = query if query.startswith(("https://", "http://", "www.")) else f"ytsearch:{query}"
    # Same full extraction as the original. No flat search + second lookup and
    # no forced YouTube client, cache disable, headers, format or solver changes.
    try:
        with cookie_input(request.get("cookies")) as cookies:
            if cookies is not None:
                options["cookiefile"] = cookies
            with contextlib.redirect_stdout(sys.stderr), YoutubeDL(options) as ydl:
                if cookies is not None:
                    # This is a local cookie-presence check, not confirmation
                    # that YouTube still accepts the account session.
                    authenticated = ydl.get_info_extractor("Youtube").is_authenticated
                    logger.diagnostics.add(
                        "auth_cookies_recognized" if authenticated else "auth_cookies_missing"
                    )
                extract_entries(ydl, target, request, logger, output)
    except Exception as exc:
        code = exc.code if isinstance(exc, MediaError) else classify(exc)
        raise MediaError(code, sorted(logger.diagnostics)) from None


def extract_entries(ydl, target, request, logger, output):
    info = ydl.extract_info(target, download=False)
    if not info:
        raise MediaError(logger.code)
    entries = info.get("entries")
    playlist = entries is not None and not target.startswith("ytsearch:")
    output(
        {
            "type": "header",
            "playlist": playlist,
            "title": str(info.get("title", "Unknown Playlist"))[:256],
            "diagnostics": sorted(logger.diagnostics),
        }
    )
    count = failed = 0
    for entry in entries if entries is not None else [info]:
        if not entry or not entry.get("url"):
            failed += 1
            continue
        output(
            {
                "type": "track",
                "title": str(entry.get("title", "Unknown"))[:256],
                "source": entry["url"],
                "original_url": entry.get("webpage_url")
                or f"https://www.youtube.com/watch?v={entry['id']}",
            }
        )
        count += 1
        if count + failed >= request["limit"]:
            break
    if not count:
        raise MediaError(logger.code)
    output(
        {
            "type": "done",
            "count": count,
            "failed": failed,
            "limited": count + failed >= request["limit"],
        }
    )


if __name__ == "__main__":
    try:
        extract(json.loads(sys.stdin.readline()))
    except Exception as exc:
        emit(
            {
                "type": "error",
                "code": exc.code if isinstance(exc, MediaError) else classify(exc),
                "diagnostics": list(exc.diagnostics) if isinstance(exc, MediaError) else [],
            }
        )
        sys.exit(1)
