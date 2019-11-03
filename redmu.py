import discordmain
import praw
from discord.ext import commands
import config

# reddit initialize
reddit = praw.Reddit(client_id=config.config["redditClientID"],
                     client_secret=config.config['redditClientSecret'],
                     password=config.config["redditPass"],
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True

class Redmu(commands.Cog):
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
        main = getPosts(sub, int(n))
        for submis in main:
            await ctx.send(submis[0] + '\n' + submis[1] + '\n\n')




def getPosts(sub, n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day', limit=n):
        if submission.is_self:
            main += [[submission.title, submission.selftext]]
        else:
            main += [[submission.title, submission.url]]
    return main



def setup(bot):
    bot.add_cog(Redmu(bot))


