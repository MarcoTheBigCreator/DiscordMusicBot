"""Exercise the production extraction/PCM path without logging in to Discord."""

import argparse
import asyncio
import json
import shutil
import sys
from contextlib import aclosing
from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import Settings
from media import Media, MediaError, track_from_event
from player import open_audio


async def diagnose(query, cookies=""):
    settings = replace(Settings(), cookies=cookies)
    media = Media(settings)
    result = {
        "python": sys.version.split()[0],
        "yt_dlp": version("yt-dlp"),
        "cookies_configured": bool(cookies),
        "extraction_ok": False,
        "audio_read_ok": False,
        "pcm_bytes": 0,
        "deno_available": shutil.which("deno") is not None,
    }
    try:
        result["yt_dlp_ejs"] = version("yt-dlp-ejs")
    except PackageNotFoundError:
        result["yt_dlp_ejs"] = "missing"
    source = None
    try:
        async with aclosing(media.extract(query, 0, limit=1)) as events:
            async for event in events:
                if event["type"] == "track":
                    result["extraction_ok"] = True
                    source = await open_audio(track_from_event(event), settings.ffmpeg)
                    # One prefetched 20ms PCM frame; uses the real production path.
                    frame = source.read()
                    result["pcm_bytes"] = len(frame)
                    result["audio_read_ok"] = len(frame) == 3840
    except Exception as exc:
        result["error_code"] = exc.code if isinstance(exc, MediaError) else type(exc).__name__
        result["diagnostics"] = list(exc.diagnostics) if isinstance(exc, MediaError) else []
    finally:
        if source:
            source.cleanup()
    print(json.dumps(result, indent=2))
    return result["audio_read_ok"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--cookies-file", default="", help="Optional Netscape file; never printed.")
    args = parser.parse_args()
    sys.exit(0 if asyncio.run(diagnose(args.query, args.cookies_file)) else 1)
