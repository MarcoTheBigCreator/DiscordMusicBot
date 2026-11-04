import asyncio
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import discord
import pytest

import player
from media import MediaError
from models import State
from music_commands import MusicCommands
from tests.conftest import Voice, entry, started


def events(title):
    return [
        {"type": "header", "playlist": False, "title": title},
        {
            "type": "track",
            "title": title,
            "source": "temporary:" + title,
            "original_url": "https://youtu.be/" + title,
        },
        {"type": "done", "failed": 0, "limited": False},
    ]


@pytest.mark.parametrize("mode,expected", [("off", "B"), ("song", "A"), ("queue", "B")])
async def test_natural_completion_modes(session, mode, expected):
    session.loop_mode = mode
    session.media.refresh = AsyncMock()
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await started(session)
    session.voice_client.finish()
    await started(session)
    assert session.current.title == expected
    if mode == "queue":
        assert [e.title for e in session.pending] == ["A"]


@pytest.mark.parametrize("paused", [False, True])
async def test_skip_overrides_song_loop_and_stale_callback(session, paused):
    session.pending = [entry("A"), entry("B")]
    session.loop_mode = "song"
    session.start_playing()
    await started(session)
    previous = session.voice_client.after
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    session.remove(1)
    await started(session)
    previous(None)
    await asyncio.sleep(0)  # Drain call_soon_threadsafe; no wall-clock timing.
    assert session.current.title == "B"
    assert not session.pending


@pytest.mark.parametrize("operation", ["jump", "move", "shuffle", "remove"])
async def test_queue_operations_conserve_identity(session, operation):
    session.pending = [entry(name) for name in "ABCDE"]
    session.start_playing()
    await started(session)
    before = {id(e) for e in session.queue}
    if operation == "jump":
        session.jump(4)
        await started(session)
        assert [e.title for e in session.queue] == list("DEABC")
    elif operation == "move":
        session.move(1, 3)
        await started(session)
        assert [e.title for e in session.queue] == list("BCADE")
    elif operation == "shuffle":
        session.shuffle()
        assert session.current.title == "A"
    else:
        removed = session.remove(3)
        before.remove(id(removed))
    assert {id(e) for e in session.queue} == before
    assert len(session.queue) == len(before)


async def test_audio_start_failure_does_not_loop_or_block_next(session, monkeypatch):
    async def audio(track, executable):
        if track.title == "A":
            raise MediaError("audio_forbidden")
        return SimpleNamespace(title=track.title, cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    session.loop_mode = "song"
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await started(session)
    assert session.current.title == "B"


async def test_runtime_audio_error_advances_without_repeat(session):
    session.loop_mode = "song"
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await started(session)
    session.voice_client.finish(RuntimeError("do not log this URL"))
    await started(session)
    assert session.current.title == "B"


async def test_notification_failure_keeps_audio(session):
    response = SimpleNamespace(status=403, reason="Forbidden")
    channel = SimpleNamespace(send=AsyncMock(side_effect=discord.Forbidden(response, "no")))
    session.pending = [entry("A", channel)]
    session.start_playing()
    driver = session.driver
    await driver
    assert session.state == State.PLAYING
    assert session.voice_client.is_playing()


async def test_initial_stream_is_used_once_without_second_extraction(session):
    session.media.refresh = AsyncMock(side_effect=AssertionError("second extraction"))
    session.pending = [entry("A")]
    session.start_playing()
    await started(session)
    assert session.current.track.source == "stream:A"
    session.media.refresh.assert_not_awaited()


@pytest.mark.parametrize("now", [0.0, 10.0, 121.0, 86400.0])
async def test_old_stream_is_refreshed_by_original_url(session, monkeypatch, now):
    # The origin of the monotonic clock is unspecified, including on fresh CI VMs.
    monkeypatch.setattr(player, "time", SimpleNamespace(monotonic=lambda: now))
    item = entry("A")
    item.track.resolved_at = now - session.settings.stream_max_age - 1
    item.enqueued_at = now
    session.media.refresh = AsyncMock()
    session.pending = [item]
    session.start_playing()
    await started(session)
    session.media.refresh.assert_awaited_once_with(item.track, 1)


@pytest.mark.parametrize("mode", ["song", "queue"])
@pytest.mark.parametrize("now", [0.0, 10.0])
async def test_natural_repeat_refreshes_even_near_clock_origin(session, monkeypatch, mode, now):
    monkeypatch.setattr(player, "time", SimpleNamespace(monotonic=lambda: now))
    item = entry("A")
    item.track.resolved_at = now
    item.enqueued_at = now
    session.media.refresh = AsyncMock()
    session.loop_mode = mode
    session.pending = [item]
    session.start_playing()
    await started(session)
    session.media.refresh.assert_not_awaited()
    session.voice_client.finish()
    await started(session)
    assert session.queue == [item]
    session.media.refresh.assert_awaited_once_with(item.track, session.guild_id)


async def test_clear_invalidates_extraction_and_next_request_works(session, ctx):
    preparing, release = asyncio.Event(), asyncio.Event()

    async def extract(query, guild_id):
        if query == "A":
            preparing.set()
            await release.wait()
        for event in events(query):
            yield event

    session.media.extract = extract
    first = session.reserve(ctx, "A")
    await preparing.wait()
    await session.clear()
    release.set()
    assert first.cancelled()
    assert not session.queue
    await session.reserve(ctx, "B")
    await started(session)
    assert session.current.title == "B"


@pytest.mark.parametrize("code", ["unavailable", "cookies_invalid", "cookies_expired", "timeout"])
async def test_failed_extraction_releases_fifo_position(session, ctx, code):
    async def extract(query, guild_id):
        if query == "A":
            raise MediaError(code)
        for event in events(query):
            yield event

    session.media.extract = extract
    await asyncio.gather(session.reserve(ctx, "A"), session.reserve(ctx, "B"))
    await started(session)
    assert session.current.title == "B"
    assert session.manager.request_count == 0


async def test_fifo_and_controls_while_preparing(session, ctx):
    preparing, release = asyncio.Event(), asyncio.Event()
    order = []

    async def extract(query, guild_id):
        order.append(query)
        if query == "A":
            preparing.set()
            await release.wait()
        for event in events(query):
            yield event

    session.media.extract = extract
    a = session.reserve(ctx, "A")
    await preparing.wait()
    b = session.reserve(ctx, "B")
    cog = MusicCommands(None, session.manager)
    await cog.loop_command.callback(cog, ctx)
    assert session.loop_mode == "song"
    release.set()
    await asyncio.gather(a, b)
    await started(session)
    assert order == ["A", "B"]
    assert [e.title for e in session.queue] == ["A", "B"]


async def test_capacity_admission_and_release(session, ctx):
    preparing = asyncio.Event()

    async def extract(query, guild_id):
        preparing.set()
        await asyncio.Event().wait()
        yield

    session.media.extract = extract
    tasks = [session.reserve(ctx, str(i)) for i in range(3)]
    with pytest.raises(MediaError, match="busy"):
        session.reserve(ctx, "fourth")
    await preparing.wait()
    assert session.manager.request_count == 3
    await session.clear()
    assert all(task.cancelled() for task in tasks)
    assert session.manager.request_count == 0


async def test_partial_playlist_starts_before_last_entry(session, ctx):
    first, release = asyncio.Event(), asyncio.Event()

    async def extract(query, guild_id):
        yield {"type": "header", "playlist": True, "title": "Playlist"}
        yield events("A")[1]
        first.set()
        await release.wait()
        yield events("B")[1]
        yield {"type": "done", "failed": 1, "limited": False}

    session.media.extract = extract
    request = session.reserve(ctx, "playlist")
    await first.wait()
    await started(session)
    assert not request.done()
    release.set()
    await request
    assert [e.title for e in session.queue] == ["A", "B"]
    embed = ctx.send.call_args.kwargs["embed"]
    assert any("Loaded 2 of 3" in field.value for field in embed.fields)


async def test_pause_resume_during_preparation(session, ctx, monkeypatch):
    preparing, release = asyncio.Event(), asyncio.Event()

    async def audio(track, executable):
        preparing.set()
        await release.wait()
        return SimpleNamespace(cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    session.pending = [entry("A")]
    session.start_playing()
    await preparing.wait()
    cog = MusicCommands(None, session.manager)
    await cog.pause.callback(cog, ctx)
    assert session.state == State.PAUSED
    release.set()
    await session.driver
    assert session.voice_client.is_paused()
    await cog.resume.callback(cog, ctx)
    assert session.state == State.PLAYING


async def test_single_connection_under_concurrent_calls(session, ctx):
    session.settings = replace(session.settings, connect_timeout=17)
    session.voice_client = None
    connected = Voice()
    ctx.author.voice.channel.connect = AsyncMock(return_value=connected)
    await asyncio.gather(session.connect(ctx), session.connect(ctx))
    ctx.author.voice.channel.connect.assert_awaited_once()
    assert ctx.author.voice.channel.connect.call_args.kwargs == {"timeout": 17}
    assert session.voice_client is connected


async def test_channel_guard_and_dm(session, ctx):
    cog = MusicCommands(None, session.manager)
    ctx.author.voice.channel.id = 999
    with pytest.raises(MediaError, match="different_channel"):
        await cog.cog_check(ctx)
    ctx.guild = None
    with pytest.raises(Exception, match="private messages"):
        await cog.cog_check(ctx)


async def test_other_guild_prepares_while_one_waits(session, ctx):
    entered, release = asyncio.Event(), asyncio.Event()

    async def extract(query, guild_id):
        if guild_id == 1:
            entered.set()
            await release.wait()
        for event in events(query):
            yield event

    session.media.extract = extract
    other = session.manager.session(2)
    other.voice_client = Voice()
    other_ctx = SimpleNamespace(**vars(ctx))
    other_ctx.guild = SimpleNamespace(id=2, voice_client=None)
    waiting = session.reserve(ctx, "A")
    await entered.wait()
    await other.reserve(other_ctx, "B")
    await started(other)
    assert other.current.title == "B"
    await session.clear()
    assert waiting.cancelled()


async def test_reconnect_after_disconnect(session, ctx):
    await session.safe_disconnect()
    voice = Voice()
    ctx.author.voice.channel.connect = AsyncMock(return_value=voice)

    async def extract(query, guild_id):
        for event in events(query):
            yield event

    session.media.extract = extract
    await session.reserve(ctx, "B")
    await started(session)
    assert session.current.title == "B"
    assert session.voice_client is voice


async def test_clear_during_connection_cannot_resurrect_session(session, ctx):
    entered = asyncio.Event()

    async def connect(**kwargs):
        entered.set()
        await asyncio.Event().wait()

    session.voice_client = None
    ctx.author.voice.channel.connect = connect
    request = session.reserve(ctx, "A")
    await entered.wait()
    await session.clear()
    assert request.cancelled()
    assert session.voice_client is None


async def test_song_search_uses_typing_without_new_chat_message(session, ctx):
    session.reserve = Mock()
    ctx.typing = AsyncMock()
    cog = MusicCommands(None, session.manager)
    await cog.play.callback(cog, ctx, query="black papermoon")
    session.reserve.assert_called_once_with(ctx, "black papermoon")
    ctx.typing.assert_awaited_once()
    ctx.send.assert_not_awaited()


async def test_playlist_restores_original_loading_message_and_removes_it(session, ctx):
    prepared = asyncio.get_running_loop().create_future()
    prepared.set_result(None)
    session.reserve = Mock(return_value=prepared)
    message = SimpleNamespace(delete=AsyncMock())
    ctx.send = AsyncMock(return_value=message)
    cog = MusicCommands(None, session.manager)
    await cog.play.callback(cog, ctx, query="https://youtube.com/playlist?list=example")
    assert ctx.send.call_args.kwargs["embed"].description == "🎵 Loading playlist..."
    message.delete.assert_awaited_once()


async def test_real_reader_thread_callback_transitions_on_loop(session):
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await started(session)
    await asyncio.to_thread(session.voice_client.finish)
    await started(session)
    assert session.current.title == "B"


async def test_callback_from_before_clear_cannot_remove_new_song(session):
    session.pending = [entry("A")]
    session.start_playing()
    await started(session)
    previous = session.voice_client.after
    await session.clear()
    session.pending = [entry("B")]
    session.start_playing()
    await started(session)
    previous(None)
    await asyncio.sleep(0)
    assert session.current.title == "B"


async def test_final_song_failure_returns_idle_and_accepts_new_song(session, monkeypatch):
    async def audio(track, executable):
        if track.title == "A":
            raise MediaError("playback_failed")
        return SimpleNamespace(cleanup=lambda: None)

    monkeypatch.setattr(player, "open_audio", audio)
    session.loop_mode = "song"
    session.pending = [entry("A")]
    session.start_playing()
    await session.driver
    await asyncio.sleep(0)
    assert session.state == State.IDLE and not session.queue
    session.pending = [entry("B")]
    session.start_playing()
    await started(session)
    assert session.current.title == "B"
