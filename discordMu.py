import asyncio
import config
import discord
import json
import os
import praw
import pytz
import textwrap
from discord.ext import commands
from imgurpython import ImgurClient

client = ImgurClient(config.config['imgurClient'], config.config['imgurSecret'])



import webApp, mediaMu, miscMu, imageMu, gameMu, queueMu
from pingMu import pingMu

import importlib

importlib.reload(webApp)
importlib.reload(mediaMu)
importlib.reload(miscMu)
importlib.reload(imageMu)
importlib.reload(gameMu)
importlib.reload(queueMu)

# reddit initialize
reddit = praw.Reddit(client_id=config.config["redditClientID"],
                     client_secret=config.config['redditClientSecret'],
                     password=config.config["redditPass"],
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True

bot = commands.Bot(command_prefix='!',
                   description='Anumu has many many many features, too many to list so I only listed some.')


# class MyClient(discord.Client):
@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)


"""
help(ctx) provides a list of all commands except the hidden ones lol
"""


@bot.command()
async def helpme(ctx, arg=""):
    """Lists all non hidden commands in more depth"""
    if arg == "":
        await ctx.send(textwrap.dedent("""
        
        >>> ```!whatgame: takes in a list of games then randomly picks one and returns it 
        !again: rerolls the previous whatgame operation 
        !coin: flips a coin. 
        !goldmine:  leads you to the city of gold 
        !bl3 : is a function that @'s all owners of Borderlands 3 that I remembered to add
        !weebs: notifies weebs
        !headshot: provides a headshot of the great god's face 
        !glenoku: is exactly what you think it is 
        !timer: time is taken in time in units of minutes 
        !maketeams: Divides list into n random teams 
        !joined: prints when the user first joined the server.
        !getreddit: gets top n posts of given subreddit
        !poll: creates a strawpoll
        !yt: Plays a youtube video | !volume,!stop,!play,!join all supported
        !ytsearch: Searches and plays top rated youtube video 
        !stream: Same as yt but doesn't predownload so prolly should use this
        !firstmsg: gets date of first message and gives clickable link!
        !weebdar: gets name of anime and episode from gif or image
        !opgg: gets an accounts op.gg
        !twit: gets video of twitter post and sends it to channel, also works on twitch clips, prolly more
        !redv: gets reddit video from post
        
        Ping Library: (do !helpme ping)
        !pingCreate: Creates group for pinging purposes
        !pingAdd: Adds member to group 
        !pingRemove: Removes member from group
        !ping: Pings group
        
        ```
        


        For specific syntax do !helpme <command>
        """))
    elif arg == "whatgame":
        await ctx.send("""
        !whatgame <elt1, elt2, elt3,...> | Chooses one of elts
        """)
    elif arg == "again":
        await ctx.send("""
        !again | No parameters taken | Replays whatgame round
        """)
    elif arg == "coin":
        await ctx.send("""
        !coin | No parameters taken |Heads or Tails
        """)
    elif arg == "goldmine":
        await ctx.send("""
        !goldmine | No parameters taken
        """)
    elif arg == "bl3":
        await ctx.send("""
        !bl3 | No parameters taken
        """)
    elif arg == "weebs":
        await ctx.send("""
        !animegang | No parameters taken
        """)
    elif arg == "glenoku":
        await ctx.send("""
        !glenoku | No parameters taken
        """)
    elif arg == "timer":
        await ctx.send("""
        !timer <time> | time must be a number in minutes
        """)
    elif arg == "maketeams":
        await ctx.send("""
        !maketeams <n> <elt1, elt2, elt3,...> |  Divides list into n random teams
        """)
    elif arg == "joined":
        await ctx.send("""
        !joined @<Name>| Prints when user first joined the server
        """)
    elif arg == "getreddit":
        await ctx.send("""
        !getreddit <subreddit> <number of posts>| gets top n posts of given subreddit
        """)
    elif arg == "poll":
        await ctx.send("""
        !poll <title> <elt1, elt2, elt3,...> | Create a strawpoll with a title, and arguments
        """)
    elif arg == "yt":
        await ctx.send("""
        !yt <url> | Plays youtube video audio
        """)
    elif arg == "ytsearch":
        await ctx.send("""
        !ytsearch <name>| Plays youtube video audio
        """)
    elif arg == "firstmsg":
        await ctx.send("""
        !firstmsg | No parameters taken, channel based
        """)
    elif arg == "weebdar":
        await ctx.send("""
        !weebdar <url.jpg/png> | Gives information on what anime picture is from
        Can also do whatanime
        """)
    elif arg == "opgg":
        await ctx.send("""
        !opgg <username> | Grabs op.gg of user, put "" around name if there are spaces
        Can also do different regions by giving a second arg if you use the command !Ropgg
        kr,euw,etc 
        """)
    elif arg == "twot":
        await ctx.send("""
        !twit <url of post> | the url just has to be a twitter post
        This thing took so damn long to implement I should've just given up earlier
        damn twitter.
        """)
    elif arg == "redv":
        await ctx.send("""
        !redv <url of post> | the url is just any reddit post that has a v.reddit link
        screw this thing too
        """)
    elif arg == "ping":
        await ctx.send("""
        !pingCreate <Group Name>: Creates group for pinging purposes
        !pingAdd <Group Name> <@Members>: Adds listed members to group, do @ and let discord fill in the rest
        !pingRemove <Group Name> <@Member>: Removes member from group, do @ and let discord fill in the rest
        !ping <Group Name>: Pings group
        
        These functions create local files to keep track of them meaning they remain even if the Anumu Bot goes down.
        
        """)

def listToString(list):
    main = ""
    for item in list:
        main += item + " "
    main = main.strip()
    return main

"""
on_message(Gohan) is a shitpost
"""


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if 'Gohan' in message.content:
        if message.author != bot.user:
            channel = message.channel
            await channel.send('''Gohan?
            What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little "clever" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo.
            ''')



"""
timer(ctx,time) is takes in time in units of minutes
"""


@bot.command()
async def timer(ctx, numero: float):
    """Timer that takes in time in units of minutes"""
    await ctx.send("The timer has started")
    await asyncio.sleep(60 * numero)
    await ctx.send(str(numero) + ' minutes have passed.')


@bot.command(hidden=True)
async def remindme(ctx, dm, time: str, *args):
    """Do !help remindme

    Remind user via Direct Message or via current channel
    dm=0 for no dm, dm=1 for dm
    time is a number with a letter at the end (i.e 10s,13h)
    Can use s, m, h after time for seconds,minutes or hours. Minutes default"""
    message = listToString(args)
    case = time[-1]
    time = float(time[:-1])
    await ctx.send("The timer has started")
    if case == "m":
        await asyncio.sleep(60 * time)
        if bool(dm):
            await ctx.author.send("""{num} minutes have passed. Your message:
{msg}""".format(msg=message, num=str(time)))
            return
        await ctx.send("""{num} minutes have passed. Your message:
{msg}""".format(msg=message, num=str(time)))
    elif case == "s":
        await asyncio.sleep(time)
        if bool(dm):
            await ctx.author.send("""{num} seconds have passed. Your message:
{msg}""".format(msg=message, num=str(time)))
            return
        await ctx.send("""{num} seconds have passed. Your message:
{msg}""".format(msg=message, num=str(time)))
    elif case == "h":
        await asyncio.sleep(3600 * time)
        if bool(dm):
            await ctx.author.send("""{num} hours have passed. Your message:
{msg}""".format(msg=message, num=str(time)))
            return
        await ctx.send("""{num} hours have passed. Your message:
{msg}""".format(msg=message, num=str(time)))


######TEST


@bot.command(pass_context=True, hidden=True)
async def test(ctx):
    """test commands"""
    channel = ctx.message.channel
    print("Test")
    await ctx.send(ctx.guild.id)

@bot.command(pass_context=True, hidden=True)
async def invoke(ctx):
    """test commands"""
    channel = ctx.message.channel
    print("Test")
    ctx.invoke(test, ctx)
    await ctx.send(ctx.guild.id)

@bot.command(pass_context=True, hidden=True)
async def hbd(ctx):
    """adds happy birthday to thing"""
    if ctx.message.author.id == 161146253307150336:
        channel = ctx.message.channel
        await ctx.send(file=discord.File("imageMu/Happy_Birthday_Amumu_Edition.gif"))


@bot.command(pass_context=True, hidden=True)
async def shutdown(ctx):
    if ctx.message.author.id == 161146253307150336:
      print("shutdown")
      try:
        await bot.logout()
      except:
        print("EnvironmentError")
        bot.clear()
    else:
      await ctx.send("F off m8 you don't own me")

#######TEST

@bot.command(hidden=True)
async def cash(ctx):
    await ctx.send('Get yourself something nice :dollar:')


####Fun Server Features


"""
joined(ctx,member) prints when user first joined the server.
"""


@bot.command()
async def joined(ctx, *, member: discord.Member):
    """Prints when user first joined the server."""
    await ctx.send('{0} joined on {0.joined_at}'.format(member))


@bot.command(hidden=True)
async def latency(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))

"""
on_message_delete logger
"""

@bot.event
async def on_message_delete(message):
    await bot.process_commands(message)
    channel = message.channel
    os.environ["TZ"] = "EST"
    time = utc_to_local(message.created_at)
    file = {
         'author': message.author.name,
         'channel': message.channel.name,
         'time' : time.strftime("%m/%d/%Y, %H:%M:%S"),
        'message': message.content
        }
    with open('logMu/delete.json') as f:
        data = json.load(f)
    data["data"]['servers'].append(file)

    with open('logMu/delete.json', 'w') as f:
        json.dump(data, f)

"""
on_message_edit logger
"""

@bot.event
async def on_message_edit(message,after):
    await bot.process_commands(message)
    channel = message.channel
    time = utc_to_local(message.created_at)
    file = {
         'author': message.author.name,
         'channel': message.channel.name,
         'time' : time.strftime("%m/%d/%Y, %H:%M:%S"),
        'before': message.content,
        'afterl': after.content
        }
    #print(os.getcwd())
    with open('./logMu/edit.json') as f:
        data = json.load(f)
    data["data"]['servers'].append(file)

    with open('./logMu/edit.json', 'w') as f:
        json.dump(data, f)



local_tz = pytz.timezone("America/New_York")

def utc_to_local(utc):
    return utc.replace(tzinfo=pytz.utc).astimezone(local_tz)


"""
firstmsg(ctx) gets date of first message sent in chat
"""


@bot.command()
async def firstmsg(ctx):
    """Gets date of first message sent in chat"""
    channel = ctx.message.channel
    async for x in channel.history(limit=1, oldest_first=True):
        msg = x
        tim = utc_to_local(x.created_at)
    await ctx.send(tim)
    await ctx.send(msg.jump_url)


bot.add_cog(gameMu.League(bot))
bot.add_cog(imageMu.imageMu(bot))
bot.add_cog(pingMu.Ping(bot))
bot.add_cog(miscMu.Misc(bot))
bot.add_cog(webApp.web(bot))  # Reddit
bot.add_cog(webApp.why(bot))
bot.add_cog(mediaMu.Media(bot))
bot.add_cog(queueMu.Queue(bot))
bot.run(config.config["discordKey"])
