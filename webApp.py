import discordMu
import praw, twitter, requests,json
from discord.ext import commands
import config

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
                  config.config["twitAccessSecret"])



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
    whatanime(ctx, url) finds name of anime using trace.moe API
    https://soruly.github.io/trace.moe/#/
    """


    @commands.command(pass_context=True, aliases=['whatanime'])
    async def weebdar(self,ctx, url):
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
    async def poll(self,ctx, name, *args):
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






def getPosts(sub, n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day', limit=n):
        if submission.is_self:
            main += [[submission.title, submission.selftext]]
        else:
            main += [[submission.title, submission.url]]
    return main



def setup(bot):
    bot.add_cog(web(bot))


