import discordMu
import praw, twitter, requests, json, re,time,asyncio
from discord.ext import commands
import config
from datetime import date
from bs4 import BeautifulSoup


# reddit initialize
reddit = praw.Reddit(client_id=config.config["redditClientID"],
                     client_secret=config.config['redditClientSecret'],
                     password=config.config["redditPass"],
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True

# TWITTER BLOCK
api = twitter.Api(config.config["twitConsKey"],
                  config.config["twitConsSecret"],
                  config.config["twitAccessKey"],
                  config.config["twitAccessSecret"],
                  tweet_mode='extended')


class web(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # """
    # redditcheck(ctx) checks if reddit is working
    # """
    # @commands.command()
    # async def redditcheck(self,ctx):
    #     print(reddit.user.me())
    #     await ctx.send(reddit.user.me())

    """
    getreddit(ctx,sub,n) gets top n posts of subreddit
    """

    @commands.command()
    async def getreddit(self, ctx, sub, n):
        """Gets top n posts of subreddit"""
        main = getPosts(sub, int(n))
        for submis in main:
            await ctx.send("```" + '\n' + "Title: " + submis[0] + " ``` " + submis[1] + '\n\n')

    """
    getreddit(ctx,sub,n) gets top n posts of subreddit
    """

    @commands.command()
    async def red(self, ctx, url):
        """Gets elements out of reddit post"""
        post_id = reddit.submission(url=url)
        submission = reddit.submission(id=post_id)
        title = submission.title
        if submission.is_self:
            second = submission.selftext
        else:
            second = submission.url
        # print("Red")
        await ctx.send("```" + '\n' + "Title: " + title + " ``` " + second + '\n\n')

    """
    whatanime(ctx, url) finds name of anime using trace.moe API
    https://soruly.github.io/trace.moe/#/
    """

    @commands.command(pass_context=True, aliases=['whatanime'])
    async def weebdar(self, ctx, url):
        """Finds name of anime using trace.moe API"""
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

    """
    poll(ctx,name,args) creates poll
    """

    @commands.command()
    async def poll(self, ctx, name, *args):
        """Creates poll with name then args"""
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

    @commands.command(pass_context=True, hidden=True, aliases=['borderlands'])
    async def shift(self, ctx):
        """gets the latest shift keys for borderlands 3 only"""
        acc = []

        # statuses = api.GetUserTimeline(906234810,count=100,exclude_replies=True) #For dgShift
        statuses = api.GetUserTimeline(1185243019622137857, count=100, exclude_replies=True)

        # print(statuses)
        for s in statuses:
            shift = shiftEx(s.full_text)
            if shift != "None":
                acc.append(shift)

        await ctx.send(prettyList(acc))
        # print([s.text for s in statuses])

    @commands.command( hidden=True)
    async def monitor(self,ctx,base):
        url = base
        r = requests.get(url)
        html = r.text
        html5 = r.text

        n = 0
        starttime = time.time()
        while (html == html5):
            r = requests.get(url)
            html5 = r.text
            n+=0.5
            print("time :" + str(n))
            time.sleep(30.0 - ((time.time() - starttime) % 30.0))

        await ctx.author.send("It's up")



    @commands.command( hidden=True)
    async def monitortest(self,ctx):
        await ctx.author.send("It's up")


def getPosts(sub, n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day', limit=n):
        if submission.is_self:
            main += [[submission.title, submission.selftext]]
        else:
            main += [[submission.title, submission.url]]
    return main


def shiftEx(tweet):
    # list = [y for y in (x.strip() for x in str.splitlines()) if y]
    check = tweet.lower()
    if 'shift code' in check:
        if "borderlands 3" in check:
            m = re.search('.....[-].....[-].....[-].....[-].....', tweet)
            n = re.search('[0-9]+ GOLD KEY', tweet)
            if m:
                try:
                    return m.group(0) + "  |  " + n.group(0)
                except:
                    return m.group(0) + "  |  Other"
    return "None"






def prettyList(lst):
    acc = '```' + '\n'
    for i in lst:
        acc += i + '\n'
    acc += '```'
    return acc


y = True  # Hides why block


class why(commands.Cog):

    @commands.command(hidden=y)
    async def catfact(self, ctx):
        """Gets a random cat fact"""
        r = requests.get("https://catfact.ninja/fact")
        result = r.json()
        await ctx.send("```Cat Fact: \n" + result['fact'] + "```")

    @commands.command(hidden=y)
    async def dog(self, ctx):
        """Gets a random picture of a dog"""
        r = requests.get("https://dog.ceo/api/breeds/image/random")
        result = r.json()
        await ctx.send(result['message'])

    @commands.command(hidden=y)
    async def cat(self, ctx):
        """Gets a random picture of a cat"""
        r = requests.get("https://aws.random.cat/meow?ref=apilist.fun")
        result = r.json()
        await ctx.send(result['file'])

    @commands.command(hidden=y)
    async def fact(self, ctx):
        """Gets a random fact"""
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        result = r.json()
        await ctx.send("```Fact: \n" + result['text'] + "```")

    @commands.command(hidden=y)
    async def tfact(self, ctx):
        """Gets today's random fact"""
        r = requests.get("https://uselessfacts.jsph.pl/today.json?language=en")
        result = r.json()
        today = date.today()
        await ctx.send("```Today's, {dat}, fact: \n\n".format(dat=today) + result['text'] + "```")

    @commands.command(hidden=y)
    async def kanye(self, ctx):
        """Gets a kanye quote"""
        r = requests.get("https://api.kanye.rest/")
        result = r.json()
        await ctx.send("```Kanye: \n\n\"" + result['quote'] + "\"```")


def setup(bot):
    bot.add_cog(web(bot))
