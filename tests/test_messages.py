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
