import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from logging_setup import ConsoleContext, event, log_context
from models import State
from music_commands import MusicCommands
from tests.conftest import entry, started
from tests.test_player import events


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
@pytest.mark.parametrize("paused", [False, True])
async def test_skip_command_in_all_loop_modes(session, ctx, mode, paused):
    session.loop_mode = mode
    session.pending = [entry(name) for name in "ABC"]
    session.start_playing()
    await started(session)
    previous = session.voice_client.after
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    cog = MusicCommands(None, session.manager)
    await cog.skip.callback(cog, ctx)
    await started(session)
    previous(None)
    await asyncio.sleep(0)
    expected = list("BCA") if mode == "queue" else list("BC")
    assert [item.title for item in session.queue] == expected
    assert session.loop_mode == mode
    assert session.state == State.PLAYING
    # In queue-loop mode, A still exists exactly once after B naturally ends.
    if mode == "queue":
        session.voice_client.finish()
        await started(session)
        assert [item.title for item in session.queue] == list("CAB")


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
@pytest.mark.parametrize("paused", [False, True])
@pytest.mark.parametrize("index", [1, 2])
async def test_remove_from_looping_playlist_never_returns(session, ctx, mode, paused, index):
    session.loop_mode = mode
    session.media.refresh = AsyncMock()
    original = [entry(name) for name in "ABCD"]
    session.pending = original.copy()
    session.start_playing()
    await started(session)
    previous = session.voice_client.after
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    cog = MusicCommands(None, session.manager)
    await cog.remove.callback(cog, ctx, index)
    if index == 1:
        await started(session)
        previous(None)
        await asyncio.sleep(0)
    else:
        assert session.state == (State.PAUSED if paused else State.PLAYING)
        if paused:
            session.voice_client.resume()
            session.state = State.PLAYING
    removed = original[index - 1]
    assert all(item is not removed for item in session.queue)
    # Exercise repeated natural transitions to detect a removed entry resurfacing.
    for _ in range(4 if mode != "off" else 2):
        session.voice_client.finish()
        await started(session)
        assert all(item is not removed for item in session.queue)


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
@pytest.mark.parametrize("paused", [False, True])
async def test_shuffle_preserves_audio_pause_loop_and_entries(
    session, ctx, monkeypatch, mode, paused
):
    session.loop_mode = mode
    session.media.refresh = AsyncMock()
    session.pending = [entry(name) for name in "ABCD"]
    session.start_playing()
    await started(session)
    source, after = session.voice_client.source, session.voice_client.after
    identities = {id(item) for item in session.queue}
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    monkeypatch.setattr("player.random.shuffle", lambda items: items.reverse())
    cog = MusicCommands(None, session.manager)
    await cog.shuffle_queue.callback(cog, ctx)
    assert [item.title for item in session.queue] == list("ADCB")
    assert {id(item) for item in session.queue} == identities
    assert session.voice_client.source is source
    assert session.voice_client.after is after
    assert session.state == (State.PAUSED if paused else State.PLAYING)
    assert session.loop_mode == mode
    assert session.voice_client.starts.empty()
    if paused:
        session.voice_client.resume()
    session.voice_client.finish()
    await started(session)
    expected = "A" if mode == "song" else "D"
    assert session.current.title == expected


@pytest.mark.parametrize("now", [0.0, 10.0, 86400.0])
async def test_skip_only_song_in_queue_loop_restarts_once(session, ctx, monkeypatch, now):
    monkeypatch.setattr("player.time", SimpleNamespace(monotonic=lambda: now))
    session.media.refresh = AsyncMock()
    session.loop_mode = "queue"
    original = entry("A")
    original.track.resolved_at = now
    original.enqueued_at = now
    session.pending = [original]
    session.start_playing()
    await started(session)
    cog = MusicCommands(None, session.manager)
    await cog.skip.callback(cog, ctx)
    await started(session)
    assert session.queue == [original]
    session.media.refresh.assert_not_awaited()


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
@pytest.mark.parametrize("paused", [False, True])
async def test_jump_preserves_entries_loop_and_ignores_previous_callback(
    session, ctx, mode, paused
):
    session.loop_mode = mode
    session.media.refresh = AsyncMock()
    original = [entry(name) for name in "ABCD"]
    session.pending = original.copy()
    session.start_playing()
    await started(session)
    previous = session.voice_client.after
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    cog = MusicCommands(None, session.manager)
    await cog.jump.callback(cog, ctx, 3)
    await started(session)
    previous(None)
    await asyncio.sleep(0)
    assert [item.title for item in session.queue] == list("CDAB")
    assert {id(item) for item in session.queue} == {id(item) for item in original}
    assert session.loop_mode == mode
    assert session.state == State.PLAYING
    session.voice_client.finish()
    await started(session)
    assert session.current.title == ("C" if mode == "song" else "D")
    if mode == "queue":
        assert [item.title for item in session.queue] == list("DABC")


@pytest.mark.parametrize("mode", ["off", "song", "queue"])
@pytest.mark.parametrize("paused", [False, True])
@pytest.mark.parametrize("source,destination", [(1, 3), (4, 2)])
async def test_move_preserves_loop_pause_policy_and_identity(
    session, ctx, mode, paused, source, destination
):
    session.loop_mode = mode
    session.media.refresh = AsyncMock()
    original = [entry(name) for name in "ABCD"]
    session.pending = original.copy()
    session.start_playing()
    await started(session)
    audio, previous = session.voice_client.source, session.voice_client.after
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    cog = MusicCommands(None, session.manager)
    await cog.move_song.callback(cog, ctx, source, destination)
    if source == 1:
        await started(session)
        previous(None)
        await asyncio.sleep(0)
        assert session.state == State.PLAYING
        assert [item.title for item in session.queue] == list("BCAD")
    else:
        assert session.voice_client.source is audio
        assert session.voice_client.after is previous
        assert session.state == (State.PAUSED if paused else State.PLAYING)
        assert [item.title for item in session.queue] == list("ADBC")
        if paused:
            await cog.resume.callback(cog, ctx)
    assert session.loop_mode == mode
    assert {id(item) for item in session.queue} == {id(item) for item in original}
    before = session.current.title
    session.voice_client.finish()
    await started(session)
    assert session.current.title == (before if mode == "song" else "C" if source == 1 else "D")


async def test_request_and_playback_logs_correlate_without_sensitive_data(session, ctx, caplog):
    caplog.set_level(logging.INFO)
    ctx.guild.name = "Test server"

    async def extract(query, guild_id):
        for item in events("private-title-not-for-logs"):
            yield item

    session.media.extract = extract
    await session.reserve(ctx, "sensitive-query-do-not-log")
    await started(session)
    records = [record for record in caplog.records if hasattr(record, "request_id")]
    received = next(record for record in records if record.message.startswith("Request accepted"))
    playing = next(
        record for record in records if record.message.startswith("Discord audio player started")
    )
    assert received.request_id == playing.request_id != "-"
    assert received.guild == playing.guild == "Test server (1)"
    assert "request_to_start_ms=" in playing.message
    assert any("guild_wait_ms=" in record.message for record in records)
    assert any("queue_wait_ms=" in record.message for record in records)
    assert any("FFmpeg produced PCM audio" in record.message for record in records)
    assert "sensitive-query" not in caplog.text
    assert "private-title" not in caplog.text
    assert "temporary:" not in caplog.text


async def test_error_logs_include_safe_code_without_raw_exception(session, ctx, caplog):
    caplog.set_level(logging.INFO)
    from media import MediaError

    async def extract(query, guild_id):
        raise MediaError("format_unavailable")
        yield

    session.media.extract = extract
    await session.reserve(ctx, "not-logged")
    assert "result=error" in caplog.text
    assert "error_code=format_unavailable" in caplog.text
    assert "Request ready" not in caplog.text
    assert "not-logged" not in caplog.text


def test_console_context_supports_library_logs_and_sanitizes_server_names():
    record = logging.LogRecord("library", logging.INFO, "", 0, "Library message", (), None)
    assert ConsoleContext().filter(record)
    assert record.guild == record.request_id == "-"
    record.guild = "server\n\x1b[31m"
    ConsoleContext().filter(record)
    assert "\n" not in record.guild and "\x1b" not in record.guild


async def test_log_context_is_isolated_between_concurrent_requests(caplog):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("request-test")
    ready, release = asyncio.Event(), asyncio.Event()

    async def first():
        with log_context("Guild A", "A"):
            ready.set()
            await release.wait()
            event(logger, "first")

    task = asyncio.create_task(first())
    await ready.wait()
    with log_context("Guild B", "B"):
        event(logger, "second")
    release.set()
    await task
    event(logger, "outside")
    records = {record.message: record for record in caplog.records if record.name == "request-test"}
    assert (records["first"].guild, records["first"].request_id) == ("Guild A", "A")
    assert (records["second"].guild, records["second"].request_id) == ("Guild B", "B")
    assert records["outside"].request_id == "-"
