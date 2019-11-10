import discord, asyncio, time, praw, requests, json, urllib.request, youtube_dl, textwrap, requests.exceptions, \
     moviepy.editor as mp, os, config,platform
from discord.ext import commands
from bs4 import BeautifulSoup

# reddit initialize
reddit = praw.Reddit(client_id=config.config["redditClientID"],
                     client_secret=config.config['redditClientSecret'],
                     password=config.config["redditPass"],
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True

######YOUTUBE
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'musicMu/%(extractor)s-%(id)s-%(title)s.mp4',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.20):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=False, aliases=['joinA'])
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(pass_context=True, aliases=['playA'])
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        plat = platform.system()
        if ('Darwin' == plat):
            os.chdir('/Users/brandonjoseph/Music/iTunes/iTunes Media/Music')
        else:
            a = 'figure out later'
        print(os.getcwd())
        print(plat)



        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(os.getcwd() + query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command(pass_context=True, aliases=['ytA'])
    async def yt(self, ctx, *, url):
        """Downloads and plays from a url """

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command(pass_context=True, aliases=['streamA'])
    async def stream(self, ctx, *, url):
        """Streams from a url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def twit(self, ctx, *, url):
        """Plays video from twitter directly (works on almost all media)"""
        await ctx.send("Working...")
        try:

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ext = [".mp4",".m4a"]
            files = [x for x in os.listdir(os.getcwd() + '/musicMu') if x.endswith(tuple(ext))]
            print(files)
            os.chdir('musicMu/')
            latest_file = max(files, key=os.path.getctime)
          #  os.chdir('..')
            print(latest_file)


            statinfo = os.stat(latest_file).st_size
            if (statinfo <= 8000000):
                await ctx.send(file=discord.File(latest_file))
                return
            # clip_resized = clip.resize(height=360)  # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
            clip = mp.VideoFileClip(latest_file)
            clip.write_videofile("movie_resized.mp4", bitrate="200k")

            await ctx.send(file=discord.File("movie_resized.mp4"))
        except:
             await ctx.send("Bad link")

    @commands.command(pass_context=True, aliases=['ytsearchA'])
    async def ytsearch(self, ctx, *, url):
        """Search for youtube video to play in VC"""
        textToSearch = url
        query = urllib.parse.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
            url = 'https://www.youtube.com' + vid['href']
            break
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    """
    redv(ctx,post) gets reddit video from post
    """

    @commands.command()
    async def redv(self, ctx, *, url):
        """Gets reddit video from post"""
        post_id = reddit.submission(url=url)
        submission = reddit.submission(id=post_id)
        url = submission.url
        await ctx.send("Working...")
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        ext = [".mp4",".m4a"]
        files = [x for x in os.listdir(os.getcwd()) if x.endswith(tuple(ext))]
        os.chdir('musicMu/')
        latest_file = max(files, key=os.path.getctime)
        print(latest_file)

        statinfo = os.stat(latest_file).st_size
        if (statinfo <= 8000000):
            await ctx.send("Title: " + submission.title)
            await ctx.send(file=discord.File(latest_file))
            return
        clip = mp.VideoFileClip(latest_file)
        clip.write_videofile("movie_resized.mp4", bitrate="200k")

        await ctx.send("Title: " + submission.title)
        await ctx.send(file=discord.File("movie_resized.mp4"))

    @commands.command()
    async def playlast(self, ctx):
        """Play last downloaded video (yt or play)"""

        ext = [".mp4", ".m4a"]
        files = [x for x in os.listdir(os.getcwd() + '/musicMu' ) if x.endswith(tuple(ext))]
        os.chdir('musicMu/')
        query = 'musicMu/' + max(files, key=os.path.getctime)
        os.chdir('..')
        print(query)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))






    @commands.command(pass_context=True, aliases=['volumeA'])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command(pass_context=True, aliases=['leave'])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    @ytsearch.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


#####YOUTUBE