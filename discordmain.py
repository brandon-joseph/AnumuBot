import discord, random, asyncio, time, praw, requests, json, urllib.request, youtube_dl, textwrap, requests.exceptions, \
    twitter, moviepy.editor as mp, os, config
from discord.ext import commands
from bs4 import BeautifulSoup
# import tweepy
# import glob

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
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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
    def __init__(self, source, *, data, volume=0.5):
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


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def twit(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        await ctx.send("Working...")
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        ext = [".mp4",".m4a"]
        files = [x for x in os.listdir(os.getcwd()) if x.endswith(tuple(ext))]
        latest_file = max(files, key=os.path.getctime)
        print(latest_file)


        statinfo = os.stat(latest_file).st_size
        if (statinfo <= 8000000):
            await ctx.send(file=discord.File(latest_file))
            return
        # clip_resized = clip.resize(height=360)  # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
        clip = mp.VideoFileClip(latest_file)
        clip.write_videofile("movie_resized.mp4", bitrate="200k")

        await ctx.send(file=discord.File("movie_resized.mp4"))

    @commands.command()
    async def ytsearch(self, ctx, *, url):
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
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    """
    redv(ctx,post) gets reddit video from post
    """

    @commands.command()
    async def redv(self, ctx, *, url):
        post_id = reddit.submission(url=url)
        submission = reddit.submission(id=post_id)
        url = submission.url
        await ctx.send("Working...")
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        ext = [".mp4",".m4a"]
        files = [x for x in os.listdir(os.getcwd()) if x.endswith(tuple(ext))]
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
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
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


bot = commands.Bot(command_prefix='!',
                   description='Anumu has many many many features, too many to list so I only listed some.')
globlist = []


def cmplist(list):  # Actually this function calls from another function
    global globlist
    if (len(list) > len(globlist)):
        globlist = list[:]  # copy all element of list to globlist


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


def getPosts(sub, n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day', limit=n):
        if submission.is_self:
            main += [[submission.title, submission.selftext]]
        else:
            main += [[submission.title, submission.url]]
    return main


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
    if arg == "":
        await ctx.send(textwrap.dedent("""
        
        >>> **!whatgame: takes in a list of games then randomly picks one and returns it 
        !again: rerolls the previous whatgame operation 
        !coin: flips a coin. 
        !goldmine:  leads you to the city of gold 
        !bl3 : is a function that @'s all owners of Borderlands 3 that I remembered to add
        !weebs: notifies weebs
        !headshot: provides a headshot of the great god's face 
        !glenoku: is exactly what you think it is 
        !timer: time is taken in time in units of minutes | WARNING: Can't use other functions while timer runs
        !maketeams: Divides list into random teams of size n 
        !joined: prints when the user first joined the server.
        !getreddit: gets top n posts of given subreddit
        !poll: creates a strawpoll
        !yt: Plays a youtube video | !volume,!stop,!play,!join all supported
        !ytsearch: Searches and plays top rated youtube video 
        !stream: Same as yt but doesn't predownload so prolly should use this
        !firstmsg: gets date of first message and gives clickable link!
        !whatanime: gets name of anime and episode from gif or image
        !opgg: gets an accounts op.gg
        !twit: gets video of twitter post and sends it to channel, also works on twitch clips, prolly more
        !redv: gets reddit video from post**


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
        !maketeams <n> <elt1, elt2, elt3,...> |  Divides list into random teams of size n 
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
    elif arg == "whatanime":
        await ctx.send("""
        !whatanime <url.jpg/png> | Gives information on what anime picture is from
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
async def maketeams(ctx, n, *args):
    acc = []
    for v in args:
        acc.append(v)
    #
    if int(n) <= 0 or len(acc) < int(n):
        await ctx.send("Not enough slots")
        return

    random.shuffle(acc)
    teams = chunkIt(acc, n)
    i = 1
    t = False
    finalteams = "Teams:" + '\n'
    for team in teams:
        tem = prettylist(team)
        if not (t):
            finalteams += "Team " + str(i) + ": " + tem
            t = True
            i += 1
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
    acc = ["Heads", "Tails"]
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
    acc = ["Smite", "League"]
    game = random.choice(acc)
    await ctx.send('How about ' + game + '?')


"""
bl3(ctx) is a function that @'s all owners of Borderlands 3
"""


@bot.command()
async def bl3(ctx):
    await ctx.send(
        'Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269>')


"""
animegang(ctx) is a function that @'s weebs
"""


@bot.command()
async def weebs(ctx):
    await ctx.send(
        'Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269> <@328215412007370762><@191267028454080513><@187745555273744384>')


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
async def timer(ctx, numero: float):
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
async def getreddit(ctx, sub, n):
    main = getPosts(sub, int(n))
    for submis in main:
        await ctx.send(submis[0] + '\n' + submis[1] + '\n\n')


# redditcheck(ctx) checks if reddit is working
# """
# @bot.command()
# async def redditcheck(ctx):
#     print(reddit.user.me())
#     await ctx.send(reddit.user.me())


"""
poll(ctx,name,args) creates poll
"""


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
    r = requests.post(url=myurl, data=body)

    dic = r.json()
    await ctx.send('https://www.strawpoll.me/' + str(dic['id']))


"""
whatanime(ctx, url) finds name of anime using trace.moe API
https://soruly.github.io/trace.moe/#/
"""


@bot.command()
async def whatanime(ctx, url):
    try:
        r = requests.get("https://trace.moe/api/search?url=" + url)
        r.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        await ctx.send("Server down")
    except requests.exceptions.HTTPError:
        await ctx.send("4xx, 5xx error")
    else:
        result = r.json()
        docs = (result['docs'])[0]
        title = docs['title_english']
        mal_id = docs['mal_id']
        mal = "https://myanimelist.net/anime/" + str(mal_id)
        ep = docs['episode']
        sim = docs["similarity"]
        await ctx.send("""Title: {title}
        Episode: {ep}
        Similarity: {similarity}
        Mal:  {mal}""".format(title=title, ep=ep, similarity=sim, mal=mal))


#######LEAGUE BLOCK

def listToString(list):
    main = ""
    for item in list:
        main += item + " "
    main = main.strip()
    return main


"""
opgg(ctx,name) gets name's op.gg, assuming they're on NA
"""


@bot.command()
async def opgg(ctx, *args):
    name = listToString(args)
    newstring = (str(name)).replace(" ", "+")
    url = "https://na.op.gg/summoner/userName=" + newstring
    r = requests.get(url)
    if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
        await ctx.send("User doesn't exist probably maybe")
    else:
        await ctx.send("https://na.op.gg/summoner/userName=" + newstring)


"""
Ropgg(ctx,name) gets name's op.gg, has region support
"""


@bot.command()
async def Ropgg(ctx, name, region="na"):
    newstring = (str(name)).replace(" ", "+")
    url = "https://" + region + ".op.gg/summoner/userName=" + newstring
    r = requests.get(url)
    if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
        await ctx.send("User doesn't exist probably maybe")
    else:
        await ctx.send("https://" + region + ".op.gg/summoner/userName=" + newstring)


######LEAGUE BLCOK


# TWITTER BLOCK
api = twitter.Api(config.config["twitConsKey"],
                  config.config["twitConsSecret"],
                  config.config["twitAccessKey"],
                  config.config["twitAccessSecret"])

# api = tweepy.API(auth)


####Fun Server Features
"""
joined(ctx,member) prints when user first joined the server.
"""


@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} joined on {0.joined_at}'.format(member))


"""
firstmsg(ctx) gets date of first message sent in chat
"""


@bot.command()
async def firstmsg(ctx):
    channel = ctx.message.channel
    async for x in channel.history(limit=1, oldest_first=True):
        msg = x
        tim = x.created_at
    await ctx.send(tim)
    await ctx.send(msg.jump_url)


bot.add_cog(Music(bot))
bot.run(config.config["discordKey"])
