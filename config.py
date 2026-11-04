"""Runtime settings. Importing this module never reads credentials."""

import math
import os
import shutil
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Preserve the working extractor selector, defaults, and PCM FFmpeg flags.
YDL_OPTIONS = {
    "format": "m4a/bestaudio/best",
    "noplaylist": False,
    "extract_flat": False,
    "ignoreerrors": True,
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@dataclass(frozen=True)
class Settings:
    token: str = field(default="", repr=False)
    prefix: str = "-"
    cookies: str = field(default="", repr=False)
    ffmpeg: str = "ffmpeg"
    data_dir: Path = ROOT / "data"
    workers: int = 3
    audio_workers: int = 2
    pending_global: int = 12
    pending_guild: int = 3
    playlist_limit: int = 50
    queue_limit: int = 200
    extraction_timeout: float = 60
    connect_timeout: float = 30
    stream_max_age: float = 120

    def __post_init__(self):
        validate_prefix(self.prefix)
        for name in (
            "workers",
            "audio_workers",
            "pending_global",
            "pending_guild",
            "playlist_limit",
            "queue_limit",
            "extraction_timeout",
            "connect_timeout",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite positive number.")
            if name not in {"extraction_timeout", "connect_timeout"} and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                raise ValueError(f"{name} must be a positive integer.")
        if self.stream_max_age < 0 or not math.isfinite(self.stream_max_age):
            raise ValueError("stream_max_age must be finite and nonnegative.")

    @classmethod
    def load(cls):
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
        data_dir = Path(os.getenv("CRUMMY_DATA_DIR", str(ROOT / "data"))).expanduser()
        limits = {}
        for field_name, variable, alias, parser in (
            ("workers", "WORKERS", "CRUMMY_EXTRACT_WORKERS", int),
            ("audio_workers", "AUDIO_WORKERS", "CRUMMY_AUDIO_WORKERS", int),
            ("pending_global", "REQUESTS", "CRUMMY_PENDING_GLOBAL", int),
            ("pending_guild", "GUILD_REQUESTS", "CRUMMY_PENDING_GUILD", int),
            ("playlist_limit", "PLAYLIST_LIMIT", "CRUMMY_PLAYLIST_LIMIT", int),
            ("queue_limit", "QUEUE_LIMIT", "CRUMMY_QUEUE_LIMIT", int),
            ("extraction_timeout", "EXTRACT_TIMEOUT", "CRUMMY_EXTRACTION_TIMEOUT", float),
            ("connect_timeout", "CONNECT_TIMEOUT", "CRUMMY_CONNECT_TIMEOUT", float),
            ("stream_max_age", "STREAM_MAX_AGE", "CRUMMY_STREAM_MAX_AGE", float),
        ):
            # Retain the operator's established names; accept the recently
            # introduced CRUMMY_* spellings only as lower-priority aliases.
            variable = variable if variable in os.environ else alias
            if variable in os.environ:
                try:
                    limits[field_name] = parser(os.environ[variable])
                except ValueError:
                    raise ValueError(f"{variable} must contain a valid number.") from None
        settings = cls(
            token=os.getenv("DISCORD_API_TOKEN", ""),
            prefix=os.getenv("DISCORD_BOT_PREFIX", "-"),
            cookies=os.getenv("YTDLP_COOKIES_FILE", "").strip(),
            ffmpeg=os.getenv("FFMPEG_EXECUTABLE", "ffmpeg"),
            data_dir=data_dir if data_dir.is_absolute() else ROOT / data_dir,
            **limits,
        )
        if not settings.token:
            raise ValueError("Set DISCORD_API_TOKEN in .env before starting the bot.")
        validate_prefix(settings.prefix)
        if not shutil.which(settings.ffmpeg):
            raise ValueError("FFmpeg was not found. Install it and reopen your terminal.")
        if not shutil.which("deno"):
            raise ValueError(
                "Deno was not found. Install Deno and reopen your terminal for YouTube JavaScript challenges."
            )
        if settings.cookies and (
            not Path(settings.cookies).is_absolute() or not Path(settings.cookies).is_file()
        ):
            raise ValueError("YTDLP_COOKIES_FILE must point to an existing Netscape cookies file.")
        try:
            version("yt-dlp-ejs")
        except PackageNotFoundError:
            raise ValueError(
                "The EJS solver is missing. Install dependencies with: uv sync --locked"
            ) from None
        return settings


def validate_prefix(value):
    if not 1 <= len(value) <= 10 or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError("Use a prefix of 1–10 characters without spaces.")
