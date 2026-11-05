"""Per-guild playback. Every state transition runs on the asyncio loop."""

import asyncio
import itertools
import logging
import random
import subprocess
import tempfile
import time
from contextlib import aclosing

import discord

from config import FFMPEG_OPTIONS
from constants import DEFAULT_LOOP_MODE, LOOP_ICONS, MESSAGES
from logging_setup import event as log_event
from logging_setup import log_context
from media import Media, MediaError, track_from_event
from models import QueueEntry, State
from views import fit_embed

logger = logging.getLogger(__name__)


async def send(channel, *, settings=None, **kwargs):
    """Discord notification failure cannot stop successful audio."""
    try:
        if settings is not None and settings.message_ttl is not None:
            kwargs.setdefault("delete_after", settings.message_ttl)
        if kwargs.get("embed"):
            kwargs["embed"] = fit_embed(kwargs["embed"])
        return await channel.send(**kwargs)
    except (discord.HTTPException, discord.Forbidden):
        log_event(
            logger,
            "Failed to send Discord message",
            level=logging.WARNING,
            operation="message",
            error_type="DiscordHTTPError",
        )


class PrefetchedPCM(discord.AudioSource):
    def __init__(self, source, first_frame, diagnostic):
        self.source, self.frame, self.diagnostic = source, first_frame, diagnostic
        self.failure = None

    def read(self):
        if self.frame:
            frame, self.frame = self.frame, b""
            return frame
        frame = self.source.read()
        if not frame:
            # discord.py treats FFmpeg EOF as normal completion, even when the
            # process failed. Preserve that distinction before applying loops.
            process = getattr(self.source, "_process", None)
            if process is not None:
                try:
                    status = process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    status = -1
                if status:
                    self.diagnostic.seek(0)
                    code = (
                        "audio_forbidden"
                        if b"403" in self.diagnostic.read(65536)
                        else "playback_failed"
                    )
                    self.failure = MediaError(code)
        return frame

    def cleanup(self):
        self.source.cleanup()
        self.diagnostic.close()


async def open_audio(track, executable):
    # Preserve PCM, format selection and FFmpeg flags from the working bot.
    diagnostic = tempfile.TemporaryFile()
    source = None
    try:
        source = discord.FFmpegPCMAudio(
            track.source, executable=executable, stderr=diagnostic, **FFMPEG_OPTIONS
        )
        read = asyncio.create_task(asyncio.to_thread(source.read))
        try:
            frame = await asyncio.wait_for(asyncio.shield(read), timeout=20)
        except BaseException:
            source.cleanup()
            await read
            raise
        if not frame:
            diagnostic.seek(0)
            code = "audio_forbidden" if b"403" in diagnostic.read(65536) else "playback_failed"
            raise MediaError(code)
        return PrefetchedPCM(source, frame, diagnostic)
    except BaseException:
        if source:
            source.cleanup()
        diagnostic.close()
        raise


class Session:
    def __init__(self, manager, guild_id):
        self.manager, self.guild_id = manager, guild_id
        self.bot, self.settings, self.media = manager.bot, manager.settings, manager.media
        self.current = None
        self.pending = []
        self.state = State.IDLE
        self.loop_mode = DEFAULT_LOOP_MODE
        self.voice_client = None
        self.connection_lock = asyncio.Lock()
        self.disconnect_lock = asyncio.Lock()
        self.voice_recovery = None
        self.now_playing_message = None
        self.now_playing_lock = asyncio.Lock()
        self.request_lock = asyncio.Lock()
        self.requests = set()
        self.generation = 0
        self.ticket = 0
        self.driver = None
        self.audio_source = None
        self.playback_blocked = False
        self.drivers = set()
        self.guild_label = str(guild_id)

    async def send(self, channel, **kwargs):
        return await send(channel, settings=self.settings, **kwargs)

    async def _delete_now_playing(self, message):
        try:
            await message.delete()
        except discord.NotFound:
            pass  # Already removed manually or by MESSAGE_TTL_SECONDS.
        except discord.HTTPException:
            with log_context(self.guild_label):
                log_event(
                    logger,
                    "Failed to delete previous Now Playing message",
                    level=logging.WARNING,
                    operation="message",
                    error_type="DiscordHTTPError",
                )

    async def show_now_playing(self, channel, entry, ticket):
        # Commands and automatic announcements share one message per server.
        # Serializing also prevents concurrent -np calls leaving duplicates.
        async with self.now_playing_lock:
            if self.current is not entry or self.ticket != ticket:
                return
            message = await self.send(
                channel,
                embed=discord.Embed(
                    title=MESSAGES["now_playing"],
                    description=entry.title,
                    color=discord.Color.light_gray(),
                ),
            )
            if message is None:
                return
            if self.current is not entry or self.ticket != ticket:
                await self._delete_now_playing(message)
                return
            previous, self.now_playing_message = self.now_playing_message, message
            if previous is not None:
                await self._delete_now_playing(previous)

    @property
    def queue(self):
        return ([self.current] if self.current else []) + self.pending

    @property
    def is_playing(self):
        return self.current is not None

    def active_voice(self):
        return self.voice_client and self.voice_client.is_connected()

    async def connect(self, ctx):
        started = time.monotonic()
        async with self.connection_lock:
            target = getattr(getattr(ctx.author, "voice", None), "channel", None)
            if not target:
                raise MediaError("not_in_voice")
            if self.active_voice():
                if self.voice_client.channel.id != target.id:
                    raise MediaError("different_channel")
                return
            if self.voice_recovery and not self.voice_recovery.done():
                raise MediaError("voice_reconnecting")
            generation = self.generation
            self.stop_current()
            self.pending.clear()
            if ctx.guild.voice_client:
                await ctx.guild.voice_client.disconnect(force=True)
            try:
                log_event(logger, "Connecting to voice channel", operation="connect")
                voice = await target.connect(timeout=self.settings.connect_timeout)
                if generation != self.generation:
                    await voice.disconnect(force=True)
                    raise MediaError("request_cancelled")
                self.voice_client = voice
                log_event(
                    logger,
                    "Voice connection ready",
                    operation="connect",
                    elapsed_ms=round((time.monotonic() - started) * 1000),
                )
            except asyncio.CancelledError:
                if ctx.guild.voice_client:
                    await ctx.guild.voice_client.disconnect(force=True)
                raise
            except (discord.DiscordException, OSError, TimeoutError) as exc:
                self.voice_client = None
                raise MediaError("connection_failed") from exc

    def reserve(self, ctx, query):
        name = getattr(ctx.guild, "name", "")
        self.guild_label = f"{name} ({self.guild_id})" if name else str(self.guild_id)
        if (
            len(self.requests) >= self.settings.pending_guild
            or self.manager.request_count >= self.settings.pending_global
        ):
            with log_context(self.guild_label):
                log_event(
                    logger,
                    "Request rejected: capacity reached",
                    level=logging.WARNING,
                    operation="request",
                    result="busy",
                    guild_requests=len(self.requests),
                    global_requests=self.manager.request_count,
                )
            raise MediaError("busy")
        self.manager.request_count += 1
        generation = self.generation
        request_id = f"{next(self.manager.request_ids):06d}"
        received_at = time.monotonic()
        with log_context(self.guild_label, request_id):
            log_event(
                logger,
                "Request accepted",
                operation="request",
                guild_requests=len(self.requests) + 1,
                global_requests=self.manager.request_count,
            )
        task = asyncio.create_task(self._request(ctx, query, generation, request_id, received_at))
        self.requests.add(task)
        task.add_done_callback(self._request_done)
        return task

    def _request_done(self, task):
        self.requests.discard(task)
        self.manager.request_count -= 1
        if not task.cancelled() and task.exception():
            logger.error(
                "guild=%s operation=request error_type=%s",
                self.guild_id,
                type(task.exception()).__name__,
            )

    async def _request(self, ctx, query, generation, request_id, received_at):
        with log_context(self.guild_label, request_id):
            try:
                await self._prepare_request(ctx, query, generation, request_id, received_at)
            except asyncio.CancelledError:
                log_event(logger, "Request cancelled", operation="request", result="cancelled")
                raise

    async def _prepare_request(self, ctx, query, generation, request_id, received_at):
        count = failed = 0
        preview = []
        was_playing = self.current is not None
        playlist = False
        title = ""
        try:
            # FIFO per guild, max one extraction per guild. Other guilds may
            # prepare concurrently; control commands never acquire this lock.
            async with self.request_lock:
                if generation != self.generation:
                    return
                log_event(
                    logger,
                    "Preparing request",
                    operation="request",
                    guild_wait_ms=round((time.monotonic() - received_at) * 1000),
                )
                await self.connect(ctx)
                if generation != self.generation:
                    return
                async with aclosing(self.media.extract(query, self.guild_id)) as events:
                    async for event in events:
                        if generation != self.generation:
                            return
                        if event["type"] == "header":
                            playlist, title = event["playlist"], event["title"]
                            if event.get("diagnostics"):
                                log_event(
                                    logger,
                                    "Extractor session diagnostics",
                                    operation="extract",
                                    diagnostics=",".join(event["diagnostics"]),
                                )
                        elif event["type"] == "track":
                            if len(self.queue) >= self.settings.queue_limit:
                                raise MediaError("queue_full")
                            entry = QueueEntry(
                                track_from_event(event),
                                ctx.channel,
                                ctx.author,
                                request_id,
                                received_at,
                            )
                            queued = self.current is not None or bool(self.pending)
                            self.pending.append(entry)
                            count += 1
                            if len(preview) < 3:
                                preview.append(entry.title)
                            self.start_playing()
                            if not playlist and queued:
                                embed = self.create_success_embed("queued")
                                embed.add_field(
                                    name=MESSAGES["song_field"], value=entry.title, inline=False
                                )
                                embed.add_field(
                                    name=MESSAGES["by_field"],
                                    value=ctx.author.mention,
                                    inline=False,
                                )
                                await self.send(ctx, embed=embed)
                        elif event["type"] == "done":
                            failed = event["failed"]
                            if event["limited"]:
                                await self.send(
                                    ctx,
                                    embed=self.create_info_embed(
                                        "playlist_limit", self.settings.playlist_limit
                                    ),
                                )
                if not count:
                    raise MediaError("song_not_found")
                log_event(
                    logger,
                    "Request ready",
                    operation="request",
                    result="ok",
                    added=count,
                    failed=failed,
                    elapsed_ms=round((time.monotonic() - received_at) * 1000),
                )
                if playlist:
                    embed = self.create_success_embed(
                        "playlist_queued" if was_playing else "playlist_added", count
                    )
                    embed.add_field(
                        name=MESSAGES["playlist_title"].format(title)[:256],
                        value=MESSAGES["playlist_count"].format(count),
                        inline=False,
                    )
                    embed.add_field(
                        name=MESSAGES["by_field"], value=ctx.author.mention, inline=False
                    )
                    embed.add_field(
                        name=MESSAGES["preview"],
                        value="\n".join(f"{i + 1}. {name}" for i, name in enumerate(preview))
                        + ("\n" + MESSAGES["more_songs"].format(count - 3) if count > 3 else ""),
                        inline=False,
                    )
                    if failed:
                        embed.add_field(
                            name="⚠️",
                            value=MESSAGES["playlist_partial"].format(count, count + failed),
                        )
                    await self.send(ctx, embed=embed)
        except MediaError as exc:
            log_event(
                logger,
                "Failed to prepare request",
                level=logging.WARNING,
                operation="request",
                result="error",
                error_code=exc.code,
                diagnostics=",".join(exc.diagnostics) or "none",
                added=count,
            )
            if generation == self.generation:
                await self.send(ctx, embed=self.create_error_embed(exc.code))
        except Exception as exc:
            log_event(
                logger,
                "Unexpected request preparation error",
                level=logging.ERROR,
                operation="request",
                error_type=type(exc).__name__,
            )
            if generation == self.generation:
                await self.send(ctx, embed=self.create_error_embed("extraction_failed"))

    def start_playing(self):
        if self.playback_blocked:
            return
        if self.current or not self.pending or not self.active_voice():
            return
        if self.driver and not self.driver.done():
            return
        self.driver = asyncio.create_task(self._start())
        self.drivers.add(self.driver)
        self.driver.add_done_callback(self._driver_done)

    def _driver_done(self, task):
        self.drivers.discard(task)
        if self.driver is task:
            self.driver = None
        if not task.cancelled() and task.exception():
            logger.error(
                "guild=%s operation=play error_type=%s",
                self.guild_id,
                type(task.exception()).__name__,
            )
        self.start_playing()

    async def _start(self):
        entry = self.pending.pop(0)
        with log_context(self.guild_label, entry.request_id):
            await self._play_entry(entry)

    async def _open_entry_audio(self, entry):
        async def attempt():
            waiting = time.monotonic()
            async with self.manager.audio_capacity:
                started = time.monotonic()
                source = await open_audio(entry.track, self.settings.ffmpeg)
            log_event(
                logger,
                "FFmpeg produced PCM audio",
                operation="audio",
                worker_wait_ms=round((started - waiting) * 1000),
                decode_ms=round((time.monotonic() - started) * 1000),
            )
            return source

        try:
            return await attempt()
        except MediaError as exc:
            if exc.code != "audio_forbidden":
                raise
        # Age alone does not mean a signed URL has expired. Always try the
        # saved URL first, including queued tracks and loop repetitions.
        log_event(
            logger,
            "Checking playable formats for the same video",
            operation="audio_retry",
            attempt=1,
        )
        try:
            await self.media.refresh(entry.track, self.guild_id, verify_audio=True)
        except MediaError as exc:
            if exc.code == "format_unavailable":
                # The selector exhausted its candidates after an actual 403.
                raise MediaError("audio_forbidden", exc.diagnostics) from None
            raise
        return await attempt()

    def retry_playback(self):
        if not self.playback_blocked:
            return False
        entry, self.current = self.current, None
        self.playback_blocked = False
        self.state = State.IDLE
        if entry is not None:
            self.pending.insert(0, entry)
        self.start_playing()
        return True

    async def _play_entry(self, entry):
        self.current = entry
        started = time.monotonic()
        log_event(
            logger,
            "Preparing audio",
            operation="audio",
            queue_wait_ms=round((started - entry.enqueued_at) * 1000),
        )
        self.state = State.PREPARING
        self.ticket += 1
        ticket = self.ticket
        source = None
        try:
            source = await self._open_entry_audio(entry)
            self.audio_source = source
            loop = asyncio.get_running_loop()
            self.voice_client.play(
                source,
                after=lambda error: loop.call_soon_threadsafe(
                    self._finished, ticket, error or getattr(source, "failure", None)
                ),
            )
            if self.state == State.PAUSED:
                self.voice_client.pause()
            else:
                self.state = State.PLAYING
            metrics = {
                "operation": "play",
                "state": self.state.value,
                "pending": len(self.pending),
                "loop": self.loop_mode,
                "startup_ms": round((time.monotonic() - started) * 1000),
            }
            if entry.received_at is not None:
                metrics["request_to_start_ms"] = round(
                    (time.monotonic() - entry.received_at) * 1000
                )
            log_event(logger, "Discord audio player started", **metrics)
        except asyncio.CancelledError:
            if source:
                source.cleanup()
            raise
        except Exception as exc:
            if source:
                source.cleanup()
            self.current = None
            self.audio_source = None
            self.state = State.IDLE
            code = exc.code if isinstance(exc, MediaError) else "playback_failed"
            if code in {
                "audio_forbidden",
                "bot_verification",
                "rate_limited",
                "cookies_invalid",
                "cookies_expired",
                "authentication_required",
                "timeout",
            }:
                self.current = entry
                self.state = State.PAUSED
                self.playback_blocked = True
            log_event(
                logger,
                "Failed to start audio",
                level=logging.WARNING,
                operation="play",
                result="error",
                error_code=code,
                diagnostics=",".join(exc.diagnostics)
                if isinstance(exc, MediaError) and exc.diagnostics
                else "none",
                error_type=type(exc).__name__,
            )
            await self.send(entry.channel, embed=self.create_error_embed(code))
            if self.playback_blocked:
                log_event(
                    logger,
                    "Playback held; queue preserved",
                    operation="play",
                    state="paused",
                    pending=len(self.pending),
                )
                await self.send(entry.channel, embed=self.create_info_embed("playback_held"))
            return
        # Kept separate from the playback try/except: embeds never invalidate audio.
        await self.show_now_playing(entry.channel, entry, ticket)

    def _finished(self, ticket, error):
        if ticket != self.ticket or not self.current:
            return
        entry, self.current = self.current, None
        if not self.active_voice():
            self.audio_source = None
            if self.state == State.PAUSED:
                self.current = entry
                self.playback_blocked = True
            else:
                self.state = State.IDLE
                entry.enqueued_at = time.monotonic()
                entry.received_at = None
                self.pending.insert(0, entry)
            with log_context(self.guild_label, entry.request_id):
                log_event(
                    logger,
                    "Audio interrupted by voice disconnect; track retained",
                    operation="voice_recovery",
                    pending=len(self.pending),
                )
            return
        with log_context(self.guild_label, entry.request_id):
            log_event(
                logger,
                "Playback finished" if not error else "Playback failed",
                level=logging.WARNING if error else logging.INFO,
                operation="audio",
                result="error" if error else "ok",
                error_code=getattr(error, "code", "none" if not error else "playback_failed"),
                loop=self.loop_mode,
            )
        self.audio_source = None
        self.state = State.IDLE
        if not error and self.loop_mode == "song":
            entry.enqueued_at = time.monotonic()
            entry.received_at = None
            self.pending.insert(0, entry)
        elif not error and self.loop_mode == "queue":
            entry.enqueued_at = time.monotonic()
            entry.received_at = None
            self.pending.append(entry)
        self.start_playing()

    def stop_current(self):
        self.playback_blocked = False
        self.ticket += 1
        if self.driver and not self.driver.done() and not self.driver.cancelling():
            self.driver.cancel()
        self.driver = None
        if self.voice_client:
            self.voice_client.stop()  # Also stops paused audio.
        if self.audio_source:
            self.audio_source.cleanup()  # Unblock a stalled Discord audio reader too.
            self.audio_source = None
        self.current = None
        self.state = State.IDLE

    def invalidate(self, *, clear):
        self.generation += 1
        for request in self.requests:
            if not request.cancelling():
                request.cancel()
        self.stop_current()
        if clear:
            self.pending.clear()

    async def clear(self):
        count, requests = len(self.queue), len(self.requests)
        tasks = list(self.requests)
        drivers = list(self.drivers)
        self.invalidate(clear=True)
        await asyncio.gather(*tasks, *drivers, return_exceptions=True)
        with log_context(self.guild_label):
            log_event(
                logger,
                "Queue cleared",
                operation="clear",
                removed=count,
                cancelled_requests=requests,
            )

    def voice_disconnected(self, guild):
        # A channel=None event also occurs during discord.py's own reconnect.
        # Its public guild cache retains the same VoiceClient during recovery,
        # and removes it when a terminal disconnect has completed.
        if self.voice_client is None or (self.voice_recovery and not self.voice_recovery.done()):
            return
        self.voice_recovery = asyncio.create_task(self._wait_for_voice(guild, self.voice_client))

    async def _wait_for_voice(self, guild, voice):
        try:
            with log_context(self.guild_label):
                log_event(
                    logger,
                    "Voice connection interrupted; waiting for recovery",
                    operation="voice_recovery",
                    pending=len(self.pending),
                )
                async with asyncio.timeout(self.settings.connect_timeout):
                    while self.voice_client is voice:
                        # Let discord.py process the event before checking its
                        # public connection/cache state. No private state hooks.
                        await asyncio.sleep(0.1)
                        if self.voice_client is not voice:
                            return
                        if guild.voice_client is not voice:
                            log_event(
                                logger,
                                "Voice connection ended",
                                operation="voice_recovery",
                                result="disconnected",
                            )
                            break
                        member_voice = getattr(getattr(guild, "me", None), "voice", None)
                        if (
                            voice.is_connected()
                            and getattr(member_voice, "channel", None) is not None
                        ):
                            log_event(
                                logger,
                                "Voice connection recovered; queue preserved",
                                operation="voice_recovery",
                                result="ok",
                                pending=len(self.pending),
                            )
                            self.start_playing()
                            return
        except TimeoutError:
            with log_context(self.guild_label):
                log_event(
                    logger,
                    "Voice recovery timed out",
                    level=logging.WARNING,
                    operation="voice_recovery",
                    result="timeout",
                )
        finally:
            if self.voice_recovery is asyncio.current_task():
                self.voice_recovery = None
        await self.safe_disconnect()

    async def safe_disconnect(self):
        async with self.disconnect_lock:
            voice, self.voice_client = self.voice_client, None
            recovery, self.voice_recovery = self.voice_recovery, None
            if recovery and recovery is not asyncio.current_task():
                recovery.cancel()
                await asyncio.gather(recovery, return_exceptions=True)
            self.loop_mode = DEFAULT_LOOP_MODE
            if voice is None and not self.queue and not self.requests and not self.drivers:
                return
            await self.clear()
            if voice:
                try:
                    await voice.disconnect(force=True)
                    with log_context(self.guild_label):
                        log_event(logger, "Voice disconnected", operation="disconnect", result="ok")
                except (discord.DiscordException, OSError, TimeoutError) as exc:
                    logger.warning(
                        "guild=%s operation=disconnect error_type=%s",
                        self.guild_id,
                        type(exc).__name__,
                    )

    def remove(self, index):
        entries = self.queue
        if not 1 <= index <= len(entries):
            raise MediaError("invalid_index")
        removed = entries.pop(index - 1)
        changed = index == 1
        self.reorder(entries, changed)
        with log_context(self.guild_label, removed.request_id):
            log_event(
                logger,
                "Track removed from queue",
                operation="remove",
                position=index,
                remaining=len(self.queue),
                loop=self.loop_mode,
            )
        return removed

    def skip(self):
        entries = self.queue
        if not entries:
            raise MediaError("queue_empty")
        skipped = entries.pop(0)
        if self.loop_mode == "queue":
            skipped.enqueued_at = time.monotonic()
            skipped.received_at = None
            entries.append(skipped)
        self.reorder(entries, True)
        with log_context(self.guild_label, skipped.request_id):
            log_event(
                logger,
                "Track skipped",
                operation="skip",
                action="rotate" if self.loop_mode == "queue" else "discard",
                loop=self.loop_mode,
            )
        return skipped

    def reorder(self, entries, change_current):
        if change_current:
            self.stop_current()
            self.pending = entries
            self.start_playing()
        else:
            self.pending = entries[1:] if self.current else entries

    def jump(self, index):
        entries = self.queue
        if not 2 <= index <= len(entries):
            raise MediaError("invalid_index")
        entries = entries[index - 1 :] + entries[: index - 1]
        self.reorder(entries, True)
        with log_context(self.guild_label):
            log_event(
                logger,
                "Jumped to queue position",
                operation="jump",
                position=index,
                remaining=len(entries),
            )
        return entries[0]

    def move(self, source, destination):
        entries = self.queue
        if not 1 <= source <= len(entries) or not 1 <= destination <= len(entries):
            raise MediaError("invalid_index")
        if source == destination:
            raise MediaError("same_position")
        entry = entries.pop(source - 1)
        entries.insert(destination - 1, entry)
        self.reorder(entries, source == 1 or destination == 1)
        with log_context(self.guild_label):
            log_event(
                logger,
                "Track position changed",
                operation="move",
                from_position=source,
                to_position=destination,
                switches_audio=source == 1 or destination == 1,
            )
        return entry

    def shuffle(self):
        if len(self.pending) < 2:
            raise MediaError("need_more_songs")
        random.shuffle(self.pending)
        with log_context(self.guild_label):
            log_event(
                logger,
                "Pending tracks shuffled",
                operation="shuffle",
                pending=len(self.pending),
                state=self.state.value,
                loop=self.loop_mode,
            )

    @staticmethod
    def create_error_embed(key, *args):
        return discord.Embed(
            description=MESSAGES.get(key, MESSAGES["extraction_failed"]).format(*args),
            color=discord.Color.red(),
        )

    @staticmethod
    def create_success_embed(key, *args):
        return discord.Embed(description=MESSAGES[key].format(*args), color=discord.Color.green())

    @staticmethod
    def create_info_embed(key, *args):
        return discord.Embed(description=MESSAGES[key].format(*args), color=discord.Color.blue())

    def get_status_embed(self) -> discord.Embed:
        """Generate status embed"""
        embed = discord.Embed(title=MESSAGES["status_title"], color=discord.Color.blue())

        # Connection status
        if self.voice_client and self.voice_client.is_connected():
            embed.add_field(
                name=MESSAGES["status_connection"],
                value=MESSAGES["status_connected"].format(self.voice_client.channel.name),
                inline=False,
            )
        else:
            embed.add_field(
                name=MESSAGES["status_connection"],
                value=MESSAGES["status_disconnected"],
                inline=False,
            )

        # Queue status
        if self.queue:
            current_title = self.queue[0].title
            if len(current_title) > 50:
                current_title = current_title[:50] + "..."
            embed.add_field(
                name=MESSAGES["status_queue"],
                value=MESSAGES["status_queue_count"].format(len(self.queue)),
                inline=True,
            )
            embed.add_field(name=MESSAGES["status_current"], value=current_title, inline=True)
        else:
            embed.add_field(
                name=MESSAGES["status_queue"], value=MESSAGES["status_empty"], inline=True
            )
            embed.add_field(
                name=MESSAGES["status_current"], value=MESSAGES["status_none"], inline=True
            )

        # Loop status
        embed.add_field(
            name=MESSAGES["status_loop"],
            value=f"{LOOP_ICONS[self.loop_mode]} {self.loop_mode.title()}",
            inline=True,
        )

        # Playing status
        if self.voice_client and self.voice_client.is_playing():
            status = MESSAGES["status_playing"]
        elif self.voice_client and self.voice_client.is_paused():
            status = MESSAGES["status_paused"]
        elif self.current:
            status = MESSAGES["status_preparing"]
        else:
            status = MESSAGES["status_stopped"]
        embed.add_field(name=MESSAGES["status_status"], value=status, inline=True)

        return embed


class MusicBot:
    def __init__(self, bot, settings):
        self.bot, self.settings = bot, settings
        self.media = Media(settings)
        self.sessions = {}
        self.request_count = 0
        self.audio_capacity = asyncio.Semaphore(settings.audio_workers)
        self.request_ids = itertools.count(1)

    def session(self, guild_id):
        if guild_id not in self.sessions:
            self.sessions[guild_id] = Session(self, guild_id)
        return self.sessions[guild_id]

    async def close(self):
        await asyncio.gather(*(session.safe_disconnect() for session in self.sessions.values()))
