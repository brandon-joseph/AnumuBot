import discord,requests,cv2, config,os
from discord.ext import commands
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
import urllib.request as req
from urllib.parse import urlparse
import textwrap

from imgurpython import ImgurClient

client = ImgurClient(config.config['imgurClient'], config.config['imgurSecret'])

class imageMu(commands.Cog):
    @commands.command(hidden=True,enabled=False)
    async def rmBG(self,ctx):
        # == Parameters
        BLUR = 21
        CANNY_THRESH_1 = 10
        CANNY_THRESH_2 = 100
        MASK_DILATE_ITER = 10
        MASK_ERODE_ITER = 10
        MASK_COLOR = (0.0, 0.0, 1.0)  # In BGR format




        # -- Read image
        img = cv2.imread('imageMu/test.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # -- Edge detection
        edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
        edges = cv2.dilate(edges, None)
        edges = cv2.erode(edges, None)

        # -- Find contours in edges, sort by area
        contour_info = []

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        max_contour = contour_info[0]

        # -- Create empty mask, draw filled polygon on it corresponding to largest contour ----
        # Mask is black, polygon is white
        mask = np.zeros(edges.shape)
        for c in contour_info:
            cv2.fillConvexPoly(mask, c[0], (255))

        # -- Smooth mask, then blur it
        mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        mask_stack = np.dstack([mask] * 3)  # Create 3-channel alpha mask

        # -- Blend masked img into MASK_COLOR background
        mask_stack = mask_stack.astype('float32') / 255.0
        img = img.astype('float32') / 255.0
        masked = (mask_stack * img) + ((1 - mask_stack) * MASK_COLOR)
        masked = (masked * 255).astype('uint8')

        cv2.imshow('img', masked)  # Display
        cv2.waitKey()
        cv2.imwrite("imageMu/test.png", masked)
        await ctx.send(file=discord.File("imageMu/test.png"))

    @commands.command()
    async def emoji(self,ctx, url):
        """resizes url-based image to emoji dimensions"""
        a = urlparse(url)  #
        req.urlretrieve(url, "imageMu/" + os.path.basename(a.path))
        img = Image.open("imageMu/" + os.path.basename(a.path))
        new_img = img.resize((128, 128))
        path = "imageMu/resized" + os.path.basename(a.path)
        if not path.endswith('.png') and not path.endswith('.jpg'):
            path += '.png'
        new_img.save(path, "PNG", optimize=True)
        os.remove("imageMu/" + os.path.basename(a.path))
        b = client.upload_from_path(path, config=None, anon=True)
        await ctx.send(b['link'])
        #await ctx.send(file=discord.File(path))


    @commands.command(hidden=True)
    async def circle(self,ctx,url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        #img = Image.open("dog.jpg").convert("RGB")
        npImage = np.array(img)
        h, w = img.size

        # Create same size alpha layer with circle
        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, h, w], 0, 360, fill=255)

        # Convert alpha Image to numpy array
        npAlpha = np.array(alpha)

        # Add alpha layer to RGB
        npImage = np.dstack((npImage, npAlpha))

        # Save with alpha
        Image.fromarray(npImage).save('imageMu/result.png')
        b = client.upload_from_path('imageMu/result.png', config=None, anon=True)
        await ctx.send(b['link'])
        #!await ctx.send(file=discord.File('imageMu/result.png'))

    @commands.command(hidden=True)
    async def testimgur(self,ctx):
        # Example request
        items = client.gallery()
        for item in items:
            print(item.link)


    @commands.command(hidden=True)
    async def imgur(self,ctx):
       a =  client.upload_from_path('imageMu/AmumuSquare.png', config=None, anon=True)
       print(a['link'])


    @commands.command(hidden=True)
    async def testimage(self,ctx):
        message = ctx.message
        channel = message.channel
        try:
            name = message.attachments[0].filename
        except:
            name = ""

        #url = message.attachments[0].url
        print(message.attachments)


            # await message.attachments[0].save('musicMu/run.mp3')
            # print('made it')
            # source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(os.getcwd() + '/musicMu/run.mp3'))
            # ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            # await channel.send('Now playing: {}'.format(name))

    @commands.command(hidden=True)
    async def dignity(self,ctx,name, *args):
        action = listToString(args)
        #print(os.getcwd())
        img = Image.open(os.getcwd() + "/imageMu/dignity.png")
        draw = ImageDraw.Draw(img)
        # font = ImageFont.truetype(<font-file>, <font-size>)
        font = ImageFont.truetype("fonts.otf", 32)
        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text((165, 0), name, (0, 0, 0), font=font)
        lines = textwrap.wrap(action, width=8)
        font2 = ImageFont.truetype("fonts.otf", int(32 / len(lines)) * 3)
        y_text = 44
        i = 0
        if len(lines) > 1:
            for line in lines:
                width, height = font.getsize(line)
                if i == len(lines)-1:
                    line = line + "?"
                draw.text((165, y_text), line,  (0, 0, 0), font=font2)
                y_text += int(height/ len(lines)) * 3
                i+=1
        else:
            draw.text((165, 44), action + "?", (0, 0, 0), font=font)
        img.save('./imageMu/' + name + action + ".png")
        await ctx.send(file=discord.File('./imageMu/' + name + action + ".png"))

def listToString(list):
    main = ""
    for item in list:
        main += item + " "
    main = main.strip()
    return main