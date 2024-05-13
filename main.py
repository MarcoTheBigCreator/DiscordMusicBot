"""DISCORD MUSIC BOT CRUMMY Version 1.1 (stable)"""

# Importing libraries
import discord
from discord import ClientException
from discord.ext import commands, tasks

from dotenv import load_dotenv

from yt_dlp import YoutubeDL

import os
import random

load_dotenv()

# DISCORD API TOKEN FROM .ENV
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

if not DISCORD_API_TOKEN:
    raise ValueError('No se encontró el token de Discord.')

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
@bot.command(name='ping', aliases=['pinga'], help='Verifies the bot\'s latency')
async def ping(ctx):
    await ctx.send(f'*{round(bot.latency * 1000)} ms*')


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
        mqueue.append(mqueue[0])  # Agrega la misma canción nuevamente al final de la cola
    if len(mqueue) > 0:
        is_playing = True
        mqueue.pop(0)
        if len(mqueue) > 0:
            m_url = mqueue[0][0]['source']
            vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
        else:
            is_playing = False


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
    # You can add more greetings
    greeting = ["***Hi guys***   🔥 😎"]

    if ctx.author.voice is None:
        await ctx.send("***You're not in a Voice Channel***   :flushed:  ")
        return

    # Connect to the user's voice channel
    if vc is None or not vc.is_connected():
        vc = await ctx.author.voice.channel.connect()
    elif vc.channel != ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)
        await ctx.send("***Moving to your voice channel*** :ok_hand:")

    if is_playing:
        # Add the song to the queue
        ctx.voice_client.resume()        
        song = search_yt(query)
        if isinstance(type(song), type(True)):       
            await ctx.send("***I could not find that song***   :pleading_face:")
        else:
            mqueue.append([song, ctx.author.voice.channel])
            await ctx.send('*{}* ***- Added to queue  :eject:  :notes:***'.format(song['title']))
    else:
        # Start playing the song
        ctx.voice_client.resume()        
        song = search_yt(query)
        if isinstance(type(song), type(True)):
            await ctx.send("***I could not find that song***   :pleading_face:")
        else:
            await ctx.send(random.choice(greeting))
            await ctx.send('*{}* ***- Now playing  :eject:  :notes:***'.format(song['title']))
            mqueue.append([song, ctx.author.voice.channel])
            await play_music()
    ctx.voice_client.resume()

# Queue Command
@bot.command(name='queue', aliases=['q', 'qiu', 'QUEUE', 'Queue', 'Q'], help='Shows the queue of songs')
async def queue(ctx):
    global vc, mqueue
    retval = ""
    if ctx.author.voice is None:
        await ctx.send("***You're not on the Voice Channel***   :flushed:  ")
    else:
        for i in range(0, len(mqueue)):
            number = str(i + 1)
            retval += "**" + number + ".** " + mqueue[i][0]['title'] + "\n"
        if retval != "":
            await ctx.send("***QUEUE***\n")
            await ctx.send("*Now Playing:* ")
            await ctx.send(retval)
        else:
            await ctx.send("***Queue is empty!***")


# Skip Command
@bot.command(name='skip', aliases=['s', 'SKIP', 'Skip', 'S'], help='Skips the current song')
async def skip(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        await ctx.send("***You must enter to the Voice Channel!***   :rolling_eyes:   ")
    else:
        if vc != "" and vc:
            vc.stop()
            await ctx.send("***Song skipped***   :fast_forward: ")
            retval = mqueue[0][0]['title']
            await ctx.send('**Now playing:** *{}*'.format(retval))


# Remove Command
@bot.command(name='remove', aliases=['r', 'Remove', 'REMOVE', 'R'],
             help='Removes a song from the queue (Example: -remove 2)')
async def remove(ctx, index: int):
    global vc, mqueue
    if ctx.author.voice is None:
        await ctx.send("***I don't think so***   :face_with_monocle:    ")
    else:
        if len(mqueue) == 0:
            return await ctx.send('***There is nothing to erase***')
        elif (index - 1) == 0:
            vc.stop()
            retval = mqueue[0][0]['title']
            await ctx.send("*{}* ***- Song removed***  :thumbsup: ".format(retval))
            np = mqueue[0][0]['title']
            await ctx.send('**Now playing:** *{}*'.format(np))
        else:
            x = index - 1
            retval = mqueue[x][0]['title']
            mqueue.pop(index - 1)
            await ctx.send("*{}* ***- Song removed***  :thumbsup: ".format(retval))


# Jump Command
@bot.command(name='jump', aliases=['j', 'Jump', 'JUMP', 'J'],
             help='Jumps to a song in the queue (Example: -jump 2)')
async def jump(ctx, index: int):
    global vc
    if ctx.author.voice is None:
        await ctx.send("***You must enter to the Voice Channel!***   :sleepy:    ")
    else:
        if (index - 1) == 0:
            await ctx.send('***I don\'t think so***')
            return
        else:
            x = index - 1
            np = mqueue[x][0]['title']
            await ctx.send('***Jumped to:*** *{}*  :ok_hand:'.format(np))
            for i in range(1, (index - 1)):
                mqueue.pop((index - 1) - i)
            vc.stop()

# Loop Command (experimental)
@bot.command(name='loop', aliases=['l', 'LOOP', 'Loop'], help='Toggle playlist loop')
async def playlist_loop(ctx):
    global is_looping_playlist
    is_looping_playlist = not is_looping_playlist
    await ctx.send(f"{'***loop enabled***' if is_looping_playlist else '***loop disabled***'}  :repeat: ")

# Leave Command
@bot.command(name='leave', aliases=['LEAVE', 'Leave'], help='Leaves the Voice Channel')
async def leave(ctx):
    global vc, is_playing, mqueue, is_looping_playlist
    if ctx.author.voice is None:
        await ctx.send("***You must enter to the Voice Channel***   :weary:     ")
    elif ctx.voice_client is None:
        await ctx.send("***The bot is not connected to a voice channel***   :confused:    ")
    else:
        # You can add more farewell messages
        farewell = ["***See ya guys***   👀"]
        is_playing = False
        is_looping_playlist = False
        await ctx.voice_client.disconnect()
        await ctx.send(random.choice(farewell))
        mqueue = []
        vc = None

# Pause Command
@bot.command(name='pause', aliases=['pa', 'Pause', 'PAUSE'], help='Pause the song')
async def pause(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        await ctx.send("***You must enter to the Voice Channel***   :weary:     ")
    elif ctx.voice_client is None:
        await ctx.send("***The bot is not connected to a voice channel***   :confused:    ")
    elif ctx.voice_client.is_playing():
        await ctx.send(":pause_button:")
        ctx.voice_client.pause()
    else:
        await ctx.send("***There is no song playing to pause***   :thinking:    ")


# Resume Command
@bot.command(name='resume', aliases=['unpause', 're', 'un'], help='Resume the song')
async def resume(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        await ctx.send("***You must enter to the Voice Channel***   :sleepy:    ")
    elif ctx.voice_client is None:
        await ctx.send("***The bot is not connected to a voice channel***   :confused:    ")
    elif ctx.voice_client.is_paused():
        await ctx.send(":arrow_forward:")
        ctx.voice_client.resume()
    else:
        await ctx.send("***The song is not paused***   :rolling_eyes:    ")
        ctx.voice_client.resume()


# Now Playing Command
@bot.command(name='nowplaying', aliases=['np', 'Nowplaying', 'NP', 'NOWPLAYING'],
             help='Shows the song that is playing')
async def nowplaying(ctx):
    global vc, mqueue
    if ctx.author.voice is None:
        await ctx.send("***I don't think so***   :face_with_monocle:    ")
    else:
        retval = mqueue[0][0]['title']
        await ctx.send('**Now playing:** *{}*  :musical_note:'.format(retval))


# bot run loging in with token
bot.run(DISCORD_API_TOKEN)
