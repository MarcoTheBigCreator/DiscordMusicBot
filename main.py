"""
DISCORD MUSIC BOT CRUMMY Version 3.0 (refactored)
Main application file - now with clean architecture
"""

import asyncio
import io
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from music_bot import MusicBot
from music_commands import setup as setup_commands

# Setup encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
PREFIX = os.getenv("DISCORD_BOT_PREFIX")

if not DISCORD_API_TOKEN:
    raise ValueError("DISCORD_API_TOKEN is not set in .env file")
if not PREFIX:
    raise ValueError("DISCORD_BOT_PREFIX is not set in .env file")

# Global state for prefix changes
current_prefix = PREFIX


def get_prefix(bot, message):
    """Dynamic prefix function"""
    return current_prefix


# Bot setup
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=discord.Intents.all(),
    help_command=None  # Disable default help command
)

# Initialize music bot
music_bot = MusicBot(bot)


@bot.event
async def on_ready():
    """Bot ready event"""
    # Set status once when bot starts
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="Music"
        )
    )
    print('Bot is online')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    sys.stdout.flush()


@bot.command(name='ping', aliases=['PING'])
async def ping(ctx):
    """Ping command"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Pong! 🏓",
        description=f'{latency} ms',
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, delete_after=60)


@bot.command(name='prefix', aliases=['pre', 'Prefix', 'PREFIX', 'Pre', 'PRE'])
async def change_prefix(ctx, new_prefix):
    """Change bot prefix command"""
    global current_prefix
    current_prefix = new_prefix

    # Update .env file
    try:
        with open('.env', 'r') as file:
            data = file.readlines()

        with open('.env', 'w') as file:
            for line in data:
                if line.startswith("DISCORD_BOT_PREFIX"):
                    file.write(f"DISCORD_BOT_PREFIX={new_prefix}\n")
                else:
                    file.write(line)

        embed = discord.Embed(
            description=f"Prefix changed to: `{new_prefix}`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=90)
    except Exception as e:
        print(f"Error updating prefix: {e}")
        embed = discord.Embed(
            description="Failed to update prefix",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=15)


async def main():
    """Main function to start the bot"""
    print("Starting bot...")
    async with bot:
        # Load music commands
        print("Loading music commands...")
        await setup_commands(bot, music_bot)

        # Start the bot
        print("Connecting to Discord...")
        await bot.start(DISCORD_API_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")
