#Import these
import discord
from discord.ext import commands, tasks
import music

cogs = [music]

#Help command
help_command = commands.DefaultHelpCommand(no_category = 'Commands')

#Defining prefix of commands
client = commands.Bot(command_prefix='-', Intents = discord.Intents.all(),help_command = help_command)

# START EVENTS:
@client.event
async def on_ready():
    status.start()
    print('Bot is online')

@tasks.loop(seconds=1)
async def status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Sida"))

# Ping Command
@client.command( name= 'ping', aliases=['pinga'], help = 'Verifica si tienes algo de lag')
async def ping(ctx):
    await ctx.send(f'*{round(client.latency * 1000)} ms*')


# Basado Command
'''
This command was made for fun and entertainment of a server in common
It can be erased or modified to your server
It is not a vital command for the whole functioning of the bot


@client.command(name='basado', aliases=['basadote','b','bsado','basadisimo'], help= 'Úsalo cuando alguien se haya pasado de Basadote' )
async def basado(ctx,*args):
    persona = " ".join(args)
    
    basado = ["Bien basadote", "Basadísimo", "Basado", "A dónde tan basado", "Qué basado", 
            "Muy basado de tu parte", "Muy basadísimo de tu parte", "Basadote de tu parte"
            "Párenlo está muy basado"]
    
    basada = ["Bien basadota", "Basadísima", "Basada", "A dónde tan basada", "Qué basada", 
            "Muy basado de tu parte", "Muy basadísimo de tu parte", "Basadote de tu parte"
            "Párenla está muy basada"]
    
    emojis = ["   :unamused: ","  :zipper_mouth: ","   :face_with_monocle: ", "   :sunglasses: ",
            "  :pleading_face: ", "  :eyes: ", "  :smiling_imp: ", "  :imp: ", "  :hot_face: "
            ,"  :face_in_clouds: "]
    
    rbasado = random.choice(basado)
    rbasada = random.choice(basada)
    remojis = random.choice(emojis)
    
    if(persona == "fernanda" or persona == "Fernanda" or persona == "fercho" or persona == "Fercho" 
        or persona =="carmen" or persona == "Carmen" or persona == "frnda" or persona == "elena"
        or persona == "frnanda" or persona == "Frnanda" or persona == "Elena" or persona == "Melanie" 
        or persona == "melanie"or persona == "Eligarden" or persona == "eligarden" 
        or persona == "Karely" or persona == "karely" or persona == "Durán" or persona == "Duran"
        or persona == "duran" or persona == "durán"):
    
        if (rbasada == "Bien basadota" or rbasada == "Basadísima" or rbasada == "Basada" 
        or rbasada == "Qué basada" or rbasada == "Párenlo está muy basada"):
        
            bsada = "***" + rbasada + " la " + persona + remojis + "***"
            await ctx.send(bsada)
        
        elif(rbasada == "A dónde tan basada" or rbasada == "Muy basado de tu parte" 
        or rbasada == "Muy basadísimo de tu parte" or rbasada == "Basadote de tu parte"):
            
            bsada = "***" + rbasada + " " + persona + remojis + "***"
            await ctx.send(bsada)
    else:
        
        if (rbasado == "Bien basadote" or rbasado == "Basadísimo" or rbasado == "Basado" 
        or rbasado == "Qué basado" or rbasado == "Párenlo está muy basado"):
        
            bsado = "***" + rbasado + " el " + persona + remojis + "***"
            await ctx.send(bsado)
        
        elif(rbasado == "A dónde tan basado" or rbasado == "Muy basado de tu parte" 
        or rbasado == "Muy basadísimo de tu parte" or rbasado == "Basadote de tu parte"):

            bsado = "***" + rbasado + " " +persona + remojis + "***"
            await ctx.send(bsado)
'''

#Process of cogs
for i in range(len(cogs)):
    cogs[i].setup(client)

client.run('YOUR BOT TOKEN')