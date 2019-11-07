import discord, random, config
from discord.ext import commands

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



class Misc(commands.Cog):


    """
    whatgame(ctx,*args) takes in a list of games then randomly picks one and returns it
    """

    @commands.command()
    async def whatgame(self,ctx, *args):
        """Takes in a list of games then randomly picks one and returns it"""
        acc = []
        for v in args:
            acc.append(v)
        cmplist(acc)
        game = random.choice(acc)
        await ctx.send('How about ' + game + '?')

    """
    maketeams(ctx,n,*args) divides people into n teams
    """

    @commands.command()
    async def maketeams(self,ctx, n, *args):
        """Divides people into n teams"""
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

    @commands.command()
    async def again(self,ctx):
        """Rerolls the previous whatgame operation"""
        game = random.choice(globlist)
        await ctx.send('Maybe ' + game + ' is better?')

    """
    coin(ctx) flips a coin.
    """

    @commands.command()
    async def coin(self,ctx):
        """Flips a coin."""
        acc = ["Heads", "Tails"]
        game = random.choice(acc)
        await ctx.send(game)

    """
    goldmine(ctx) is a hidden command that leads you to Eldorado
    """

    @commands.command(pass_context=True, hidden=True)
    async def goldmine(self,ctx):
        """Leads you to Eldorado"""
        await ctx.send('You\'ve found it ' + 'https://www.youtube.com/user/Rayzor324/videos?view_as=subscriber')

    """
    usual(ctx) is a deprecated function that performs whatgame(ctx,*args) on an already generated list, that should
    contain games frequented.
    """

    @commands.command(pass_context=True, hidden=True)
    async def usual(self,ctx):
        """Deprecated function"""
        acc = ["Smite", "League"]
        game = random.choice(acc)
        await ctx.send('How about ' + game + '?')

    """
    headshot(ctx) provides a headshot of the great god's face
    """

    @commands.command(pass_context=True, hidden=True)
    async def headshot(self,ctx):
        """Provides a headshot of the great god's face"""
        channel = ctx.message.channel
        await channel.send(file=discord.File('AmumuSquare.png'))
    """
    glenoku(ctx) is  exactly what you think it is
    """

    @commands.command()
    async def glenoku(self,ctx):
        """Exactly what you think it is"""
        await ctx.send('https://www.youtube.com/watch?v=D7c7ywgWnAY')


    """
    glenoku2(ctx) is a hidden comma
    """

    @commands.command(pass_context=True, hidden=True)
    async def glenoku2(self,ctx):
        """Oh dear it seems you've seen it"""
        await ctx.send("""In the works but for now:
                      https://vimeo.com/371258450 
                      pass: glen""")


    """
    glenoku3(ctx) is a hidden comma
    """

    @commands.command(pass_context=True, hidden=True)
    async def glenoku3(self,ctx):
        """Oh dear it seems you've seen it again"""
        await ctx.send("""This one also got blocked cause of copyright
        https://vimeo.com/371526746
        pass: glen
        """)
