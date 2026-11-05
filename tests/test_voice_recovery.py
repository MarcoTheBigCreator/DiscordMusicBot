import asyncio
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from config import Settings
from main import create_bot
from media import MediaError
from models import State
from tests.conftest import entry, started


def guild_for(session):
    return SimpleNamespace(
        voice_client=session.voice_client,
        me=SimpleNamespace(voice=SimpleNamespace(channel=None)),
    )


@pytest.mark.parametrize("paused", [False, True])
async def test_transient_disconnect_preserves_current_queue_and_loop(session, paused, caplog):
    session.pending = [entry("A"), entry("B")]
    session.loop_mode = "queue"
    session.start_playing()
    await started(session)
    before = session.queue
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    guild = guild_for(session)
    session.voice_client.connected = False
    with caplog.at_level("INFO"):
        session.voice_disconnected(guild)
        recovery = session.voice_recovery
        await asyncio.sleep(0)
        assert session.queue == before
        session.voice_client.disconnect.assert_not_awaited()
        # Discord's public guild cache still references the recovering client.
        guild.me.voice.channel = session.voice_client.channel
        session.voice_client.connected = True
        await recovery
    assert session.queue == before
    assert session.loop_mode == "queue"
    assert session.state == (State.PAUSED if paused else State.PLAYING)
    session.voice_client.disconnect.assert_not_awaited()
    assert "Voice connection recovered; queue preserved" in caplog.text
    assert "Queue cleared" not in caplog.text
    assert session.voice_recovery is None


async def test_terminal_disconnect_cleans_once_even_with_duplicate_events(session, caplog):
    session.pending = [entry("A"), entry("B")]
    voice = session.voice_client
    voice.connected = False
    guild = guild_for(session)
    guild.voice_client = None  # discord.py completed cleanup of the old client.
    with caplog.at_level("INFO"):
        session.voice_disconnected(guild)
        recovery = session.voice_recovery
        session.voice_disconnected(guild)
        assert session.voice_recovery is recovery
        await recovery
        session.voice_disconnected(guild)
        await session.safe_disconnect()
    assert not session.queue
    assert session.voice_client is None
    assert session.voice_recovery is None
    voice.disconnect.assert_awaited_once_with(force=True)
    assert caplog.text.count("Queue cleared") == 1


async def test_recovery_deadline_disconnects_and_cleans(session, caplog):
    session.settings = replace(session.settings, connect_timeout=0.01)
    session.pending = [entry("A")]
    voice = session.voice_client
    voice.connected = False
    with caplog.at_level("INFO"):
        session.voice_disconnected(guild_for(session))
        await session.voice_recovery
    assert not session.queue
    assert session.voice_client is None
    voice.disconnect.assert_awaited_once()
    assert "Voice recovery timed out" in caplog.text


async def test_explicit_leave_cancels_recovery_without_rejoining(session):
    session.pending = [entry("A")]
    voice = session.voice_client
    voice.connected = False
    session.voice_disconnected(guild_for(session))
    recovery = session.voice_recovery
    await asyncio.sleep(0)
    await session.safe_disconnect()
    assert recovery.done()
    assert session.voice_recovery is None
    assert session.voice_client is None
    assert not session.queue
    voice.disconnect.assert_awaited_once()


async def test_new_request_during_recovery_does_not_replace_connection_or_queue(session, ctx):
    song = entry("A")
    session.pending = [song]
    session.voice_client.connected = False
    session.voice_disconnected(guild_for(session))
    with pytest.raises(MediaError, match="voice_reconnecting"):
        await session.connect(ctx)
    assert session.pending == [song]
    ctx.author.voice.channel.connect.assert_not_awaited()


@pytest.mark.parametrize("paused", [False, True])
async def test_audio_ending_during_outage_retains_track_without_loop_rotation(session, paused):
    session.loop_mode = "queue"
    session.pending = [entry("A"), entry("B")]
    session.start_playing()
    await started(session)
    before = session.queue
    if paused:
        session.voice_client.pause()
        session.state = State.PAUSED
    guild = guild_for(session)
    session.voice_client.connected = False
    session.voice_disconnected(guild)
    recovery = session.voice_recovery
    session.voice_client.finish()
    await asyncio.sleep(0)
    assert session.queue == before
    guild.me.voice.channel = session.voice_client.channel
    session.voice_client.connected = True
    await recovery
    if paused:
        assert session.state == State.PAUSED
        assert session.voice_client.starts.empty()
        session.retry_playback()
    await started(session)
    assert session.queue == before
    assert session.current.title == "A"


async def test_idle_recovery_does_not_start_audio(session):
    guild = guild_for(session)
    session.voice_client.connected = False
    session.voice_disconnected(guild)
    recovery = session.voice_recovery
    guild.me.voice.channel = session.voice_client.channel
    session.voice_client.connected = True
    await recovery
    assert session.voice_client.starts.empty()
    session.voice_client.disconnect.assert_not_awaited()


async def test_bot_voice_event_delegates_without_force_disconnect(tmp_path):
    bot = create_bot(Settings(data_dir=tmp_path))
    bot._connection.user = SimpleNamespace(id=99)
    session = SimpleNamespace(voice_disconnected=Mock())
    bot.music.sessions[1] = session
    guild = SimpleNamespace(id=1)
    try:
        await bot.on_voice_state_update(
            SimpleNamespace(id=99, guild=guild), None, SimpleNamespace(channel=None)
        )
        session.voice_disconnected.assert_called_once_with(guild)
        await bot.on_voice_state_update(
            SimpleNamespace(id=100, guild=guild), None, SimpleNamespace(channel=None)
        )
        assert session.voice_disconnected.call_count == 1
    finally:
        bot.music.sessions.clear()
        await bot.close()
