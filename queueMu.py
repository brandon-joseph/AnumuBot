"""
Base of this file was made by someone else
"""
import discord
from discord.ext import commands

import asyncio
import itertools,random
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
import os


ytdlopts = {
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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes-
}

ffmpegopts = {
  #  'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=True):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```', delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

####




    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)

#---------------
    @classmethod
    async def create_local(cls, ctx, data, source, loop):
        loop = loop or asyncio.get_event_loop()

        return cls(source, data=data, requester=ctx.author)



class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .8
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` added by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Queue(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='join', aliases=['j','joinA'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice channel
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

    #    await ctx.send(f'Connected to: **{channel}**', delete_after=20)

    @commands.command(name='play', aliases=['playA','yt','ytsearch','p'])
    async def play_(self, ctx, *, search: str):
        """Add song to queue to the queue
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=True)

        await player.queue.put(source)

    @commands.command(name='pause', aliases=['pauseA','halt'])
    async def pause_(self, ctx):
        """Pause the current playing song"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('Not playing anything', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: paused the song')

    @commands.command(name='resume',aliases=['resumeA'])
    async def resume_(self, ctx):
        """Resume current paused song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not playing anything', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: resumed the song')

    @commands.command(name='skip',aliases=['skipA','jump'])
    async def skip_(self, ctx):
        """Skip current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not playing anything', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: skipped')

    @commands.command(name='queue', aliases=['q', 'playlist','queueA'])
    async def queue_info(self, ctx):
        """View queue"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not in a voice chat', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('Queue\'s empty bud')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(name='current', aliases=['np', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        """Information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not in a voice chat', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('Not playing anything')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'*Playing:** `{vc.source.title}` '
                                   f'added by `{vc.source.requester}`')

    @commands.command(name='vol', aliases=['volume','volumeA'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the volume
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not in a voice chat', delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: set the volume to **{vol}%**')

    @commands.command(name='stop',aliases=['lq','stopA','leave'])
    async def stop_(self, ctx):
        """Stop song and clear queue
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Not playing anything', delete_after=20)

        await self.cleanup(ctx.guild)




    @commands.command()
    async def persona(self, ctx):
        """Plays persona playlist
        """
        await ctx.trigger_typing()


        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        songs = []

        root = "/Users/brandonjoseph/Music/iTunes/iTunes Media/Music/Various Artists/PERSONA5 ORIGINAL SOUNDTRACK"
        for path, subdirs, files in os.walk(root):
            for name in files:
                sourcesub = discord.FFmpegPCMAudio(os.path.join(path, name))

                source = await YTDLSource.create_local(ctx,todatum(str(name)),sourcesub,loop=self.bot.loop)
                songs.append(source)


        random.shuffle(songs)

        for song in songs:
            await player.queue.put(song)



def todatum(name):
    data = {'_type': 'playlist', 'entries': [{'id': 'BWWfjK0v8eM', 'uploader': 'DeoxysPrime', 'uploader_id': 'DeoxysPrimeX2', 'uploader_url': 'http://www.youtube.com/user/DeoxysPrimeX2', 'channel_id': 'UCubokaJqWnfPdVpFw_G_Q2w', 'channel_url': 'http://www.youtube.com/channel/UCubokaJqWnfPdVpFw_G_Q2w', 'upload_date': '20130326', 'license': name, 'creator': name, 'title': name, 'alt_title': name, 'thumbnail': 'https://i.ytimg.com/vi/BWWfjK0v8eM/maxresdefault.jpg', 'description': 'Game: Sonic the Hedgehog (2006)\nMusic: His World (Theme of Sonic)', 'categories': ['Gaming'], 'tags': ['Sonic the Hedgehog', '2006', 'Sonic 06', 'OST', 'music', 'soundtrack', 'His World', 'Main Theme', 'Theme of Sonic'], 'subtitles': {}, 'automatic_captions': {}, 'duration': 278, 'age_limit': 0, 'annotations': None, 'chapters': None, 'webpage_url': 'none', 'view_count': 3534920, 'like_count': 37410, 'dislike_count': 645, 'average_rating': 4.9322033, 'formats': [{'format_id': '249', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=249&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=audio%2Fwebm&gir=yes&clen=1613549&dur=277.561&lmt=1543603720668114&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5511222&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhAOcl6zJyRa9l2JNekfHxD5JbQzoZlHBb1UmajtnQCPnnAiEA9w950kxIr7WTQOvwoSqa1JSWkEjMmg8zXidJg08HimQ%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'format_note': 'tiny', 'acodec': 'opus', 'abr': 50, 'asr': 48000, 'filesize': 1613549, 'fps': None, 'height': None, 'tbr': 48.159, 'width': None, 'vcodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '249 - audio only (tiny)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '250', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=250&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=audio%2Fwebm&gir=yes&clen=2138886&dur=277.561&lmt=1543603700763941&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5511222&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIgb4HKIHCHUq93jJpC3KFoXkrmb4AeGv6m7oaN6Oshll8CIQCu7EzCUe3K477ESxqP-Rm4Kd6l07dnyu5w4ihC37m--A%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'format_note': 'tiny', 'acodec': 'opus', 'abr': 70, 'asr': 48000, 'filesize': 2138886, 'fps': None, 'height': None, 'tbr': 63.862, 'width': None, 'vcodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '250 - audio only (tiny)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '251', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=251&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=audio%2Fwebm&gir=yes&clen=4257760&dur=277.561&lmt=1543603699681358&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5511222&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAK8kO7uW4aK9EVwzJ21XIRJYGUS50CCICKaMp4ehsG9-AiB0OK0c2VX9a9r_yHyZEjBbg02Wc5LACc_qUNzFyAfQuw%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'format_note': 'tiny', 'acodec': 'opus', 'abr': 160, 'asr': 48000, 'filesize': 4257760, 'fps': None, 'height': None, 'tbr': 126.741, 'width': None, 'vcodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '251 - audio only (tiny)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '140', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=140&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=audio%2Fmp4&gir=yes&clen=4493268&dur=277.594&lmt=1543598302474707&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgW2t6NsgCPbukq82CB6TrhJsCZsZ8aj9fukhzDLc_1r4CICqIXeGsomuhQb-3jvjQOSyNCtFMr7nAVhHyY8PZLuWL&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'm4a', 'format_note': 'tiny', 'acodec': 'mp4a.40.2', 'abr': 128, 'container': 'm4a_dash', 'asr': 44100, 'filesize': 4493268, 'fps': None, 'height': None, 'tbr': 130.649, 'width': None, 'vcodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '140 - audio only (tiny)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '160', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=160&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=516989&dur=277.458&lmt=1543600809029057&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhALPWr-pkJF-xiEvXSbqUwpaGLGtxE6W40DsDNA-YalFKAiEAvxx3eVyfZQ4CaaWX2N_w5tMEyG45JkLV8BpLmwHRYNU%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'mp4', 'height': 144, 'format_note': '144p', 'vcodec': 'avc1.4d400c', 'asr': None, 'filesize': 516989, 'fps': 24, 'tbr': 17.749, 'width': 256, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '160 - 256x144 (144p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '133', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=133&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=877531&dur=277.458&lmt=1543600634858693&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAO5IKYz0fxmxYft87iT3KplpodJJLBCs1Igw7vuv6XCTAiAy-8IJNN6RmL_KJFwYptAtbbChAu-AR9HpiPEGzP8E3w%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'mp4', 'height': 240, 'format_note': '240p', 'vcodec': 'avc1.4d4015', 'asr': None, 'filesize': 877531, 'fps': 24, 'tbr': 27.817, 'width': 426, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '133 - 426x240 (240p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '278', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=278&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fwebm&gir=yes&clen=1389594&dur=277.458&lmt=1543602420044509&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhAMZn2BG6jvpztKKE_VOZ0_-I0bCuKsm7a7mJPZSQERmnAiEA7-oP7Eoh5GxPoS0Wemy-k-7iyZZDVoDBZmZU5-2F1FY%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'height': 144, 'format_note': '144p', 'container': 'webm', 'vcodec': 'vp9', 'asr': None, 'filesize': 1389594, 'fps': 24, 'tbr': 41.399, 'width': 256, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '278 - 256x144 (144p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '394', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=394&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=1453895&dur=277.458&lmt=1556945487998446&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5532432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhANwNjOBbsx2URuJ_s2R9X6bcB6uBKpbpGoYWjqhowRKVAiBqfJpfEl9klsReMeUYEwdjWq6WGBNhVRUFW7lF-ecM1Q%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'acodec': 'none', 'vcodec': 'av01.0.00M.08', 'asr': None, 'filesize': 1453895, 'format_note': '144p', 'fps': 24, 'height': 144, 'tbr': 43.723, 'width': 256, 'ext': 'mp4', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '394 - 256x144 (144p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '395', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=395&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=1865506&dur=277.458&lmt=1556945517037325&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5532432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgATpsvjbs4-54PfgJ6bftCVCqtUrZ6vDuZwlsy_k05vECIHyEk7pccSdxna4845nG713XExEzIaRnJUXqQHLZZA8x&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'acodec': 'none', 'vcodec': 'av01.0.00M.08', 'asr': None, 'filesize': 1865506, 'format_note': '240p', 'fps': 24, 'height': 240, 'tbr': 54.511, 'width': 426, 'ext': 'mp4', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '395 - 426x240 (240p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '134', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=134&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=1630076&dur=277.458&lmt=1543600614208068&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhAL0QFtNZyAwin1vPG-Nix6Y1wv-RFoTOSGfOM2-XMpatAiEAtIZ9MGrAmDoVQeg87fmwOAh5MNBQ3hTj6dyiORZKEuY%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'mp4', 'height': 360, 'format_note': '360p', 'vcodec': 'avc1.4d401e', 'asr': None, 'filesize': 1630076, 'fps': 24, 'tbr': 57.042, 'width': 640, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '134 - 640x360 (360p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '242', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=242&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fwebm&gir=yes&clen=2128229&dur=277.458&lmt=1543602190149419&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhALX1btiSjT6sUluzYVzZhcp5ggCmgaCKNwMJnB7mVPMUAiA4EOV0wCjLfRPxaV3QoxVBGNOJJ7BM8bkLebJ7Y7zv9Q%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'height': 240, 'format_note': '240p', 'vcodec': 'vp9', 'asr': None, 'filesize': 2128229, 'fps': 24, 'tbr': 61.974, 'width': 426, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '242 - 426x240 (240p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '396', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=396&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=3164138&dur=277.458&lmt=1556945544292273&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5532432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIhAIrYuzfqd_YI6t1Fld01he4Ww4Cyefa0traabtYQJdogAiAVBZPQbCbI2WkV6mWMuoSIgN57cebYuf_NHLxxTw046w%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'acodec': 'none', 'vcodec': 'av01.0.01M.08', 'asr': None, 'filesize': 3164138, 'format_note': '360p', 'fps': 24, 'height': 360, 'tbr': 91.475, 'width': 640, 'ext': 'mp4', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '396 - 640x360 (360p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '135', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=135&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=2743751&dur=277.458&lmt=1543600606155484&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIgG1jLRYy5bk6GI1b51dwganpNdmnLvNwb_oIk5EaVUVMCIQDnPmBZruXbjB0OvTsH51xrWzfqRCKq4PYFzZDOGnDqVg%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'mp4', 'height': 480, 'format_note': '480p', 'vcodec': 'avc1.4d401e', 'asr': None, 'filesize': 2743751, 'fps': 24, 'tbr': 96.609, 'width': 854, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '135 - 854x480 (480p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '244', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=244&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fwebm&gir=yes&clen=3734578&dur=277.458&lmt=1543601877742394&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhAI7pupmyNNsDyeS9ObNQfemJ6ggM3GvrbP5ZXoHXFYQ0AiEA6S3zI7m3A_4e7PwxCOJvHBTf1kVJgEC19mZHPzIZInk%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'height': 480, 'format_note': '480p', 'vcodec': 'vp9', 'asr': None, 'filesize': 3734578, 'fps': 24, 'tbr': 108.06, 'width': 854, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '244 - 854x480 (480p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '243', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=243&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fwebm&gir=yes&clen=3805165&dur=277.458&lmt=1543602569306355&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgTXx5vUBCDb_pL1xstSmW6G4XrAqQiYRkXZhB8bMTWOICIFN8dx8DUFR7RtcsWk9O8CKXaMwY7aS0ldZiLPVw9aFM&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'height': 360, 'format_note': '360p', 'vcodec': 'vp9', 'asr': None, 'filesize': 3805165, 'fps': 24, 'tbr': 118.219, 'width': 640, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '243 - 640x360 (360p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '397', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=397&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=4887593&dur=277.458&lmt=1556945606455418&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5532432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRQIgU3cST2LAap658VrPfRRvQ2Ya6gH_x2xO2IQiVaEKoAsCIQDzEq9UY_GIKj_qWHfyioVWWil1yZ-Y5g_4i-rU52rVoA%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'acodec': 'none', 'vcodec': 'av01.0.04M.08', 'asr': None, 'filesize': 4887593, 'format_note': '480p', 'fps': 24, 'height': 480, 'tbr': 143.341, 'width': 854, 'ext': 'mp4', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '397 - 854x480 (480p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '136', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=136&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=4847872&dur=277.458&lmt=1543601841424107&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgL0N2QXQgraAUd9au2nBA42EWP4a5u_QXaKvxB0yMzjsCIHewu7-nQ1_tixSJD5sB9Gy3XRSVT7AfaG_rENoUegJG&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'mp4', 'height': 720, 'format_note': '720p', 'vcodec': 'avc1.4d401f', 'asr': None, 'filesize': 4847872, 'fps': 24, 'tbr': 187.082, 'width': 1280, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '136 - 1280x720 (720p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '398', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=398&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=9887834&dur=277.458&lmt=1556945844373114&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5532432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgSOmbldkPhwCK-EzQxPARinbBd-sErCSJBo_zUt15qN8CIDdtO8M4fN2ShfN34d4bhpmJ0vyYEnvoUd6yV25mW2OS&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'asr': None, 'filesize': 9887834, 'format_note': '720p', 'fps': 24, 'height': 720, 'tbr': 285.814, 'width': 1280, 'ext': 'mp4', 'vcodec': 'av01.0.05M.08', 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '398 - 1280x720 (720p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '247', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=247&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C394%2C395%2C396%2C397%2C398&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fwebm&gir=yes&clen=8568083&dur=277.458&lmt=1543602606931530&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRgIhAPNsRLCNQ649KjepBAcsd-qs8wVEgf7cE6bovhsshW5jAiEA3mjsKLxOhVh7JTOnMsKExBAKNYXemS9nqdQl3Jhf6Mg%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'webm', 'height': 720, 'format_note': '720p', 'vcodec': 'vp9', 'asr': None, 'filesize': 8568083, 'fps': 24, 'tbr': 341.538, 'width': 1280, 'acodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '247 - 1280x720 (720p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'format_id': '18', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=18&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=video%2Fmp4&gir=yes&clen=9015170&ratebypass=yes&dur=277.594&lmt=1543595824681231&mt=1576454621&fvip=5&fexp=23842630&c=WEB&txp=5531432&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=ALgxI2wwRQIgCEpdnRe1OlRCkRQhMf2kXTSoAg63K4KDPJObNtBPzT8CIQDHop_8ZTgPrLx7zsHOdtCb3FdaAL0Nbp69uoFLGrBJYA%3D%3D&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a', 'player_url': None, 'ext': 'mp4', 'width': 640, 'height': 360, 'acodec': 'mp4a.40.2', 'abr': 96, 'vcodec': 'avc1.42001E', 'asr': 44100, 'filesize': 9015170, 'format_note': '360p', 'fps': None, 'tbr': 259.936, 'format': '18 - 640x360 (360p)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'is_live': None, 'start_time': None, 'end_time': None, 'series': None, 'season_number': None, 'episode_number': None, 'track': None, 'artist': None, 'album': None, 'release_date': None, 'release_year': None, 'extractor': 'youtube', 'webpage_url_basename': 'BWWfjK0v8eM', 'extractor_key': 'Youtube', 'n_entries': 1, 'playlist': 'his world', 'playlist_id': 'his world', 'playlist_title': None, 'playlist_uploader': None, 'playlist_uploader_id': None, 'playlist_index': 1, 'thumbnails': [{'url': 'https://i.ytimg.com/vi/BWWfjK0v8eM/maxresdefault.jpg', 'id': '0'}], 'display_id': 'BWWfjK0v8eM', 'requested_subtitles': None, 'format_id': '140', 'url': 'https://r1---sn-4pgnuapbiu-5ace.googlevideo.com/videoplayback?expire=1576476360&ei=aMr2XfKoEYLYhgbfsbyIBQ&ip=128.84.127.21&id=o-AL6buBea1fZS1U-2c--lVKWyFSSb9fS7rOJBwOJV0iuk&itag=140&source=youtube&requiressl=yes&mm=31%2C29&mn=sn-4pgnuapbiu-5ace%2Csn-ab5sznle&ms=au%2Crdu&mv=m&mvi=0&pl=20&initcwndbps=3210000&mime=audio%2Fmp4&gir=yes&clen=4493268&dur=277.594&lmt=1543598302474707&mt=1576454621&fvip=5&keepalive=yes&fexp=23842630&c=WEB&txp=5533432&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=ALgxI2wwRAIgW2t6NsgCPbukq82CB6TrhJsCZsZ8aj9fukhzDLc_1r4CICqIXeGsomuhQb-3jvjQOSyNCtFMr7nAVhHyY8PZLuWL&lsparams=mm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AHylml4wRAIgGNXcTYMsE3hVGhfMyd2dX8f0agPnA-HH0DpB3C3M848CIAqnvcFaSO6HBJ_50s8rv4vA-IVu29m9FGNq01adGX_a&ratebypass=yes', 'player_url': None, 'ext': 'm4a', 'format_note': 'tiny', 'acodec': 'mp4a.40.2', 'abr': 128, 'container': 'm4a_dash', 'asr': 44100, 'filesize': 4493268, 'fps': None, 'height': None, 'tbr': 130.649, 'width': None, 'vcodec': 'none', 'downloader_options': {'http_chunk_size': 10485760}, 'format': '140 - audio only (tiny)', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.89 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'id': 'his world', 'extractor': 'youtube:search', 'webpage_url': 'ytsearch:his world', 'webpage_url_basename': 'his world', 'extractor_key': 'YoutubeSearch'}
    data['title'] = name[:-4]
    return data

def setup(bot):
    bot.add_cog(Queue(bot))