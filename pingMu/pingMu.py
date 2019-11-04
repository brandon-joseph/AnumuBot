import discord
from discord.ext import commands
import pickle,os



def idToString(id):
    return '<@'+ str(id) + '>'

def prettylist(lst):
    acc = ""
    for b in lst[:-1]:
        acc = acc + str(b) + ", "
    return acc + str(lst[-1])

class Ping(commands.Cog):
    """
    bl3(ctx) is a function that @'s all owners of Borderlands 3
    """


    @commands.command()
    async def bl3(self,ctx):
        await ctx.send(
            'Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269>')


    """
    weebs(ctx) is a function that @'s weebs
    """


    @commands.command()
    async def weebs(self,ctx):
        await ctx.send(
            'Assemble: ' + '<@161146253307150336> <@191259371672567809> <@199673866132389889> <@328215412007370762> <@195335847028064269> <@328215412007370762><@191267028454080513><@187745555273744384>')



    @commands.command(pass_context=True, aliases=['pC'])
    async def pingCreate(self,ctx,name):

        for x in os.listdir(os.getcwd() + '/pingMu'):
            if x == (name + '.txt'):
                await ctx.send('Already created')
                return

        file = open('./pingMu/' + name + '.txt', "w")
     #   file.write("Your text goes here")
        file.close()

        await ctx.send('Created')

    @commands.command(pass_context=True, aliases=['p'])
    async def ping(self,ctx,group):
        try:
            with open('./pingMu/' + group + '.txt', 'rb') as fp:
                itemlist = pickle.load(fp)
            result = prettylist(itemlist)
            await ctx.send(
                'Assemble: ' + result)
        except:
            await ctx.send("Possibly corrupt group, likely empty")


    @commands.command(pass_context=True, aliases=['pA'])
    async def pingAdd(self,ctx, group, member: discord.User):
        for x in os.listdir(os.getcwd() + '/pingMu'):
            if x == (group + '.txt'):
                with open('./pingMu/' + group + '.txt', 'rb') as fp:
                    if os.stat('./pingMu/' + group + '.txt').st_size != 0:
                        itemlist = pickle.load(fp)
                    else:
                        itemlist = []
                for item in itemlist:
                    if item == idToString(member.id):
                        await ctx.send("Member already in group")
                        return
                itemlist.append(idToString(member.id))
                with open('./pingMu/' + group + '.txt', 'wb') as fp:
                    pickle.dump(itemlist, fp)
                await ctx.send("Done")
                return
        await ctx.send("Not a real group nerd")

    @commands.command(pass_context=True, aliases=['pAll','pAddMult'])
    async def pingAddAll(self,ctx, group, *mem: discord.User):
        for member in mem:
            for x in os.listdir(os.getcwd() + '/pingMu'):
                if x == (group + '.txt'):
                    with open('./pingMu/' + group + '.txt', 'rb') as fp:
                        if os.stat('./pingMu/' + group + '.txt').st_size != 0:
                            itemlist = pickle.load(fp)
                        else:
                            itemlist = []
                    for item in itemlist:
                        if item == idToString(member.id):
                            await ctx.send("Member already in group")
                            continue
                    if item != idToString(member.id):
                        itemlist.append(idToString(member.id))
                    with open('./pingMu/' + group + '.txt', 'wb') as fp:
                        pickle.dump(itemlist, fp)

        await ctx.send("Done")


    @commands.command(pass_context=True, aliases=['pR'])
    async def pingRemove(self,ctx,group, member: discord.User):
        for x in os.listdir(os.getcwd() + '/pingMu'):
            if x == (group + '.txt'):
                with open('./pingMu/' + group + '.txt', 'rb') as fp:
                    if os.stat('./pingMu/' + group + '.txt').st_size != 0:
                        itemlist = pickle.load(fp)
                    else:
                        itemlist = []
                itemlist.remove(idToString(member.id))
                with open('./pingMu/' + group + '.txt', 'wb') as fp:
                    pickle.dump(itemlist, fp)
                await ctx.send("Done")
                return
        await ctx.send("Not a real group nerd")
