import asyncio
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest
from discord.ext import commands

from config import Settings
from constants import MESSAGES
from main import create_bot
from music_commands import MusicCommands
from player import send
from tests.conftest import entry, started


async def test_skip_acknowledges_title_and_next_track_separately(session, ctx):
    session.pending = [entry("Previous song"), entry("Next song")]
    session.start_playing()
    await started(session)
    cog = MusicCommands(None, session.manager)
    await cog.skip.callback(cog, ctx)
    await started(session)
    reply = ctx.send.call_args.kwargs
    assert reply["embed"].title == MESSAGES["song_skipped"]
    assert reply["embed"].description == "Previous song"
    assert "delete_after" not in reply
    assert session.current.title == "Next song"


@pytest.mark.parametrize("ttl", [None, 60.0])
async def test_playback_and_command_messages_share_optional_duration(session, ctx, ttl):
    settings = replace(session.settings, message_ttl=ttl)
    session.settings = session.manager.settings = settings
    song = entry("Track")
    session.pending = [song]
    session.start_playing()
    driver = session.driver
    await driver
    playback_reply = song.channel.send.call_args.kwargs
    cog = MusicCommands(None, session.manager)
    await cog.loop_command.callback(cog, ctx)
    command_reply = ctx.send.call_args.kwargs
    if ttl is None:
        assert "delete_after" not in playback_reply
        assert "delete_after" not in command_reply
    else:
        assert playback_reply["delete_after"] == command_reply["delete_after"] == ttl


@pytest.mark.parametrize("ttl", [None, 60.0])
async def test_main_error_responses_use_the_same_duration(tmp_path, ttl):
    bot = create_bot(Settings(data_dir=tmp_path, message_ttl=ttl))
    ctx = SimpleNamespace(send=AsyncMock(), prefix="-", guild=None)
    try:
        await bot.on_command_error(ctx, commands.NoPrivateMessage())
        kwargs = ctx.send.call_args.kwargs
        if ttl is None:
            assert "delete_after" not in kwargs
        else:
            assert kwargs["delete_after"] == ttl
    finally:
        await bot.close()


@pytest.mark.parametrize("override", [None, 12])
async def test_explicit_per_message_duration_overrides_default(override):
    channel = SimpleNamespace(send=AsyncMock())
    await send(
        channel,
        settings=Settings(message_ttl=60),
        embed=discord.Embed(description="Example"),
        delete_after=override,
    )
    assert channel.send.call_args.kwargs["delete_after"] == override


async def test_next_song_replaces_only_previous_now_playing(session, ctx):
    first_message = SimpleNamespace(delete=AsyncMock())
    second_message = SimpleNamespace(delete=AsyncMock())
    first, second = entry("A"), entry("B")
    first.channel.send.return_value = first_message
    second.channel.send.return_value = second_message
    session.pending = [first, second]
    session.start_playing()
    await session.driver
    await started(session)
    cog = MusicCommands(None, session.manager)
    await cog.pause.callback(cog, ctx)
    other_message = ctx.send.return_value
    session.voice_client.finish()
    await started(session)
    await session.driver
    first_message.delete.assert_awaited_once()
    second_message.delete.assert_not_awaited()
    other_message.delete.assert_not_awaited()
    assert session.now_playing_message is second_message
    assert session.current is second


async def test_concurrent_np_commands_share_the_automatic_message_slot(session, ctx):
    automatic = SimpleNamespace(delete=AsyncMock())
    replies = [SimpleNamespace(delete=AsyncMock()), SimpleNamespace(delete=AsyncMock())]
    song = entry("A")
    song.channel.send.return_value = automatic
    session.pending = [song]
    session.start_playing()
    await session.driver
    ctx.send.side_effect = replies
    cog = MusicCommands(None, session.manager)
    await asyncio.gather(cog.nowplaying.callback(cog, ctx), cog.nowplaying.callback(cog, ctx))
    automatic.delete.assert_awaited_once()
    replies[0].delete.assert_awaited_once()
    replies[1].delete.assert_not_awaited()
    assert session.now_playing_message is replies[1]
    assert session.voice_client.is_playing()


@pytest.mark.parametrize("error_type", [discord.NotFound, discord.Forbidden])
async def test_previous_message_deletion_failure_does_not_stop_audio(session, error_type):
    response = SimpleNamespace(status=404 if error_type is discord.NotFound else 403, reason="test")
    previous = SimpleNamespace(delete=AsyncMock(side_effect=error_type(response, "test")))
    session.now_playing_message = previous
    song = entry("A")
    session.pending = [song]
    session.start_playing()
    await session.driver
    assert session.voice_client.is_playing()
    assert session.now_playing_message is song.channel.send.return_value


async def test_failed_announcement_does_not_discard_previous_message(session):
    previous = SimpleNamespace(delete=AsyncMock())
    session.now_playing_message = previous
    song = entry("A")
    song.channel.send.side_effect = discord.Forbidden(
        SimpleNamespace(status=403, reason="test"), "test"
    )
    session.pending = [song]
    session.start_playing()
    await session.driver
    previous.delete.assert_not_awaited()
    assert session.now_playing_message is previous
    assert session.voice_client.is_playing()


async def test_stale_announcement_is_removed_if_track_changes_during_send(session):
    first, second = entry("A"), entry("B")
    message = SimpleNamespace(delete=AsyncMock())

    async def send_after_change(**kwargs):
        session.current = second
        session.ticket += 1
        return message

    first.channel.send.side_effect = send_after_change
    session.current = first
    await session.show_now_playing(first.channel, first, session.ticket)
    message.delete.assert_awaited_once()
    assert session.now_playing_message is None


async def test_now_playing_is_independent_per_server(session):
    other = session.manager.session(2)
    first, second = entry("A"), entry("B")
    session.current, other.current = first, second
    await session.show_now_playing(first.channel, first, session.ticket)
    await other.show_now_playing(second.channel, second, other.ticket)
    assert session.now_playing_message is first.channel.send.return_value
    assert other.now_playing_message is second.channel.send.return_value
    first.channel.send.return_value.delete.assert_not_awaited()
    second.channel.send.return_value.delete.assert_not_awaited()
