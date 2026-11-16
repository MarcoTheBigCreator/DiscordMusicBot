"""Original illustrated help and queue UI, with typed entries and live prefixes."""

import discord
from discord.ext import commands

from constants import (
    COMMAND_CATEGORIES,
    HELP_CATEGORIES,
    LOOP_ICONS,
    MESSAGES,
    QUEUE_SONGS_PER_PAGE,
    VIEW_TIMEOUT,
)


class HelpPaginator(discord.ui.View):
    """Modern help system with categorized commands"""

    def __init__(self, bot: commands.Bot, prefix: str = "-"):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.message = None
        self.bot = bot
        self.prefix = prefix
        self.current_category = "overview"
        self.categories = HELP_CATEGORIES
        self.command_categories = COMMAND_CATEGORIES

    def get_help_embed(self) -> discord.Embed:
        """Generate help embed for current category"""
        category_info = self.categories[self.current_category]

        embed = discord.Embed(
            title=category_info["title"],
            description=category_info["description"],
            color=discord.Color.blue(),
        )

        if self.current_category == "overview":
            # Overview page with all categories
            for cat_key, cat_info in self.categories.items():
                if cat_key != "overview":
                    embed.add_field(
                        name=f"{cat_info['icon']} {cat_info['title']}",
                        value=cat_info["description"],
                        inline=False,
                    )

            embed.add_field(
                name=MESSAGES["help_how_to"],
                value=MESSAGES["help_usage"].replace("`-`", f"`{self.prefix}`"),
                inline=False,
            )
        else:
            # Category-specific commands
            commands = self.command_categories.get(self.current_category, [])

            for cmd_name, alias, description, example in commands:
                if cmd_name:  # Regular command
                    alias_text = f" / `{alias}`" if alias else ""
                    embed.add_field(
                        name=f"`{cmd_name}`{alias_text}",
                        value=description
                        + "\n"
                        + MESSAGES["help_example"].format(self.prefix + example)
                        if example
                        else description,
                        inline=False,
                    )
                else:  # Special formatting (like loop modes)
                    embed.add_field(
                        name="\u200b",  # Invisible character
                        value=description,
                        inline=False,
                    )

        embed.set_footer(text=MESSAGES["help_footer"])
        return fit_embed(embed)

    @discord.ui.button(label=MESSAGES["button_overview"], style=discord.ButtonStyle.green, row=0)
    async def overview_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Overview/Home button"""
        self.current_category = "overview"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_music"], style=discord.ButtonStyle.primary, row=0)
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Music commands button"""
        self.current_category = "music"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_queue"], style=discord.ButtonStyle.primary, row=0)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Queue management button"""
        self.current_category = "queue"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_loop"], style=discord.ButtonStyle.primary, row=0)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Loop & shuffle button"""
        self.current_category = "loop"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_info"], style=discord.ButtonStyle.primary, row=1)
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Information button"""
        self.current_category = "info"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_admin"], style=discord.ButtonStyle.primary, row=1)
    async def admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Admin commands button"""
        self.current_category = "admin"
        embed = self.get_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=MESSAGES["button_close"], style=discord.ButtonStyle.red, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close help view"""
        await interaction.response.edit_message(
            content=MESSAGES["help_closed"], embed=None, view=None
        )
        self.stop()

    async def on_timeout(self):
        """Called when the view times out"""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class QueuePaginator(discord.ui.View):
    """Paginated queue view with navigation buttons"""

    def __init__(self, music_bot, current_page: int = 1):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.message = None
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
        self.current_page = max(1, min(self.current_page, total_pages))

        # Update previous button
        self.prev_button.disabled = self.current_page <= 1

        # Update next button
        self.next_button.disabled = self.current_page >= total_pages

    def get_queue_embed(self) -> discord.Embed:
        """Generate paginated queue embed"""
        total_pages = self.get_total_pages()
        self.current_page = max(1, min(self.current_page, total_pages))
        total_songs = len(self.music_bot.queue)
        self.update_buttons()

        embed = discord.Embed(
            title=MESSAGES["queue_title"].format(self.current_page, total_pages),
            color=discord.Color.blue(),
        )

        if not self.music_bot.queue:
            embed.description = MESSAGES["queue_empty_view"]
            return fit_embed(embed)

        # Add queue info
        embed.description = MESSAGES["queue_count"].format(total_songs)

        # Calculate start and end indices for current page
        start_idx = (self.current_page - 1) * self.songs_per_page
        end_idx = min(start_idx + self.songs_per_page, total_songs)

        # Add songs for current page
        for i in range(start_idx, end_idx):
            item = self.music_bot.queue[i]
            title = item.title
            requester = (
                item.requester.display_name
                if hasattr(item.requester, "display_name")
                else MESSAGES["unknown_requester"]
            )

            # Format song entry
            if (
                i == 0
                and self.music_bot.voice_client
                and (
                    self.music_bot.voice_client.is_playing()
                    or self.music_bot.voice_client.is_paused()
                )
            ):
                field_name = MESSAGES["queue_current"].format(title)
                field_value = MESSAGES["requested_by"].format(requester)
            else:
                field_name = MESSAGES["queue_item"].format(i + 1, title)
                field_value = MESSAGES["requested_by"].format(requester)

            embed.add_field(name=field_name[:256], value=field_value[:1024], inline=False)

        # Add loop mode info
        embed.set_footer(
            text=MESSAGES["queue_footer"].format(
                LOOP_ICONS[self.music_bot.loop_mode], self.music_bot.loop_mode.title()
            )
        )

        return fit_embed(embed)

    @discord.ui.button(label=MESSAGES["button_previous"], style=discord.ButtonStyle.gray)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Previous page button"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()

            embed = self.get_queue_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(MESSAGES["first_page"], ephemeral=True)

    @discord.ui.button(label=MESSAGES["button_next"], style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Next page button"""
        total_pages = self.get_total_pages()
        self.current_page = max(1, min(self.current_page, total_pages))
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_buttons()

            embed = self.get_queue_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(MESSAGES["last_page"], ephemeral=True)

    async def on_timeout(self):
        """Called when the view times out"""
        # Disable all buttons when timeout occurs
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


def fit_embed(embed):
    """Apply Discord field and combined text limits at the UI boundary."""
    data = embed.to_dict()
    budget = 6000

    def clip(text, limit):
        nonlocal budget
        result = str(text)[: min(limit, budget)]
        budget -= len(result)
        return result

    for key, limit in (("title", 256), ("description", 4096)):
        if key in data:
            data[key] = clip(data[key], limit)
    if "footer" in data:
        data["footer"]["text"] = clip(data["footer"].get("text", ""), 2048)
    if "author" in data:
        data["author"]["name"] = clip(data["author"].get("name", ""), 256)
    fields = []
    for field in data.get("fields", [])[:25]:
        if budget < 2:
            break
        name = clip(field["name"] or "\u200b", min(256, budget - 1))
        value = clip(field["value"] or "\u200b", 1024)
        fields.append({**field, "name": name, "value": value})
    data["fields"] = fields
    return discord.Embed.from_dict(data)
