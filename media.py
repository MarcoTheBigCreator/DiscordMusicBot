"""Bounded, cancellable extraction processes. Never log queries or signed URLs."""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit

from config import ROOT
from logging_setup import event as log_event
from media_worker import MediaError
from models import Track

logger = logging.getLogger(__name__)


def validate_query(query):
    if not query or len(query) > 500 or any(ord(c) < 32 for c in query):
        raise MediaError("invalid_query")
    if query.startswith(("http://", "https://", "www.")):
        try:
            parsed = urlsplit(query if "://" in query else "https://" + query)
            host = parsed.hostname or ""
        except ValueError:
            raise MediaError("invalid_query") from None
        if parsed.username or parsed.password:
            raise MediaError("invalid_query")
        if host not in {
            "youtu.be",
            "youtube.com",
            "www.youtube.com",
            "music.youtube.com",
            "m.youtube.com",
        }:
            raise MediaError("invalid_query")


async def terminate_tree(process):
    if process.returncode is None:
        if os.name == "nt":
            killer = await asyncio.create_subprocess_exec(
                "taskkill",
                "/PID",
                str(process.pid),
                "/T",
                "/F",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            await killer.wait()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
    await process.wait()


class Media:
    def __init__(self, settings):
        self.settings = settings
        self.capacity = asyncio.Semaphore(settings.workers)
        self.guild_capacity = {}

    async def extract(self, query, guild_id, *, limit=None, verify_audio=False):
        validate_query(query)
        waiting = time.monotonic()
        try:
            async with asyncio.timeout(self.settings.extraction_timeout):
                async with (
                    self.guild_capacity.setdefault(guild_id, asyncio.Semaphore(1)),
                    self.capacity,
                ):
                    started = time.monotonic()
                    log_event(
                        logger,
                        "Extraction started",
                        operation="extract",
                        worker_wait_ms=round((started - waiting) * 1000),
                    )
                    flags = (
                        {
                            "creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
                            | subprocess.CREATE_NO_WINDOW
                        }
                        if os.name == "nt"
                        else {"start_new_session": True}
                    )
                    process = await asyncio.create_subprocess_exec(
                        sys.executable,
                        str(ROOT / "media_worker.py"),
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                        limit=1024 * 1024,
                        **flags,
                    )
                    result = "cancelled"
                    count = failed = 0
                    try:
                        request = {
                            "query": query,
                            "cookies": self.settings.cookies,
                            "limit": limit or self.settings.playlist_limit,
                        }
                        if verify_audio:
                            request["verify_audio"] = True
                        process.stdin.write((json.dumps(request) + "\n").encode())
                        await process.stdin.drain()
                        process.stdin.close()
                        done = False
                        while line := await process.stdout.readline():
                            data = json.loads(line)
                            if data["type"] == "error":
                                raise MediaError(data["code"], data.get("diagnostics", ()))
                            done |= data["type"] == "done"
                            if data["type"] == "track":
                                count += 1
                            if data["type"] == "done":
                                count, failed = data["count"], data["failed"]
                            yield data
                        if await process.wait() or not done:
                            raise MediaError("extraction_failed")
                        result = "ok"
                    except Exception:
                        result = "error"
                        raise
                    finally:
                        # Keep the capacity permit until the real process and its
                        # solver descendants are stopped, even after cancellation.
                        cleanup = asyncio.create_task(terminate_tree(process))
                        try:
                            await asyncio.shield(cleanup)
                        except asyncio.CancelledError:
                            await cleanup
                            raise
                        log_event(
                            logger,
                            "Extraction finished",
                            operation="extract",
                            result=result,
                            elapsed_ms=round((time.monotonic() - started) * 1000),
                            tracks=count,
                            failed=failed,
                        )
        except TimeoutError as exc:
            raise MediaError("timeout") from exc

    async def refresh(self, track, guild_id, *, verify_audio=False):
        replacement = None
        diagnostics = ()
        options = {"verify_audio": True} if verify_audio else {}
        async for event in self.extract(track.original_url, guild_id, limit=1, **options):
            if event["type"] == "header":
                diagnostics = event.get("diagnostics", ())
                if diagnostics:
                    log_event(
                        logger,
                        "Extractor session diagnostics",
                        operation="refresh",
                        diagnostics=",".join(
                            MediaError("extraction_failed", diagnostics).diagnostics
                        ),
                    )
            if event["type"] == "track":
                replacement = event["source"]
        if replacement is None:
            raise MediaError("unavailable")
        # A failed/cancelled worker must not partially overwrite the old stream.
        track.source = replacement
        track.resolved_at = time.monotonic()


def track_from_event(event):
    return Track(event["title"], event["original_url"], event["source"])
