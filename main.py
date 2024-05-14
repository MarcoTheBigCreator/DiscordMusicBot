"""DISCORD MUSIC BOT CRUMMY Version 1.5 (stable)"""

# Importing libraries
import asyncio

import discord
from discord import ClientException
from discord.ext import commands, tasks

from dotenv import load_dotenv

from yt_dlp import YoutubeDL

import os

load_dotenv()

# DISCORD API TOKEN FROM .ENV
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

if not DISCORD_API_TOKEN:
    raise ValueError("DISCORD_API_TOKEN is not set in .env file")

# Global variables
is_playing = False
is_looping_playlist = False

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

# Defining prefix of commands
bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), help_command=help_command)


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
    await ctx.send(embed=embed)


# Search the title written by the user
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception:
            return False

    return {'source': info['url'], 'title': info['title']}


# Play next song (loop experimental)
def play_next():
    global is_playing, vc, mqueue, is_looping_playlist
    
    if is_looping_playlist:
        mqueue.append(mqueue[0])  # Add the first song to the end of the queue
    if len(mqueue) > 0:
        is_playing = True
        mqueue.pop(0)
        if len(mqueue) > 0:
            m_url = mqueue[0][0]['source']
            vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
            asyncio.run_coroutine_threadsafe(send_now_playing_message(mqueue[0][0]['title']), bot.loop)
        else:
            is_playing = False

# Function to send now playing message
async def send_now_playing_message(song_title):
    global vc, mqueue
    
    text_channel = mqueue[0][2]
    
    embed = discord.Embed(title="Now Playing", description=f"{song_title}", color=discord.Color.light_gray())
    await text_channel.send(embed=embed)

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
        await ctx.send(embed=embed)
        return

    # Connect to the user's voice channel
    if vc is None or not vc.is_connected():
        vc = await ctx.author.voice.channel.connect()
    elif vc.channel != ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)
        embed = discord.Embed(description="Moving to your voice channel", color=discord.Color.blue())
        await ctx.send(embed=embed)

    if is_playing:
        # Add the song to the queue
        ctx.voice_client.resume()        
        song = search_yt(query)
        if isinstance(type(song), type(True)):
            embed = discord.Embed(description="I could not find that song", color=discord.Color.red())       
            await ctx.send(embed=embed)
        else:
            mqueue.append([song, ctx.author.voice.channel, ctx.channel, ctx.author])
            
            author = ctx.author
            embed = discord.Embed(title="Queued", color=discord.Color.green())
            embed.add_field(name="Song", value=song['title'], inline=False)
            embed.add_field(name="By", value=[author.mention], inline=False)
            
            await ctx.send(embed=embed)
    else:
        # Start playing the song
        ctx.voice_client.resume()        
        song = search_yt(query)
        if isinstance(type(song), type(True)):
            embed = discord.Embed(description="I could not find that song", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            # embed = discord.Embed(title="Now Playing", description=f"{song['title'], ctx.author}", color=discord.Color.green())
            # await ctx.send(embed=embed)
            mqueue.append([song, ctx.author.voice.channel, ctx.channel, ctx.author])
            
            author = ctx.author
            embed = discord.Embed(title="Now Playing", color=discord.Color.green())
            embed.add_field(name="Song", value=song['title'], inline=False)
            embed.add_field(name="By", value=[author.mention], inline=False)
            await ctx.send(embed=embed)
            
            await play_music()
    ctx.voice_client.resume()


# Queue Command
@bot.command(name='queue', aliases=['q', 'qiu', 'QUEUE', 'Queue', 'Q'], help='Shows the queue of songs')
async def queue(ctx):
    global mqueue
    
    if ctx.author.voice is None:
        embed = discord.Embed(description=f"You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Queue", color=discord.Color.green())
        if len(mqueue) > 0:
            for i, item in enumerate(mqueue, 1):
                if isinstance(item[3], discord.Member):
                    requester_mention = item[3].mention
                else:
                    requester_mention = "Unknown"
                
                if i == 1 and ctx.voice_client.is_playing():
                    embed.add_field(name=f"**Now Playing -** {i}. {item[0]['title']}", value="", inline=True)
                else:
                    embed.add_field(name=f"{i} - {item[0]['title']}", value="", inline=True)
        else:
            embed.description = "Queue is empty"
        await ctx.send(embed=embed)


# Skip Command
@bot.command(name='skip', aliases=['s', 'SKIP', 'Skip', 'S'], help='Skips the current song')
async def skip(ctx):
    global vc, mqueue
    
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        if not mqueue:
            embed = discord.Embed(description="The queue is empty", color=discord.Color.dark_red())
            await ctx.send(embed=embed)
        elif vc != "" and vc:
            vc.stop()
            retval = mqueue[0][0]['title']
            embed = discord.Embed(title="Song skipped",description=f"{retval}", color=discord.Color.green())
            await ctx.send(embed=embed)


# Remove Command
@bot.command(name='remove', aliases=['r', 'Remove', 'REMOVE', 'R'],
             help='Removes a song from the queue (Example: -remove 2)')
async def remove(ctx, index: int):
    global vc, mqueue
    
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        if len(mqueue) == 0:
            embed = discord.Embed(description="There is nothing to erase", color=discord.Color.red())
            return await ctx.send(embed=embed)
        elif (index - 1) == 0:
            vc.stop()
            retval = mqueue[0][0]['title']
            np = mqueue[0][0]['title']
            emebed = discord.Embed(title="Song removed", description=f"{retval}", color=discord.Color.dark_grey())
            embed.add_field(name="Now playing", value=f"{np}", inline=False)
            await ctx.send(embed=emebed)
        else:
            x = index - 1
            retval = mqueue[x][0]['title']
            mqueue.pop(index - 1)
            embed = discord.Embed(description=f"Removed {retval}", color=discord.Color.dark_grey())
            await ctx.send(embed=embed)


# Jump Command
@bot.command(name='jump', aliases=['j', 'Jump', 'JUMP', 'J'],
             help='Jumps to a song in the queue (Example: -jump 2)')
async def jump(ctx, index: int):
    global vc
    
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        if (index - 1) == 0:
            embed = discord.Embed(description="You can't jump an empty queue", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        else:
            x = index - 1
            np = mqueue[x][0]['title']
            embed = discord.Embed(description=f"Jumped to {np}", color=discord.Color.green())
            await ctx.send(embed=embed)
            for i in range(1, (index - 1)):
                mqueue.pop((index - 1) - i)
            vc.stop()


# Loop Command (experimental)
@bot.command(name='loop', aliases=['l', 'LOOP', 'Loop'], help='Loops the current playlist')
async def playlist_loop(ctx):
    global is_looping_playlist
    
    is_looping_playlist = not is_looping_playlist
    
    embed = discord.Embed(description=f"{'loop enabled' if is_looping_playlist else 'loop disabled'}", color=discord.Color.blue())
    await ctx.send(embed=embed)

# Leave Command
@bot.command(name='leave', aliases=['LEAVE', 'Leave'], help='Leaves the Voice Channel')
async def leave(ctx):
    global vc, is_playing, mqueue, is_looping_playlist
    
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        is_playing = False
        is_looping_playlist = False
        
        await ctx.voice_client.disconnect()
        embed = discord.Embed(description="Disconnected", color=discord.Color.dark_grey())
        await ctx.send(embed=embed)
        
        mqueue = []
        vc = None

# Pause Command
@bot.command(name='pause', aliases=['pa', 'Pause', 'PAUSE'], help='Pause the song')
async def pause(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif ctx.voice_client.is_playing():
        embed = discord.Embed(description="Paused", color=discord.Color.blue())
        await ctx.send(embed=embed)
        ctx.voice_client.pause()
    else:
        embed = discord.Embed(description="There is no song playing to pause", color=discord.Color.red())


# Resume Command
@bot.command(name='resume', aliases=['unpause', 're', 'un'], help='Resume the song')
async def resume(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif ctx.voice_client is None:
        embed = discord.Embed(description="The bot is not connected to a voice channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif ctx.voice_client.is_paused():
        embed = discord.Embed(description="Resumed", color=discord.Color.blue())
        await ctx.send(embed=embed)
        ctx.voice_client.resume()
    else:
        embed = discord.Embed(description="The song is not paused", color=discord.Color.red())
        await ctx.send(embed=embed)
        ctx.voice_client.resume()


# Now Playing Command
@bot.command(name='nowplaying', aliases=['np', 'Nowplaying', 'NP', 'NOWPLAYING'],
             help='Shows the song that is playing')
async def nowplaying(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        embed = discord.Embed(description="You're not in a Voice Channel", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        retval = mqueue[0][0]['title']
        embed = discord.Embed(title="Now Playing", description=f"{retval}", color=discord.Color.blue())
        await ctx.send(embed=embed)

# bot run loging in with token
bot.run(DISCORD_API_TOKEN)
