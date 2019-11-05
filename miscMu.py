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
        game = random.choice(globlist)
        await ctx.send('Maybe ' + game + ' is better?')

    """
    coin(ctx) flips a coin.
    """

    @commands.command()
    async def coin(self,ctx):
        acc = ["Heads", "Tails"]
        game = random.choice(acc)
        await ctx.send(game)

    """
    goldmine(ctx) is a hidden command that leads you to Eldorado
    """

    @commands.command()
    async def goldmine(self,ctx):
        await ctx.send('You\'ve found it ' + 'https://www.youtube.com/user/Rayzor324/videos?view_as=subscriber')

    """
    usual(ctx) is a deprecated function that performs whatgame(ctx,*args) on an already generated list, that should
    contain games frequented.
    """

    @commands.command()
    async def usual(self,ctx):
        acc = ["Smite", "League"]
        game = random.choice(acc)
        await ctx.send('How about ' + game + '?')

    """
    headshot(ctx) provides a headshot of the great god's face
    """

    @commands.command()
    async def headshot(self,ctx):
        channel = ctx.message.channel
        await channel.send(file=discord.File('AmumuSquare.png'))
    """
    glenoku(ctx) is  exactly what you think it is
    """

    @commands.command()
    async def glenoku(self,ctx):
        await ctx.send('https://www.youtube.com/watch?v=D7c7ywgWnAY')


    """
    glenoku2(ctx) is a hidden comma
    """

    @commands.command()
    async def glenoku2(self,ctx):
        await ctx.send("""In the works but for now:
                      https://vimeo.com/371258450 
                      pass: glen""")
