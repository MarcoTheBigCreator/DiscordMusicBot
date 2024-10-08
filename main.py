"""DISCORD MUSIC BOT CRUMMY Version 2.1 (stable)"""

# Importing libraries
import asyncio

import discord
from discord import ClientException
from discord.ext import commands, tasks

from dotenv import load_dotenv

from yt_dlp import YoutubeDL

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# DISCORD API TOKEN FROM .ENV
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

if not DISCORD_API_TOKEN:
    raise ValueError("DISCORD_API_TOKEN is not set in .env file")

# PREFIX FROM .ENV
PREFIX = os.getenv("DISCORD_BOT_PREFIX")
if not PREFIX:
    raise ValueError("DISCORD_BOT_PREFIX is not set in .env file")

# Global variables
is_playing = False
is_looping_playlist = False
current_prefix = PREFIX

# Queue
mqueue = []
# Options for the YoutubeDL
YDL_OPTIONS = {'format': 'm4a/bestaudio/best', 'noplaylist': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}

# Voice channel
vc = None

# Defining help command
help_command = commands.DefaultHelpCommand(no_category='Commands')

# Function to get the prefix if changed
def get_prefix(bot, message):
    return current_prefix

# Defining prefix of commands
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all(), help_command=help_command)


# When the bot is ready
@bot.event
async def on_ready():
    status.start()
    print('Bot is online')


# When a member joins the server
@tasks.loop(seconds=1)
async def status():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music"))


# Ping Command
@bot.command(name='ping', aliases=['PING'], help='Verifies the bot\'s latency')
async def ping(ctx):
    embed = discord.Embed(title="Pong!   🏓", description=f'{round(bot.latency * 1000)} ms', color=discord.Color.red())
    await ctx.send(embed=embed, delete_after=60)


# Search the title written by the user
def search_yt(item):
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            return {'source': info['url'], 'title': info['title']}
    except Exception as e:
        print(f"Error in search_yt: {e}")
        return None


def play_next():
    global is_playing, vc, mqueue, is_looping_playlist

    if is_looping_playlist:
        mqueue.append(mqueue[0])  # Add the first song to the end of the queue
    if len(mqueue) > 0:
        is_playing = True
        mqueue.pop(0)
        if len(mqueue) > 0:
            m_url = mqueue[0][0]['source']
            # Check if vc is connected before trying to play
            if vc and vc.is_connected():
                vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
                asyncio.run_coroutine_threadsafe(send_now_playing_message(mqueue[0][0]['title']), bot.loop)
            else:
                is_playing = False
        else:
            is_playing = False
    else:
        is_playing = False


# Function to send now playing message
async def send_now_playing_message(song_title):
    global vc, mqueue

    text_channel = mqueue[0][2]

    embed = discord.Embed(title="Now Playing", description=f"{song_title}", color=discord.Color.light_gray())
    await text_channel.send(embed=embed, delete_after=120)


# infinite loop checking for songs in the queue
async def play_music():
    global is_playing, vc, mqueue

    if len(mqueue) > 0:
        is_playing = True

        m_url = mqueue[0][0]['source']
        if vc == "" or not vc.is_connected() or vc is None:
            vc = await mqueue[0][1].connect()
        else:
            await vc.move_to(mqueue[0][1])

        print(mqueue)
        try:
            vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
        except ClientException as e:
            print(f"Ignoring exception: {e}")
            pass
    else:
        is_playing = False

# Music Commands
# Play Command
@bot.command(name='play', aliases=['p', 'PLAY', 'Play', 'P'],
             help='Add a song to the queue (Example: -play dark necessities)')
async def play(ctx, *args):
    global vc, mqueue

    query = " ".join(args)

    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
        return

    # Connect to the user's voice channel
    if vc is None or not vc.is_connected():
        vc = await ctx.author.voice.channel.connect()
    elif vc.channel != ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)
        embed = discord.Embed(description="Moving to your voice channel", color=discord.Color.blue())
        await ctx.send(embed=embed, delete_after=15)

    if is_playing:
        # Add the song to the queue
        ctx.voice_client.resume()
        song = search_yt(query)
        if song is None:
            embed = discord.Embed(description="I could not find that song", color=discord.Color.red())
            await ctx.send(embed=embed, delete_after=15)
        else:
            mqueue.append([song, ctx.author.voice.channel, ctx.channel, ctx.author])

            author = ctx.author
            embed = discord.Embed(title="Queued", color=discord.Color.green())
            embed.add_field(name="Song", value=song['title'], inline=False)
            embed.add_field(name="By", value=[author.mention], inline=False)

            await ctx.send(embed=embed, delete_after=120)
    else:
        # Start playing the song
        ctx.voice_client.resume()
        song = search_yt(query)
        if song is None:
            embed = discord.Embed(description="I could not find that song", color=discord.Color.red())
            await ctx.send(embed=embed, delete_after=15)
        else:
            mqueue.append([song, ctx.author.voice.channel, ctx.channel, ctx.author])

            author = ctx.author
            embed = discord.Embed(title="Now Playing", color=discord.Color.green())
            embed.add_field(name="Song", value=song['title'], inline=False)
            embed.add_field(name="By", value=[author.mention], inline=False)
            await ctx.send(embed=embed, delete_after=120)

            await play_music()
    ctx.voice_client.resume()


# Queue Command
@bot.command(name='queue', aliases=['q', 'QUEUE', 'Queue', 'Q'], help='Shows the queue of songs')
async def queue(ctx):
    global mqueue

    if ctx.author.voice is None:
        embed = discord.Embed(description=f"You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        embed = discord.Embed(title="Queue", color=discord.Color.green())
        if len(mqueue) > 0:
            max_songs = min(25, len(mqueue))  # Limit to 25 songs or fewer
            for i in range(max_songs):
                item = mqueue[i]
                if isinstance(item[3], discord.Member):
                    requester_mention = item[3].mention
                else:
                    requester_mention = "Unknown"

                if i == 0 and ctx.voice_client.is_playing():
                    embed.add_field(name=f"***Now Playing - *** {i + 1}. {item[0]['title']}", value="", inline=False)
                else:
                    embed.add_field(name=f"{i + 1}. {item[0]['title']}", value="", inline=False)
            if len(mqueue) > max_songs:
                footer_text = f"And {len(mqueue) - max_songs} more..."
                embed.set_footer(text=footer_text)
        else:
            embed.description = "Queue is empty"
        await ctx.send(embed=embed, delete_after=3600)


# Skip Command
@bot.command(name='skip', aliases=['s', 'SKIP', 'Skip', 'S'], help='Skips the current song')
async def skip(ctx):
    global vc, mqueue

    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        if not mqueue:
            embed = discord.Embed(description="The queue is empty", color=discord.Color.dark_red())
            await ctx.send(embed=embed, delete_after=15)
        elif vc != "" and vc:
            vc.stop()
            retval = mqueue[0][0]['title']
            embed = discord.Embed(title="Song skipped", description=f"{retval}", color=discord.Color.green())
            await ctx.send(embed=embed, delete_after=120)


# Remove Command
@bot.command(name='remove', aliases=['r', 'Remove', 'REMOVE', 'R'],
             help='Removes a song from the queue (Example: -remove 2)')
async def remove(ctx, index: int):
    global vc, mqueue

    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        if len(mqueue) == 0:
            embed = discord.Embed(description="There is nothing to erase", color=discord.Color.red())
            return await ctx.send(embed=embed, delete_after=15)
        elif (index - 1) == 0:
            vc.stop()
            retval = mqueue[0][0]['title']
            np = mqueue[0][0]['title']
            embed = discord.Embed(title="Song removed", description=f"{retval}", color=discord.Color.dark_grey())
            embed.add_field(name="Now playing", value=f"{np}", inline=False)
            await ctx.send(embed=embed)
        else:
            x = index - 1
            retval = mqueue[x][0]['title']
            mqueue.pop(index - 1)
            embed = discord.Embed(description=f"Removed {retval}", color=discord.Color.dark_grey())
            await ctx.send(embed=embed)


# Jump Command (experimental improvement)
@bot.command(name='jump', aliases=['j', 'Jump', 'JUMP', 'J'],
             help='Jumps to a song in the queue (Example: -jump 2)')
async def jump(ctx, index: int):
    global vc, mqueue

    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        if len(mqueue) == 0:
            embed = discord.Embed(description="The queue is empty", color=discord.Color.red())
            await ctx.send(embed=embed, delete_after=15)
            return
        
        if index <= 1 or index > len(mqueue):
            embed = discord.Embed(description="Invalid index", color=discord.Color.red())
            await ctx.send(embed=embed, delete_after=15)
            return

        # Songs to be moved to the end of the queue
        if is_looping_playlist == False:
            songs_to_move = mqueue[:index-1]
        else:
            songs_to_move = mqueue[:index-2]

        # Remaining queue starts from the requested song
        mqueue = mqueue[index-2:]

        # Append the moved songs to the end of the queue
        mqueue.extend(songs_to_move)

        # Stop the current song
        if vc.is_playing():
            vc.stop()

        # Optional: Notify the user
        # np = mqueue[1][0]['title']
        # embed = discord.Embed(description=f"Jumped to {np}", color=discord.Color.green())
        # await ctx.send(embed=embed, delete_after=30)

# Loop Playlist Command (experimental)
@bot.command(name='loop', aliases=['l', 'LOOP', 'Loop'], help='Loops the playlist (once to enable, twice to disable)')
async def playlist_loop(ctx):
    global is_looping_playlist

    is_looping_playlist = not is_looping_playlist

    embed = discord.Embed(description=f"{'loop **enabled**' if is_looping_playlist else 'loop **disabled**'}",
                          color=discord.Color.blue())
    await ctx.send(embed=embed)


# Leave Command
@bot.command(name='leave', aliases=['LEAVE', 'Leave'], help='Leaves the Voice Channel')
async def leave(ctx):
    global vc, is_playing, mqueue, is_looping_playlist

    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        is_playing = False
        is_looping_playlist = False

        await ctx.voice_client.disconnect()
        embed = discord.Embed(description="Disconnected", color=discord.Color.dark_grey())
        await ctx.send(embed=embed, delete_after=15)

        mqueue = []
        vc = None


# Pause Command
@bot.command(name='pause', aliases=['pa', 'Pause', 'PAUSE'], help='Pause the song')
async def pause(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    elif ctx.voice_client.is_playing():
        embed = discord.Embed(description="Paused", color=discord.Color.blue())
        await ctx.send(embed=embed)
        ctx.voice_client.pause()
    else:
        embed = discord.Embed(description="There is no song playing to pause", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)


# Resume Command
@bot.command(name='resume', 
             aliases=['unpause', 're', 'un', 'Resume', 'Unpause', 'RESUME', 'UNPAUSE', 'RE'], 
             help='Resume the song')
async def resume(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    elif ctx.voice_client.is_paused():
        embed = discord.Embed(description="Resumed", color=discord.Color.blue())
        await ctx.send(embed=embed)
        ctx.voice_client.resume()
    else:
        embed = discord.Embed(description="The song is not paused", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
        ctx.voice_client.resume()


# Now Playing Command
@bot.command(name='nowplaying', aliases=['np', 'Nowplaying', 'NP', 'NOWPLAYING'],
             help='Shows the song that is playing')
async def nowplaying(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed, delete_after=15)
    else:
        retval = mqueue[0][0]['title']
        embed = discord.Embed(title="Now Playing", description=f"{retval}", color=discord.Color.blue())
        await ctx.send(embed=embed, delete_after=120)

# Change Prefix Command
@bot.command(name='prefix', aliases=['pre', 'Prefix', 'PREFIX', 'Pre', 'PRE'], help='Change the prefix of the bot (Example: -prefix !)')
async def changeprefix(ctx, new_prefix):
    global current_prefix
    current_prefix = new_prefix

    # Read the .env file
    with open('.env', 'r') as file:
        data = file.readlines()

    # Write the new prefix to the .env file
    with open('.env', 'w') as file:
        for line in data:
            if line.startswith("DISCORD_BOT_PREFIX"):
                file.write(f"DISCORD_BOT_PREFIX={new_prefix}\n")
            else:
                file.write(line)

    embed  = discord.Embed(description=f"Prefix changed to: `{new_prefix}`", color=discord.Color.green())
    await ctx.send(embed=embed, delete_after=90)

# bot run logging in with token
bot.run(DISCORD_API_TOKEN)
