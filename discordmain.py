import discord
import random
from discord.ext import commands
import asyncio
import strawpoll
from cv2 import cv2
import numpy as np
import time


bot = commands.Bot(command_prefix='!')
globlist = []

def cmplist(list): #Actually this function calls from another function
    global globlist
    if (len(list) > len(globlist)):
        globlist = list[:] #copy all element of list to globlist



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
    

# @bot.event #Deprecated
# async def on_message(message):
#     pic_ext = [".jpg",".png",".jpeg"]
#     await bot.process_commands(message)
#     for ext in pic_ext:
#         if message.content.endswith(ext):
#             # Create a black image
#            # img = np.zeros((512,512,3), np.uint8)
#             img = cv2.imread("./test.jpg")

#             # Write some Text
#             font                   = cv2.FONT_HERSHEY_SIMPLEX
#             bottomLeftCornerOfText = (10,500)
#             fontScale              = 1
#             fontColor              = (255,255,255)
#             lineType               = 2

#             cv2.putText(img,'Hello World!', 
#                 bottomLeftCornerOfText, 
#                 font, 
#                 fontScale,
#                 fontColor,
#                 lineType)

#             #Display the image
#             cv2.imshow("img",img)

#             #Save image
#             cv2.imwrite("out.jpg", img)

#             cv2.waitKey(0)

            
#     channel = message.channel



# @bot.command()
# async def when(self,ctx, *args):


# @bot.command()
# async def poll(ctx, *args):
#     acc = []
#     for v in args:
#         acc.append(v)
#     api = strawpoll.API()

#     # p2 = strawpoll.Poll('Anumu\'s Poll', acc)
#     # p2 = await api.submit_poll(p2)
#     # await ctx.send('Anumu\'s Poll' + p2.url)
#     p2 = strawpoll.Poll('lol?', ['ha', 'haha', 'hahaha', 'hahahaha', 'hahahahaha'])
#     p2 = await api.submit_poll(p2)
#     print(p2.url)

# @bot.command()
# async def usual(ctx):
#     #== Parameters =======================================================================
#     BLUR = 21
#     CANNY_THRESH_1 = 10
#     CANNY_THRESH_2 = 200
#     MASK_DILATE_ITER = 10
#     MASK_ERODE_ITER = 10
#     MASK_COLOR = (0.0,0.0,1.0) # In BGR format


#     #== Processing =======================================================================

#     #-- Read image -----------------------------------------------------------------------
#     img = cv2.imread('C:/Temp/person.jpg')
#     gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#     #-- Edge detection -------------------------------------------------------------------
#     edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
#     edges = cv2.dilate(edges, None)
#     edges = cv2.erode(edges, None)

#     #-- Find contours in edges, sort by area ---------------------------------------------
#     contour_info = []
#     _, contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
#     # Previously, for a previous version of cv2, this line was: 
#     #  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
#     # Thanks to notes from commenters, I've updated the code but left this note
#     for c in contours:
#         contour_info.append((
#             c,
#             cv2.isContourConvex(c),
#             cv2.contourArea(c),
#         ))
#     contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
#     max_contour = contour_info[0]

#     #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
#     # Mask is black, polygon is white
#     mask = np.zeros(edges.shape)
#     cv2.fillConvexPoly(mask, max_contour[0], (255))

#     #-- Smooth mask, then blur it --------------------------------------------------------
#     mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
#     mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
#     mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
#     mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

#     #-- Blend masked img into MASK_COLOR background --------------------------------------
#     mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
#     img         = img.astype('float32') / 255.0                 #  for easy blending

#     masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
#     masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

#     cv2.imshow('img', masked)                                   # Display
#     cv2.waitKey()

#     #cv2.imwrite('C:/Temp/person-masked.jpg', masked)      



# client = MyClient()
# client.run('NjM2NDQxOTc4NDY4NDMzOTMy.Xa_wxw.1QDSkqZzeyNiob_JXhTOG0oL8Ac')
bot.run('NjM2NDQxOTc4NDY4NDMzOTMy.XbJkQA.--caTnUq71sqlQCod3IvEEZ2wsE')