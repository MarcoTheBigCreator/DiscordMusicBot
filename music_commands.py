"""Public commands backed by an independent session per guild."""

import logging

import discord
from discord.ext import commands

from constants import MESSAGES
from logging_setup import event, log_context
from media import MediaError, validate_query
from models import State
from player import send
from views import HelpPaginator, QueuePaginator

logger = logging.getLogger(__name__)


class MusicCommands(commands.Cog):
    def __init__(self, bot, music_bot):
        self.bot, self.music_bot = bot, music_bot

    def session(self, ctx):
        return self.music_bot.session(ctx.guild.id)

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        if ctx.command.name == "help":
            return True
        session = self.session(ctx)
        voice = getattr(getattr(ctx.author, "voice", None), "channel", None)
        if voice is None:
            raise MediaError("not_in_voice")
        if session.active_voice() and voice.id != session.voice_client.channel.id:
            raise MediaError("different_channel")
        return True

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str = ""):
        if not query:
            raise MediaError("no_query")
        validate_query(query)
        session = self.session(ctx)
        request = session.reserve(ctx, query)
        if query.startswith(("http://", "https://", "www.")) and (
            "playlist" in query or "list=" in query
        ):
            loading = await send(ctx, embed=session.create_info_embed("playlist_loading"))
            try:
                await request
            finally:
                if loading:
                    try:
                        await loading.delete()
                    except discord.HTTPException:
                        logger.warning(
                            "guild=%s operation=loading_message error_type=DiscordHTTPError",
                            ctx.guild.id,
                        )
        else:
            try:
                await ctx.typing()
            except discord.HTTPException:
                logger.warning(
                    "guild=%s operation=typing error_type=DiscordHTTPError", ctx.guild.id
                )

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx, page: int = 1):
        view = QueuePaginator(self.session(ctx), page)
        view.message = await send(ctx, embed=view.get_queue_embed(), view=view)

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        session = self.session(ctx)
        if not session.queue:
            raise MediaError("queue_empty")
        removed = session.skip()
        embed = session.create_success_embed("song_skipped")
        embed.description = removed.title
        await send(ctx, embed=embed, delete_after=120)

    @commands.command(name="pause", aliases=["pa"])
    async def pause(self, ctx):
        session = self.session(ctx)
        if not session.current or session.state == State.PAUSED:
            raise MediaError("nothing_to_pause")
        if session.state == State.PLAYING:
            session.voice_client.pause()
        session.state = State.PAUSED
        with log_context(session.guild_label):
            event(logger, "Playback paused", operation="pause", state=session.state.value)
        await send(ctx, embed=session.create_info_embed("paused"))

    @commands.command(name="resume", aliases=["unpause", "re", "un"])
    async def resume(self, ctx):
        session = self.session(ctx)
        if not session.current or session.state != State.PAUSED:
            raise MediaError("nothing_to_resume")
        if session.voice_client and session.voice_client.is_paused():
            session.voice_client.resume()
            session.state = State.PLAYING
        else:
            session.state = State.PREPARING
        with log_context(session.guild_label):
            event(logger, "Playback resumed", operation="resume", state=session.state.value)
        await send(ctx, embed=session.create_info_embed("resumed"), delete_after=30)

    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        session = self.session(ctx)
        if not session.current:
            raise MediaError("nothing_playing")
        embed = session.create_info_embed("now_playing")
        embed.description = session.current.title
        await send(ctx, embed=embed, delete_after=120)

    @commands.command(name="loop", aliases=["l"])
    async def loop_command(self, ctx):
        session = self.session(ctx)
        session.loop_mode = {"off": "song", "song": "queue", "queue": "off"}[session.loop_mode]
        with log_context(session.guild_label):
            event(logger, "Loop mode changed", operation="loop", loop=session.loop_mode)
        await send(
            ctx, embed=session.create_info_embed("loop_" + session.loop_mode), delete_after=60
        )

    @commands.command(name="clear", aliases=["c"])
    async def clear_queue(self, ctx):
        session = self.session(ctx)
        count = len(session.queue)
        await session.clear()
        await send(ctx, embed=session.create_success_embed("queue_cleared", count), delete_after=60)

    @commands.command(name="leave")
    async def leave(self, ctx):
        session = self.session(ctx)
        await session.safe_disconnect()
        await send(ctx, embed=session.create_info_embed("disconnected"))

    @commands.command(name="status", aliases=["info"])
    async def status_command(self, ctx):
        await send(ctx, embed=self.session(ctx).get_status_embed(), delete_after=120)

    @commands.command(name="shuffle", aliases=["sh"])
    async def shuffle_queue(self, ctx):
        session = self.session(ctx)
        if len(session.pending) < 2:
            await send(
                ctx, embed=session.create_error_embed("need_more_songs", "shuffle"), delete_after=15
            )
            return
        session.shuffle()
        embed = session.create_success_embed("queue_shuffled", len(session.pending))
        embed.add_field(
            name=MESSAGES["shuffle_title"], value=MESSAGES["shuffle_pending"], inline=False
        )
        await send(ctx, embed=embed)

    @commands.command(name="remove", aliases=["r"])
    async def remove(self, ctx, index: int):
        session = self.session(ctx)
        removed = session.remove(index)
        if index == 1:
            embed = session.create_success_embed("song_removed")
            embed.description = removed.title
            if session.queue:
                embed.add_field(
                    name=MESSAGES["next_up"], value=session.queue[0].title, inline=False
                )
            await send(ctx, embed=embed, delete_after=120)
        else:
            await send(
                ctx, embed=session.create_success_embed("song_removed_format", removed.title)
            )

    @commands.command(name="jump", aliases=["j"])
    async def jump(self, ctx, index: int):
        session = self.session(ctx)
        target = session.jump(index)
        await send(ctx, embed=session.create_success_embed("jumped_to", target.title))

    @commands.command(name="move", aliases=["mv"])
    async def move_song(self, ctx, from_index: int, to_index: int):
        session = self.session(ctx)
        entry = session.move(from_index, to_index)
        await send(
            ctx,
            embed=session.create_success_embed("song_moved", entry.title, from_index, to_index),
            delete_after=60,
        )

    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx):
        view = HelpPaginator(self.bot, ctx.prefix)
        view.message = await send(ctx, embed=view.get_help_embed(), view=view)


async def setup(bot, music_bot):
    await bot.add_cog(MusicCommands(bot, music_bot))
