#Import these
import random
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

#Main class
class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False

        #Queue
        self.queue = []
        #YoutubeDL and Ffmpeg confings
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
                                'options': '-vn'}

        self.vc = ""

    #Search Method
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    #Go to next song
    def play_next(self):
        if len(self.queue) > 0:
            self.is_playing = True

            self.queue.pop(0)
            m_url = self.queue[0][0]['source']

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    #Infinite loop checking 
    async def play_music(self):
        if len(self.queue) > 0:
            self.is_playing = True

            m_url = self.queue[0][0]['source']
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.queue[0][1].connect()
            else:
                await self.vc.move_to(self.queue[0][1])
            
            print(self.queue)
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    #MUSIC COMMANDS LIST:

    #Play Command
    @commands.command(name= 'play', aliases=['p','plei','PLAY','Play','P'], 
                        help='Agrega la rola a la queue e inicia la reproducción')
    async def play(self, ctx, *args):
        query = " ".join(args)
        greetings = ["***Ya llegué pinches pobretones***   🔥 😎 :mechanical_leg: :mechanical_arm:", 
                    "***Una noche de lokeraaaa***   :face_in_clouds: :musical_note: :notes: ", 
                    "***Pero que haya morras chidas***   :smiling_imp: ",
                    "***Shorty tiene un qlo bn grande e***   :peach: ", 
                    "***'Cause I've got a golden ticket***   :tickets: ", 
                    "***k rollo con el pollo chavos***   :eyes:", 
                    "***K pdal***   :face_with_monocle: ","***Y las viejas?***   :worried: ",
                    "***Otro día otro dólar***   :face_exhaling: :money_mouth: ", 
                    "***Ahora q kieren pndejos?*** ", "***K se arme chavos***", 
                    "***Bbue, bueuee, bueuenNoos Díasss***", "***jala asia tras... sAs***", 
                    "***Todos basaotes mis chavos***", "***Todos basados B(***", 
                    "***Ya llegó el más basado***   :sunglasses: "]

        if ctx.author.voice is None:
            await ctx.send("***Eh qlro no te pases de reata ni siquiera estás en el vc***   :middle_finger: ")
        else:
            if ctx.voice_client is None:
                song = self.search_yt(query)
            
                if type(song) == type(True):
                    await ctx.send("***No pude hallar tu chingadera te la debo krnal***   :pleading_face:")
                else:
                    await ctx.send(random.choice(greetings))
                    self.queue.append([song,ctx.author.voice.channel])
                    await self.play_music()
                    retval = self.queue[0][0]['title']
                    await ctx.send('**Now playing:** *{}*'.format(retval))
            else:
                song = self.search_yt(query)
            
                if type(song) == type(True):
                    await ctx.send("***No pude hallar tu chingadera te la debo krnal***   :pleading_face:")
                else:
                    await ctx.send('*{}* ***- Agregada papu  :eject:  :notes:***'.format(song['title']))
                    self.queue.append([song,ctx.author.voice.channel])
                    await self.play_music()

    #Queue Command
    @commands.command(name='queue', aliases=['q','qiu','QUEUE','Queue','Q'], help='Muestra la queue')
    async def queue(self, ctx):
        retval = ""
        if ctx.author.voice is None:
            await ctx.send("***No estás en el vc papu***   :flushed:  ")
        else:
            for i in range(0, len(self.queue)):
                number = str(i+1)
                retval += "**" + number + ".** " + self.queue[i][0]['title'] + "\n"
            if retval != "":
                await ctx.send("***QUEUE***\n")
                await ctx.send("*Now Playing:* ")
                await ctx.send(retval)
            else:
                await ctx.send("***No hay nada en la Queue XD***")

    #Skip Command
    @commands.command(name='skip', aliases=['s','eskip','SKIP','Skip','S'], help='Salta a la rolita siguiente de la queue')
    async def skip(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("***Nonono papu métase***   :rolling_eyes:   ")
        else:
            if self.vc != "" and self.vc:
                self.vc.stop()
                await ctx.send("***Rola skippeada papu***   :fast_forward: ")
                retval = self.queue[0][0]['title']
                await ctx.send('**Now playing:** *{}*'.format(retval))

    #Remove Command
    @commands.command(name='remove', aliases=['r','rimuv','Remove','REMOVE','R'], help='Manda a la verga una rola de la queue')
    async def remove(self,ctx,index:int):
        if ctx.author.voice is None:
            await ctx.send("***No creo eh***   :face_with_monocle:    ")
        else:
            if len(self.queue) == 0:
                return await ctx.send('***No hay nada qué eliminar XDDD***')
            elif (index-1) == 0:
                self.vc.stop()
                retval = self.queue[0][0]['title']
                await ctx.send("*{}* ***- Chingadera eliminada***  :thumbsup_tone5: ".format(retval))
                np = self.queue[0][0]['title']
                await ctx.send('**Now playing:** *{}*'.format(np))
            else:
                x = index-1
                retval =self.queue[x][0]['title']
                self.queue.pop(index-1)
                await ctx.send("*{}* ***- Chingadera eliminada***  :thumbsup_tone5: ".format(retval))

    #Jump Command
    @commands.command(name='jump', aliases=['j', 'Jump','JUMP','J'], help='Salta hasta la rola que quieras de la queue')
    async def jump(self,ctx,index:int):
        if ctx.author.voice is None:
            await ctx.send("***Tas pndejo o k***   :sleepy:    ")
        else:
            if (index-1) == 0:
                await ctx.send('***Naaah kreoo***')
                return
            else:
                x = index-1
                np = self.queue[x][0]['title']
                await ctx.send('***Jumpeao a:*** *{}*  :ok_hand_tone5:'.format(np))
                for i in range(1,(index-1)):
                    self.queue.pop((index-1)-i)
                self.vc.stop()

    #Leave Command
    @commands.command(name='leave', aliases=['lif','LEAVE','Leave'], help='Manda a la chingada al bot')
    async def leave(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("***Métete krnal***   :weary:     ")
        else:
            farewell = ["***Ta bno ps***   👀", "***Pinche voice chat feo***   :face_with_hand_over_mouth:", 
                        "***kmrones ps chabos***   :shrimp: :shrimp: :shrimp: ", 
                        "***Recuerden chavos***   :eye: :point_right: :ghost: ", 
                        "***Tanto daño te an echo?***", "***Kmara se la lavan***   :hot_face: ", 
                        "***BUenas Nchessx.  tqlm. jajaa. que. descanses. uchp. diosito. te qcuida. siempre. péinsao. en it. porque. mne trae. buenos recuerdos. jajaa. xd.***", 
                        "***Ya váyanse ps kbrones***", "***Gracias a Dios, ya me quería ir alv***", 
                        "***Por k hablo con estos pndejos? Ay... lol lo escribí***",
                        "***AAAAAAAAAAAAAAAAAAHHHHHHHH!***  *explota*", "***Basabasabsa basura***", 
                        "***BABABABB BASADO***"]
            self.is_playing = False
            await ctx.voice_client.disconnect()
            await ctx.send(random.choice(farewell))
            self.queue = []

    #Pause Command
    @commands.command(name='pause',aliases=['pausa','pa','Pause','PAUSE'],help='Pausa la rolita :v')
    async def pause(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("***Métete krnal***   :weary:     ")
        else:
            await ctx.send(":pause_button:      :regional_indicator_p::regional_indicator_a::regional_indicator_p::regional_indicator_u:")
            await ctx.voice_client.pause()
        
    #Resume Command
    @commands.command(name='resume', aliases=['unpause','re','un'],help='Despausa la rolita :vvv')
    async def resume(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("***Tas pndejo o k***   :sleepy:    ")
        else:
            await ctx.send(":arrow_forward:    :regional_indicator_p::regional_indicator_a::regional_indicator_p::regional_indicator_u:")
            await ctx.voice_client.resume()
    
    #Now Playing Command
    @commands.command(name='nowplaying', aliases=['np','Nowplaying','now','playing','NP','NOWPLAYING',"pn"],help='Muestra qué chingados está sonando')
    async def nowplaying(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("***No creo eh***   :face_with_monocle:    ")
        else:
            retval = self.queue[0][0]['title']
            await ctx.send('**Now playing:** *{}*  :musical_note:'.format(retval))

'''
All the messages here are based on the server was made for
some of them are references and everything can modified
to your server references and neccesties, also de aliases for the commands
and the help messages
'''

#Add the cogs to main
def setup(client):
    client.add_cog(music(client))