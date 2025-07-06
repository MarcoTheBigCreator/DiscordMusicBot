"""
DISCORD MUSIC BOT CRUMMY Version 3.0 (refactored)
Main MusicBot class with all functionality
"""

import asyncio
from typing import Dict, List, Optional, Tuple

import discord
from discord import ClientException
from discord.ext import commands

from yt_dlp import YoutubeDL
from constants import (
    HELP_CATEGORIES, COMMAND_CATEGORIES, DEFAULT_LOOP_MODE, QUEUE_SONGS_PER_PAGE, VIEW_TIMEOUT,
    LOOP_ICONS, YDL_OPTIONS, FFMPEG_OPTIONS, MESSAGES
)


class HelpPaginator(discord.ui.View):
    """Modern help system with categorized commands"""

    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.bot = bot
        self.current_category = "overview"
        self.categories = HELP_CATEGORIES
        self.command_categories = COMMAND_CATEGORIES

    def get_help_embed(self) -> discord.Embed:
        """Generate help embed for current category"""
        category_info = self.categories[self.current_category]

        embed = discord.Embed(
            title=category_info["title"],
            description=category_info["description"],
            color=discord.Color.blue()
        )

        if self.current_category == "overview":
            # Overview page with all categories
            for cat_key, cat_info in self.categories.items():
                if cat_key != "overview":
                    embed.add_field(
                        name=f"{cat_info['icon']} {cat_info['title']}",
                        value=cat_info["description"],
                        inline=False
                    )

            embed.add_field(
                name="💡 How to use",
                value="• Click the buttons below to navigate between categories\n• Use the prefix `-` before each command\n• Commands are case-insensitive",
                inline=False
            )
        else:
            # Category-specific commands
            commands = self.command_categories.get(self.current_category, [])

            for cmd_name, alias, description, example in commands:
                if cmd_name:  # Regular command
                    alias_text = f" / `{alias}`" if alias else ""
                    embed.add_field(
                        name=f"`{cmd_name}`{alias_text}",
                        value=f"{description}\n*Example:* `-{example}`" if example else description,
                        inline=False
                    )
                else:  # Special formatting (like loop modes)
                    embed.add_field(
                        name="\u200b",  # Invisible character
                        value=description,
                        inline=False
                    )

        embed.set_footer(text=MESSAGES["help_footer"])
        return embed

    @discord.ui.button(label="🏠", style=discord.ButtonStyle.green, row=0)
    async def overview_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Overview/Home button"""
        self.current_category = "overview"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎵", style=discord.ButtonStyle.primary, row=0)
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Music commands button"""
        self.current_category = "music"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📋", style=discord.ButtonStyle.primary, row=0)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Queue management button"""
        self.current_category = "queue"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔄", style=discord.ButtonStyle.primary, row=0)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Loop & shuffle button"""
        self.current_category = "loop"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📊", style=discord.ButtonStyle.primary, row=1)
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Information button"""
        self.current_category = "info"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⚙️", style=discord.ButtonStyle.primary, row=1)
    async def admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Admin commands button"""
        self.current_category = "admin"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close help view"""
        await interaction.response.edit_message(content="Help closed.", embed=None, view=None)
        self.stop()

    async def on_timeout(self):
        """Called when the view times out"""
        for item in self.children:
            item.disabled = True


class QueuePaginator(discord.ui.View):
    """Paginated queue view with navigation buttons"""

    def __init__(self, music_bot, current_page: int = 1):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.music_bot = music_bot
        self.current_page = current_page
        self.songs_per_page = QUEUE_SONGS_PER_PAGE
        self.update_buttons()

    def get_total_pages(self) -> int:
        """Calculate total number of pages"""
        if not self.music_bot.queue:
            return 1
        return (len(self.music_bot.queue) + self.songs_per_page - 1) // self.songs_per_page

    def update_buttons(self):
        """Update button states based on current page"""
        total_pages = self.get_total_pages()

        # Update previous button
        self.prev_button.disabled = self.current_page <= 1

        # Update next button
        self.next_button.disabled = self.current_page >= total_pages

    def get_queue_embed(self) -> discord.Embed:
        """Generate paginated queue embed"""
        total_pages = self.get_total_pages()
        total_songs = len(self.music_bot.queue)

        embed = discord.Embed(
            title=f"📋 Queue - Page {self.current_page}/{total_pages}",
            color=discord.Color.blue()
        )

        if not self.music_bot.queue:
            embed.description = "🎵 Queue is empty"
            return embed

        # Add queue info
        embed.description = f"🎵 {total_songs} song(s) total"

        # Calculate start and end indices for current page
        start_idx = (self.current_page - 1) * self.songs_per_page
        end_idx = min(start_idx + self.songs_per_page, total_songs)

        # Add songs for current page
        for i in range(start_idx, end_idx):
            item = self.music_bot.queue[i]
            title = item[0]['title']
            requester = item[3].display_name if hasattr(
                item[3], 'display_name') else "Unknown"

            # Format song entry
            if i == 0 and self.music_bot.voice_client and self.music_bot.voice_client.is_playing():
                field_name = f"🎵 **Now Playing** - {title}"
                field_value = f"👤 Requested by: {requester}"
            else:
                field_name = f"{i + 1}. {title}"
                field_value = f"👤 Requested by: {requester}"

            embed.add_field(name=field_name, value=field_value, inline=False)

        # Add loop mode info
        embed.set_footer(
            text=f"🔄 Loop: {LOOP_ICONS[self.music_bot.loop_mode]} {self.music_bot.loop_mode.title()}")

        return embed

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Previous page button"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()

            embed = self.get_queue_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Already on the first page!", ephemeral=True)

    @discord.ui.button(label="Next ➡️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Next page button"""
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_buttons()

            embed = self.get_queue_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Already on the last page!", ephemeral=True)

    async def on_timeout(self):
        """Called when the view times out"""
        # Disable all buttons when timeout occurs
        for item in self.children:
            item.disabled = True


class MusicBot:
    """Main class for the Discord Music Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Bot state
        self.is_playing: bool = False
        self.loop_mode: str = DEFAULT_LOOP_MODE
        self.voice_client: Optional[discord.VoiceClient] = None

        # Queue and
        self.queue: List[Tuple] = []

        # YouTube-DL options
        self.ydl_options = YDL_OPTIONS
        self.ffmpeg_options = FFMPEG_OPTIONS

    # Utility methods
    def is_user_in_voice(self, ctx) -> bool:
        """Check if user is in a voice channel"""
        return ctx.author.voice is not None

    async def send_voice_error(self, ctx):
        """Send voice channel error message"""
        embed = discord.Embed(
            description=MESSAGES["not_in_voice"],
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=15)

    def create_error_embed(self, message_key: str, *args) -> discord.Embed:
        """Create standardized error embed"""
        message = MESSAGES[message_key].format(
            *args) if args else MESSAGES[message_key]
        return discord.Embed(description=message, color=discord.Color.red())

    def create_success_embed(self, message_key: str, *args, title: str = None) -> discord.Embed:
        """Create standardized success embed"""
        message = MESSAGES[message_key].format(
            *args) if args else MESSAGES[message_key]
        embed = discord.Embed(description=message, color=discord.Color.green())
        if title:
            embed.title = title
        return embed

    def create_info_embed(self, message_key: str, *args, title: str = None) -> discord.Embed:
        """Create standardized info embed"""
        message = MESSAGES[message_key].format(
            *args) if args else MESSAGES[message_key]
        embed = discord.Embed(description=message, color=discord.Color.blue())
        if title:
            embed.title = title
        return embed

    async def connect_to_voice(self, ctx) -> bool:
        """Connect to user's voice channel"""
        try:
            if self.voice_client is None or not self.voice_client.is_connected():
                self.voice_client = await ctx.author.voice.channel.connect()
            elif self.voice_client.channel != ctx.author.voice.channel:
                await self.voice_client.move_to(ctx.author.voice.channel)
                embed = discord.Embed(
                    description=MESSAGES["moving_channel"],
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed, delete_after=15)
            return True
        except Exception as e:
            print(f"Error connecting to voice: {e}")
            return False

    def search_youtube(self, query: str) -> Optional[Dict]:
        """Search YouTube for a song"""
        try:
            with YoutubeDL(self.ydl_options) as ydl:
                # Check if query is a URL
                if query.startswith(('http://', 'https://', 'www.')):
                    info = ydl.extract_info(query, download=False)
                    return {'source': info['url'], 'title': info['title']}
                else:
                    # Search query
                    info = ydl.extract_info(
                        f"ytsearch:{query}", download=False)
                    if 'entries' in info and len(info['entries']) > 0:
                        entry = info['entries'][0]
                        return {'source': entry['url'], 'title': entry['title']}
                    else:
                        print(f"No results found for: {query}")
                        return None
        except Exception as e:
            print(f"Error in YouTube search: {e}")
            if "unable to extract" in str(e).lower():
                print("YouTube extraction failed - video might be unavailable")
            elif "network" in str(e).lower():
                print("Network error - check internet connection")
            elif "private" in str(e).lower() or "unavailable" in str(e).lower():
                print("Video is private or unavailable")
            return None

    async def send_now_playing(self, song_title: str):
        """Send now playing message"""
        if not self.queue:
            return

        text_channel = self.queue[0][2]
        embed = discord.Embed(
            title="Now Playing",
            description=song_title,
            color=discord.Color.light_gray()
        )
        await text_channel.send(embed=embed, delete_after=120)

    def play_next_song(self):
        """Handle playing the next song based on loop mode"""
        if not self.queue:
            self.is_playing = False
            return

        # Handle loop modes
        if self.loop_mode == "song":
            # Don't remove current song from queue
            pass
        elif self.loop_mode == "queue":
            # Move current song to end
            self.queue.append(self.queue.pop(0))
        else:
            # Normal mode - remove current song
            self.queue.pop(0)

        if self.queue:
            self.is_playing = True
            song_url = self.queue[0][0]['source']
            if self.voice_client and self.voice_client.is_connected():
                try:
                    audio_source = discord.FFmpegPCMAudio(
                        song_url, **self.ffmpeg_options)
                    self.voice_client.play(
                        audio_source, after=lambda e: self.play_next_song())
                    # Schedule now playing message using run_coroutine_threadsafe
                    asyncio.run_coroutine_threadsafe(
                        self.send_now_playing(self.queue[0][0]['title']),
                        self.bot.loop
                    )
                except Exception as e:
                    print(f"Error playing audio: {e}")
                    self.is_playing = False
            else:
                self.is_playing = False
        else:
            self.is_playing = False

    async def start_playing(self):
        """Start playing music from the queue"""
        if not self.queue:
            self.is_playing = False
            return

        self.is_playing = True
        song_url = self.queue[0][0]['source']

        try:
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await self.queue[0][1].connect()
            else:
                await self.voice_client.move_to(self.queue[0][1])

            audio_source = discord.FFmpegPCMAudio(
                song_url, **self.ffmpeg_options)
            self.voice_client.play(
                audio_source, after=lambda e: self.play_next_song())

            # Send now playing message immediately
            await self.send_now_playing(self.queue[0][0]['title'])

        except ClientException as e:
            print(f"Ignoring client exception: {e}")
        except Exception as e:
            print(f"Error starting playback: {e}")
            self.is_playing = False

    def reset_state(self):
        """Reset bot state when leaving"""
        self.is_playing = False
        self.loop_mode = DEFAULT_LOOP_MODE
        self.queue = []
        self.voice_client = None

    def get_status_embed(self) -> discord.Embed:
        """Generate status embed"""
        embed = discord.Embed(title="Bot Status", color=discord.Color.blue())

        # Connection status
        if self.voice_client and self.voice_client.is_connected():
            embed.add_field(
                name="🔗 Connection", value=f"Connected to {self.voice_client.channel.name}", inline=False)
        else:
            embed.add_field(name="🔗 Connection",
                            value="Not connected", inline=False)

        # Queue status
        if self.queue:
            current_title = self.queue[0][0]['title']
            if len(current_title) > 50:
                current_title = current_title[:50] + "..."
            embed.add_field(
                name="📋 Queue", value=f"{len(self.queue)} song(s)", inline=True)
            embed.add_field(name="🎵 Current Song",
                            value=current_title, inline=True)
        else:
            embed.add_field(name="📋 Queue", value="Empty", inline=True)
            embed.add_field(name="🎵 Current Song", value="None", inline=True)

        # Loop status
        embed.add_field(
            name="🔄 Loop Mode", value=f"{LOOP_ICONS[self.loop_mode]} {self.loop_mode.title()}", inline=True)

        # Playing status
        if self.voice_client and self.voice_client.is_playing():
            status = "Playing"
        elif self.voice_client and self.voice_client.is_paused():
            status = "Paused"
        else:
            status = "Stopped"
        embed.add_field(name="⏯️ Status", value=status, inline=True)

        return embed
