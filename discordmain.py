import discord
import random
from discord.ext import commands
import asyncio
import strawpoll
from cv2 import cv2
import numpy as np
import time
import praw
import requests
import json
import urllib.request

bot = commands.Bot(command_prefix='!')
globlist = []

def cmplist(list): #Actually this function calls from another function
    global globlist
    if (len(list) > len(globlist)):
        globlist = list[:] #copy all element of list to globlist

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def prettylist(lst):
    acc = ""
    for b in lst[:-1]:
        acc = acc + str(b) + ", "
    return acc + str(lst[-1])



#reddit initialize
reddit = praw.Reddit(client_id='5FvloSDXtBoP-Q',
                     client_secret='v6xhOeAhVb4CJSkTe6sldNT8j5E',
                     password='2K04uNpgBJG9',
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True


def getPosts(sub,n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day',limit=n):
        main += [[submission.title,submission.url]]
    return main




# class MyClient(discord.Client):
@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)

# async def on_message(self, message):
#     # don't respond to ourselves
#     if message.author == self.user:
#         return

#     if message.content == 'ping':
#         await message.channel.send('pong')
# @bot.event
# async def on_message(self,message):
#     if message.content.startswith('$amumu'):
#         channel = message.channel
#         await channel.send('Hi, wanna be friends!')

#         def check(m):
#             return m.content == 'hello' and m.channel == channel

#         msg = await client.wait_for('message', check=check)
#         await channel.send('Hello {.author}!'.format(msg))



"""
help(ctx) provides a list of all commands except the hidden ones lol
"""
@bot.command()
async def helpme(ctx,arg):
    if arg == "":
        await ctx.send("""!whatgame: takes in a list of games then randomly picks one and returns it 
        !again:  rerolls the previous whatgame operation 
        !coin:  flips a coin. 
        !goldmine:  leads you to the city of gold 
        !bl3 : is a function that @'s all owners of Borderlands 3 that I remembered to add
        !headshot provides a headshot of the great god's face 
        !glenoku is exactly what you think it is 
        !timer time is takes in time in units of minutes, in decimal form (i.e 10.0 instead of 10)
        !maketeams: Divides list into random teams of size n 
        !joined prints when the user first joined the server.
        !getreddit gets top n posts of given subreddit
        !poll: creates a strawpoll
        For specific syntax do !helpme <command>
        """)
    elif arg == "whatgame":
        await ctx.send("""
        !whatgame <elt1, elt2, elt3,...>
        """)
    elif arg == "again":
        await ctx.send("""
        !again | No parameters taken
        """)
    elif arg == "coin":
        await ctx.send("""
        !coin | No parameters taken
        """)
    elif arg == "goldmine":
        await ctx.send("""
        !goldmine | No parameters taken
        """)
    elif arg == "bl3":
        await ctx.send("""
        !bl3 | No parameters taken
        """)
    elif arg == "glenoku":
        await ctx.send("""
        !glenoku | No parameters taken
        """)
    elif arg == "timer":
        await ctx.send("""
        !timer time | time must be a decimal number, i.e. 5.0,12.0. It cannot be an integer, i.e 1 or 3.
        """)
    elif arg == "maketeams":
        await ctx.send("""
        !maketeams n <elt1, elt2, elt3,...> |  Divides list into random teams of size n 
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
"""
whatgame(ctx,*args) takes in a list of games then randomly picks one and returns it
"""
@bot.command()
async def whatgame(ctx, *args):
    acc = []
    for v in args:
        acc.append(v)
    cmplist(acc)
    game = random.choice(acc) 
    await ctx.send('How about ' + game + '?')


"""
maketeams(ctx,n,*args) divides people into teams of size n 
"""
@bot.command()
async def maketeams(ctx, n,*args):
    acc = []
    for v in args:
        acc.append(v)
#
    if int(n) <= 0 or len(acc) < int(n):
        await ctx.send("Not enough slots")
        return

    random.shuffle(acc)
    teams = chunkIt(acc, n)
    i=1
    t = False
    finalteams="Teams:" + '\n'
    for team in teams:
        tem = prettylist(team)
        if not(t): 
            finalteams += "Team " + str(i) + ": " + tem
            t = True
            i+=1
        else:
            finalteams += '\n' + "Team " + str(i) + ": " + tem
            i += 1
        
    await ctx.send(finalteams)




"""
again(ctx) rerolls the previous whatgame operation
"""
@bot.command()
async def again(ctx):
    game = random.choice(globlist) 
    await ctx.send('Maybe ' + game + ' is better?')


"""
coin(ctx) flips a coin.
"""
@bot.command()
async def coin(ctx):
    acc = ["Heads","Tails"]
    game = random.choice(acc) 
    await ctx.send(game)

"""
goldmine(ctx) is a hidden command that leads you to Eldorado
"""
@bot.command()
async def goldmine(ctx):
    await ctx.send('You\'ve found it ' + 'https://www.youtube.com/user/Rayzor324/videos?view_as=subscriber')

"""
usual(ctx) is a deprecated function that performs whatgame(ctx,*args) on an already generated list, that should
contain games frequented.
"""
@bot.command()
async def usual(ctx):
    acc = ["Smite","League"]
    game = random.choice(acc) 
    await ctx.send('How about ' + game + '?')

"""
bl3(ctx) is a function that @'s all owners of Borderlands 3
"""
@bot.command()
async def bl3(ctx):
    await ctx.send('Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269>')



"""
headshot(ctx) provides a headshot of the great god's face
"""
@bot.command()
async def headshot(ctx):
    channel = ctx.message.channel
    await channel.send(file=discord.File('AmumuSquare.png'))

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
glenoku(ctx) is  exactly what you think it is
"""
@bot.command()
async def glenoku(ctx):
    await ctx.send('https://www.youtube.com/watch?v=D7c7ywgWnAY')



"""
glenoku2(ctx) is a hidden comma
"""
@bot.command()
async def glenoku2(ctx):
    await ctx.send('In the works')

"""
timer(ctx,time) is takes in time in units of minutes
"""
@bot.command()
async def timer(ctx,numero: float):
    await ctx.send("The timer has started")
    t_end = time.time() + 60 * numero
    while time.time() < t_end:
       if t_end <= 0:
            break
    await ctx.send(str(numero) + ' minutes have passed.')
    

"""
redditcheck(ctx) checks if reddit is working
"""
@bot.command()
async def redditcheck(ctx):
    print(reddit.user.me())
    await ctx.send(reddit.user.me())

"""
getreddit(ctx,sub,n) gets top n posts of subreddit
"""
@bot.command()
async def getreddit(ctx,sub,n):
    main = getPosts(sub,int(n))
    for submis in main:
        await ctx.send(submis[0] + '\n' + submis[1] + '\n')

  


# """
# redditcheck(ctx) checks if reddit is working
# """
# @bot.command()
# async def redditcheck(ctx):
#     print(reddit.user.me())
#     await ctx.send(reddit.user.me())







@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
async def yt(ctx,url):
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()


    player = await voice_client.create_ytdl_player(url)
    player.start()

@bot.command()
async def poll(ctx, name, *args):
    acc = []
    for v in args:
        acc.append(v)

    polley = {
        "title": name,
        "options": acc,
        "multi": True
    }

    body = json.dumps(polley)
    myurl = "https://www.strawpoll.me/api/v2/polls"
    r = requests.post(url = myurl, data = body)

    dic = r.json()
    await ctx.send('https://www.strawpoll.me/' + str(dic['id']))

"""
joined(ctx,member) prints when user first joined the server.
"""
@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} joined on {0.joined_at}'.format(member))




bot.run('NjM2NDQxOTc4NDY4NDMzOTMy.XbNRZw.fUhKjBJWfoOdX7KEzvlwyjfEECc')