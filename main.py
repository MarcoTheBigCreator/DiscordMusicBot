"""Crummy v4. Import-safe entry point: uv run --locked python main.py."""

import argparse
import asyncio
import logging
import sys

import discord
from discord.ext import commands

from config import Settings, validate_prefix
from constants import MESSAGES
from logging_setup import configure_logging
from media import MediaError
from music_commands import setup
from player import MusicBot, send
from prefixes import Prefixes

logger = logging.getLogger(__name__)


def create_bot(settings):
    async def reply(ctx, **kwargs):
        return await send(ctx, settings=settings, **kwargs)

    prefixes = Prefixes(settings.data_dir / "prefixes.json", settings.prefix)
    intents = discord.Intents.none()
    intents.guilds = True
    intents.messages = True
    intents.voice_states = True
    intents.message_content = True

    def prefix(bot, message):
        return prefixes.get(message.guild.id if message.guild else None)

    class Crummy(commands.Bot):
        async def setup_hook(self):
            await setup(self, self.music)

        async def close(self):
            await self.music.close()
            await super().close()

    bot = Crummy(
        command_prefix=prefix,
        intents=intents,
        help_command=None,
        case_insensitive=True,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    bot.music = MusicBot(bot, settings)

    @bot.event
    async def on_ready():
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="Music")
        )
        print("Bot is online")
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print("------", flush=True)

    @bot.event
    async def on_voice_state_update(member, before, after):
        if bot.user and member.id == bot.user.id and after.channel is None:
            session = bot.music.sessions.get(member.guild.id)
            if session:
                await session.safe_disconnect()

    @bot.event
    async def on_guild_remove(guild):
        session = bot.music.sessions.pop(guild.id, None)
        if session:
            await session.safe_disconnect()

    @bot.event
    async def on_command_error(ctx, error):
        error = getattr(error, "original", error)
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, MediaError):
            text = MESSAGES.get(error.code, MESSAGES["extraction_failed"])
        elif isinstance(error, commands.NoPrivateMessage):
            text = MESSAGES["guild_only"]
        elif isinstance(error, commands.MissingPermissions):
            text = MESSAGES["missing_permissions"]
        elif isinstance(error, commands.UserInputError):
            text = MESSAGES["invalid_arguments"].format(prefix=ctx.prefix)
        else:
            logger.error(
                "guild=%s operation=command error_type=%s",
                getattr(ctx.guild, "id", None),
                type(error).__name__,
            )
            text = MESSAGES["extraction_failed"]
        await reply(ctx, embed=discord.Embed(description=text, color=discord.Color.red()))

    @bot.command(name="ping")
    async def ping(ctx):
        await reply(
            ctx,
            embed=discord.Embed(
                title=MESSAGES["pong"],
                description=f"{round(bot.latency * 1000)} ms",
                color=discord.Color.red(),
            ),
        )

    @bot.command(name="prefix", aliases=["pre"])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def change_prefix(ctx, new_prefix: str):
        try:
            validate_prefix(new_prefix)
        except ValueError:
            raise commands.BadArgument() from None
        try:
            await prefixes.set(ctx.guild.id, new_prefix)
        except OSError:
            await reply(
                ctx,
                embed=discord.Embed(
                    description=MESSAGES["prefix_failed"], color=discord.Color.red()
                ),
            )
            return
        await reply(
            ctx,
            embed=discord.Embed(
                description=MESSAGES["prefix_changed"].format(new_prefix),
                color=discord.Color.green(),
            ),
        )

    return bot


async def main():
    settings = Settings.load()
    bot = create_bot(settings)
    print("Starting bot...")
    async with bot:
        print("Loading music commands...")
        print("Connecting to Discord...")
        await bot.start(settings.token)


def run():
    parser = argparse.ArgumentParser(description="Crummy Discord music bot")
    parser.add_argument("--version", action="version", version="Crummy 4.0.0")
    parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    configure_logging()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as exc:
        if isinstance(exc, ValueError):
            print(str(exc), file=sys.stderr)
        else:
            logger.error("operation=startup error_type=%s", type(exc).__name__)
        sys.exit(1)


if __name__ == "__main__":
    run()
