"""Readable console events with request correlation and no media URLs or queries."""

import logging
from contextlib import contextmanager
from contextvars import ContextVar

_guild = ContextVar("log_guild", default="-")
_request = ContextVar("log_request", default="-")


@contextmanager
def log_context(guild, request_id="-"):
    guild_token = _guild.set(str(guild))
    request_token = _request.set(str(request_id))
    try:
        yield
    finally:
        _request.reset(request_token)
        _guild.reset(guild_token)


def event(logger, message, *, level=logging.INFO, **metrics):
    suffix = " ".join(f"{key}={value}" for key, value in metrics.items())
    logger.log(
        level,
        message + (" | " + suffix if suffix else ""),
        extra={"guild": _guild.get(), "request_id": _request.get()},
    )


class ConsoleContext(logging.Filter):
    def filter(self, record):
        for field in ("guild", "request_id"):
            value = str(getattr(record, field, "-"))
            # Server names are untrusted: never allow multiline/terminal escapes.
            setattr(record, field, "".join(c if c.isprintable() else " " for c in value)[:120])
        return True


def configure_logging():
    handler = logging.StreamHandler()
    handler.addFilter(ConsoleContext())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s.%(msecs)03d %(levelname)-7s | server=%(guild)s | request=%(request_id)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logging.getLogger("discord").setLevel(logging.WARNING)
