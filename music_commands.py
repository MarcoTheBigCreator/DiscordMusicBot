"""
Music Bot Commands
All command definitions for the Discord Music Bot
"""

import random

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

from music_bot import MusicBot
from constants import MESSAGES, LOOP_ICONS, LOOP_ICONS


class MusicCommands(commands.Cog):
    """Music commands cog"""

    def __init__(self, bot: commands.Bot, music_bot: MusicBot):
        self.bot = bot
        self.music_bot = music_bot

    @commands.command(name='play', aliases=['p', 'PLAY', 'Play', 'P'])
    async def play(self, ctx, *args):
        query = " ".join(args)  # Fixed: add space between words

        if not query:
            embed = self.music_bot.create_error_embed("no_query")
            await ctx.send(embed=embed, delete_after=15)
            return

        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        # Connect to voice channel
        if not await self.music_bot.connect_to_voice(ctx):
            embed = self.music_bot.create_error_embed("connection_failed")
            await ctx.send(embed=embed, delete_after=15)
            return

        # Send loading message for potential playlists
        loading_msg = None
        if query.startswith(('http://', 'https://', 'www.')) and ('playlist' in query or 'list=' in query):
            embed = self.music_bot.create_info_embed("playlist_loading")
            loading_msg = await ctx.send(embed=embed)

        # Search for song/playlist
        result = self.music_bot.search_youtube(query)
        if not result:
            if loading_msg:
                await loading_msg.delete()
            embed = self.music_bot.create_error_embed("song_not_found")
            await ctx.send(embed=embed, delete_after=15)
            return

        # Handle playlist
        if result.get('is_playlist', False):
            if loading_msg:
                await loading_msg.delete()

            entries = result['entries']
            playlist_title = result['playlist_title']

            # Add all songs to queue
            added_count = 0
            for entry in entries:
                if entry:  # Skip None entries
                    song_entry = [entry, ctx.author.voice.channel,
                                  ctx.channel, ctx.author]
                    self.music_bot.queue.append(song_entry)
                    added_count += 1

            # Send detailed confirmation with preview
            if added_count > 0:
                embed = self.music_bot.create_success_embed(
                    "playlist_added", added_count)
                embed.add_field(name=MESSAGES["playlist_title"].format(playlist_title),
                                value=f"📋 **{added_count}** songs added to queue", inline=False)
                embed.add_field(name=MESSAGES["by_field"],
                                value=ctx.author.mention, inline=False)

                # Add first few songs preview
                preview_songs = []
                for i, entry in enumerate(entries[:3]):  # Show first 3
                    if entry:
                        preview_songs.append(f"{i+1}. {entry['title']}")

                if preview_songs:
                    embed.add_field(
                        name="🎵 Preview",
                        value="\n".join(
                            preview_songs) + (f"\n... and {added_count - 3} more" if added_count > 3 else ""),
                        inline=False
                    )

                await ctx.send(embed=embed)

                # Start playing if not already playing
                if not self.music_bot.is_playing:
                    await self.music_bot.start_playing()
            else:
                embed = self.music_bot.create_error_embed("song_not_found")
                await ctx.send(embed=embed, delete_after=15)
        else:
            if loading_msg:
                await loading_msg.delete()

            song_entry = [result, ctx.author.voice.channel,
                          ctx.channel, ctx.author]
            self.music_bot.queue.append(song_entry)

            if self.music_bot.is_playing:
                embed = self.music_bot.create_success_embed("queued")
                embed.add_field(name=MESSAGES["song_field"],
                                value=result['title'], inline=False)
                embed.add_field(name=MESSAGES["by_field"],
                                value=ctx.author.mention, inline=False)
                await ctx.send(embed=embed)
            else:
                await self.music_bot.start_playing()

    @commands.command(name='queue', aliases=['q', 'QUEUE', 'Queue', 'Q'])
    async def queue(self, ctx, page: int = 1):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        from music_bot import QueuePaginator

        if page < 1:
            page = 1

        paginator = QueuePaginator(self.music_bot, page)
        embed = paginator.get_queue_embed()

        await ctx.send(embed=embed, view=paginator)

    @commands.command(name='skip', aliases=['s', 'SKIP', 'Skip', 'S'])
    async def skip(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.queue:
            embed = self.music_bot.create_error_embed("queue_empty")
            await ctx.send(embed=embed, delete_after=15)
            return

        if self.music_bot.voice_client and self.music_bot.voice_client.is_playing():
            current_song = self.music_bot.queue[0][0]['title']
            self.music_bot.voice_client.stop()
            embed = self.music_bot.create_success_embed(
                "song_skipped")
            embed.description = current_song
            await ctx.send(embed=embed, delete_after=120)

    @commands.command(name='pause', aliases=['pa', 'Pause', 'PAUSE'])
    async def pause(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.voice_client:
            embed = self.music_bot.create_error_embed("bot_not_connected")
            await ctx.send(embed=embed, delete_after=15)
            return

        if self.music_bot.voice_client.is_playing():
            self.music_bot.voice_client.pause()
            embed = self.music_bot.create_info_embed("paused")
            await ctx.send(embed=embed)
        else:
            embed = self.music_bot.create_error_embed("nothing_to_pause")
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(name='resume', aliases=['unpause', 're', 'un', 'Resume', 'Unpause', 'RESUME', 'UNPAUSE', 'RE'])
    async def resume(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.voice_client:
            embed = self.music_bot.create_error_embed("bot_not_connected")
            await ctx.send(embed=embed, delete_after=15)
            return

        if self.music_bot.voice_client.is_paused():
            self.music_bot.voice_client.resume()
            embed = self.music_bot.create_info_embed("resumed")
            await ctx.send(embed=embed, delete_after=30)
        else:
            embed = self.music_bot.create_error_embed("nothing_to_resume")
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(name='nowplaying', aliases=['np', 'Nowplaying', 'NP', 'NOWPLAYING'])
    async def nowplaying(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.queue:
            embed = self.music_bot.create_error_embed("nothing_playing")
            await ctx.send(embed=embed, delete_after=15)
            return

        if not (self.music_bot.voice_client and self.music_bot.voice_client.is_playing()):
            embed = self.music_bot.create_error_embed("nothing_playing")
            await ctx.send(embed=embed, delete_after=15)
            return

        current_song = self.music_bot.queue[0][0]['title']
        embed = self.music_bot.create_info_embed("now_playing")
        embed.description = current_song
        await ctx.send(embed=embed, delete_after=120)

    @commands.command(name='loop', aliases=['l', 'LOOP', 'Loop'])
    async def loop_command(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        # Cycle through loop modes
        if self.music_bot.loop_mode == "off":
            self.music_bot.loop_mode = "song"
            embed = self.music_bot.create_info_embed("loop_song")
        elif self.music_bot.loop_mode == "song":
            self.music_bot.loop_mode = "queue"
            embed = self.music_bot.create_info_embed("loop_queue")
        else:  # queue
            self.music_bot.loop_mode = "off"
            embed = self.music_bot.create_info_embed("loop_off")

        await ctx.send(embed=embed, delete_after=60)

    @commands.command(name='clear', aliases=['c', 'Clear', 'CLEAR', 'C'])
    async def clear_queue(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.queue:
            embed = self.music_bot.create_error_embed("queue_already_empty")
            await ctx.send(embed=embed, delete_after=15)
            return

        queue_length = len(self.music_bot.queue)

        if self.music_bot.voice_client and self.music_bot.voice_client.is_playing():
            self.music_bot.voice_client.stop()

        self.music_bot.reset_state()

        embed = self.music_bot.create_success_embed(
            "queue_cleared", queue_length)
        await ctx.send(embed=embed, delete_after=60)

    @commands.command(name='leave', aliases=['LEAVE', 'Leave'])
    async def leave(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.voice_client:
            embed = self.music_bot.create_error_embed("bot_not_connected")
            await ctx.send(embed=embed, delete_after=15)
            return

        await self.music_bot.voice_client.disconnect()
        self.music_bot.reset_state()

        embed = self.music_bot.create_info_embed("disconnected")
        await ctx.send(embed=embed)

    @commands.command(name='status', aliases=['info', 'Status', 'STATUS', 'INFO'])
    async def status_command(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        embed = self.music_bot.get_status_embed()
        await ctx.send(embed=embed, delete_after=120)

    @commands.command(name='shuffle', aliases=['sh', 'Shuffle', 'SHUFFLE', 'SH'])
    async def shuffle_queue(self, ctx):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if len(self.music_bot.queue) <= 1:
            embed = self.music_bot.create_error_embed(
                "need_more_songs", "shuffle")
            await ctx.send(embed=embed, delete_after=15)
            return

        current_song = self.music_bot.queue[0]
        remaining_songs = self.music_bot.queue[1:]

        random.shuffle(remaining_songs)
        self.music_bot.queue = [current_song] + remaining_songs

        embed = self.music_bot.create_success_embed(
            "queue_shuffled", len(remaining_songs))
        await ctx.send(embed=embed)

    @commands.command(name='remove', aliases=['r', 'Remove', 'REMOVE', 'R'])
    async def remove(self, ctx, index: int):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.queue:
            embed = self.music_bot.create_error_embed("queue_empty")
            await ctx.send(embed=embed, delete_after=15)
            return

        if index < 1 or index > len(self.music_bot.queue):
            embed = self.music_bot.create_error_embed("invalid_index")
            await ctx.send(embed=embed, delete_after=15)
            return

        if index == 1:
            # Removing current song
            current_song = self.music_bot.queue[0][0]['title']
            if self.music_bot.voice_client and self.music_bot.voice_client.is_playing():
                self.music_bot.voice_client.stop()

            embed = self.music_bot.create_success_embed(
                "song_removed")
            embed.description = current_song
            if len(self.music_bot.queue) > 1:
                next_song = self.music_bot.queue[1][0]['title']
                embed.add_field(
                    name=MESSAGES["next_up"], value=next_song, inline=False)
            await ctx.send(embed=embed, delete_after=120)
        else:
            removed_song = self.music_bot.queue[index - 1][0]['title']
            self.music_bot.queue.pop(index - 1)
            embed = self.music_bot.create_success_embed(
                "song_removed_format", removed_song)
            await ctx.send(embed=embed)

    @commands.command(name='jump', aliases=['j', 'Jump', 'JUMP', 'J'])
    async def jump(self, ctx, index: int):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if not self.music_bot.queue:
            embed = self.music_bot.create_error_embed("queue_empty")
            await ctx.send(embed=embed, delete_after=15)
            return

        if index < 2 or index > len(self.music_bot.queue):
            embed = self.music_bot.create_error_embed("invalid_index")
            await ctx.send(embed=embed, delete_after=15)
            return

        # Songs to be moved to the end of the queue (before the target song)
        songs_to_move = self.music_bot.queue[:index-1]

        # Remaining queue starts from the requested song (using index-2 like original)
        self.music_bot.queue = self.music_bot.queue[index-2:]

        # Append the moved songs to the end of the queue
        self.music_bot.queue.extend(songs_to_move)

        # Stop current song to jump
        if self.music_bot.voice_client and self.music_bot.voice_client.is_playing():
            self.music_bot.is_playing = False  # Reset state before stopping
            self.music_bot.voice_client.stop()

        jumped_song = self.music_bot.queue[1][0]['title']
        embed = self.music_bot.create_success_embed(
            "jumped_to", jumped_song)
        await ctx.send(embed=embed)

    @commands.command(name='move', aliases=['mv', 'Move', 'MOVE', 'MV'])
    async def move_song(self, ctx, from_index: int, to_index: int):
        if not self.music_bot.is_user_in_voice(ctx):
            await self.music_bot.send_voice_error(ctx)
            return

        if len(self.music_bot.queue) <= 1:
            embed = self.music_bot.create_error_embed(
                "need_more_songs", "move")
            await ctx.send(embed=embed, delete_after=15)
            return

        queue_len = len(self.music_bot.queue)
        if (from_index < 1 or from_index > queue_len or
                to_index < 1 or to_index > queue_len):
            embed = self.music_bot.create_error_embed("invalid_index")
            await ctx.send(embed=embed, delete_after=15)
            return

        if from_index == to_index:
            embed = self.music_bot.create_error_embed("same_position")
            await ctx.send(embed=embed, delete_after=15)
            return

        # Move song
        song_to_move = self.music_bot.queue.pop(from_index - 1)
        self.music_bot.queue.insert(to_index - 1, song_to_move)

        song_title = song_to_move[0]['title']
        embed = self.music_bot.create_success_embed(
            "song_moved", song_title, from_index, to_index)
        await ctx.send(embed=embed, delete_after=60)

    @commands.command(name='help', aliases=['h', 'Help', 'HELP', 'H'])
    async def help_command(self, ctx):
        """Custom help command with modern UI"""
        from music_bot import HelpPaginator

        help_paginator = HelpPaginator(self.bot)
        embed = help_paginator.get_help_embed()

        await ctx.send(embed=embed, view=help_paginator)


async def setup(bot: commands.Bot, music_bot: MusicBot):
    """Setup function for the cog"""
    await bot.add_cog(MusicCommands(bot, music_bot))
