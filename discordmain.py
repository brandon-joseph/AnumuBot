import discord
import random
from discord.ext import commands
import asyncio
import strawpoll
from cv2 import cv2
import numpy as np


bot = commands.Bot(command_prefix='!')

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

@bot.command()
async def whatgame(ctx, *args):
    acc = []
    for v in args:
        acc.append(v)
    game = random.choice(acc) 
    await ctx.send('How about ' + game + '?')

@bot.command()
async def coin(ctx):
    acc = ["Heads","Tails"]
    game = random.choice(acc) 
    await ctx.send(game)

@bot.command()
async def goldmine(ctx):
    await ctx.send('You\'ve found it ' + 'https://www.youtube.com/user/Rayzor324/videos?view_as=subscriber')


@bot.command()
async def usual(ctx):
    acc = ["Smite","League"]
    game = random.choice(acc) 
    await ctx.send('How about ' + game + '?')

@bot.command()
async def bl3(ctx):
    await ctx.send('Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269>')




@bot.command()
async def rtest(ctx):
    channel = ctx.message.channel
    await channel.send(file=discord.File('test.jpg'))









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
bot.run('NjM2NDQxOTc4NDY4NDMzOTMy.Xa_wxw.1QDSkqZzeyNiob_JXhTOG0oL8Ac')