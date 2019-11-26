import discord, random, config,requests
from discord.ext import commands

from bs4 import BeautifulSoup


def listToString(list):
    main = ""
    for item in list:
        main += item + " "
    main = main.strip()
    return main




def toMulti(lst):
    base = """"""
    for i in lst:
        base += i + " \n "

    return base


class League(commands.Cog):
    #######LEAGUE BLOCK


    """
    opgg(self,ctx,name) gets name's op.gg, assuming they're on NA
    """

    @commands.command()
    async def opgg(self,ctx, *args):
        """Gets name's op.gg, assuming they're on NA"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            await ctx.send("https://na.op.gg/summoner/userName=" + newstring)

    """
    Ropgg(self,ctx,name) gets name's op.gg, has region support
    """

    @commands.command(pass_context=True, hidden=True)
    async def Ropgg(self,ctx, name, region="na"):
        """Gets name's op.gg, has region support, can do euw,kr,etc."""
        newstring = (str(name)).replace(" ", "+")
        url = "https://" + region + ".op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            await ctx.send("https://" + region + ".op.gg/summoner/userName=" + newstring)

    @commands.command(aliases=['ranks'])
    async def rank(self,ctx, *args):
        """Gets League account name's rank"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            link = "https://na.op.gg/summoner/userName=" + newstring
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]

            subs = parsed_html.body.find_all('div', attrs={'class': 'sub-tier'})
            flexobj1 = subs[0]

            flexrank = flexobj1.find('div', attrs={'class': 'sub-tier__rank-tier'}).text.strip()
            try:
                flexobj2 = subs[1]
                flexrank2 = flexobj2.find('div', attrs={'class': 'sub-tier__rank-tier'}).text.strip()
                await ctx.send('''```{name}'s rank is {str1}
    Flex Rank 3v3: {flex}
    Flex Rank 5v5: {flex2}```'''.format(name=newName, str1=str1, flex=flexrank, flex2=flexrank2))
            except:
                await ctx.send('''```{name}'s rank is {str1}
    Flex Rank 5v5: {flex}```'''.format(name=newName, str1=str1, flex=flexrank))
            # flexwinrate = flexobj.find('div', attrs={'class': 'sub-tier__grey'}).text.strip()

    ###region

    @commands.command(hidden=True)
    async def Rrank(self,ctx, region, *args):
        """Gets League account name's rank
        region can be kr,euw,etc."""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://" + region + ".op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]

            subs = parsed_html.body.find_all('div', attrs={'class': 'sub-tier'})
            flexobj1 = subs[0]

            flexrank = flexobj1.find('div', attrs={'class': 'sub-tier__rank-tier'}).text.strip()
            try:
                flexobj2 = subs[1]
                flexrank2 = flexobj2.find('div', attrs={'class': 'sub-tier__rank-tier'}).text.strip()
                await ctx.send('''```{name}'s rank is {str1}
    Flex Rank 3v3: {flex}
    Flex Rank 5v5: {flex2}```'''.format(name=newName, str1=str1, flex=flexrank, flex2=flexrank2))
            except:
                await ctx.send('''```{name}'s rank is {str1}
    Flex Rank 5v5: {flex}```'''.format(name=newName, str1=str1, flex=flexrank))
            # flexwinrate = flexobj.find('div', attrs={'class': 'sub-tier__grey'}).text.strip()

    ####winrate
    @commands.command(hidden=True, aliases=['winratio','wr'])
    async def winrate(self,ctx, *args):
        """Gets winrates of all Ranked Playlists. Hidden. Can also !wr"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            link = "https://na.op.gg/summoner/userName=" + newstring
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            subs = parsed_html.body.find_all('div', attrs={'class': 'sub-tier'})
            flexobj1 = subs[0]

            try:
                flexratio5 = flexobj1.find('div', attrs={'class': 'sub-tier__gray-text'}).text.strip()
            except:
                flexratio5 = "N/A"
            try:
                flexobj2 = subs[1]
                flexrank3 = flexobj2.find('div', attrs={'class': 'sub-tier__gray-text'}).text.strip()
            except:
                flexrank3 = "N/A"

        ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
        ratio = ratioobj.find('span', attrs={'class': 'winratio'})

        await ctx.send('''```{name}: 
    Solo: {rate}
    5v5: {flex5}
    3v3: {flex3}```'''.format(name=newName, rate=ratio.text.strip(), flex5=flexratio5, flex3=flexrank3))

    ####match count
    @commands.command(aliases=['mc'])
    async def matchcount(self,ctx, *args):
        """Gets count of all ranked matches. Can also !mc."""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            link = "https://na.op.gg/summoner/userName=" + newstring
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            subs = parsed_html.body.find_all('div', attrs={'class': 'sub-tier'})
            ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
            wins = int(ratioobj.find('span', attrs={'class': 'wins'}).text.strip()[:-1])
            losses = int(ratioobj.find('span', attrs={'class': 'losses'}).text.strip()[:-1])
            flexobj1 = subs[0]
            try:
                flex5obj = flexobj1.find('div', attrs={'class': 'sub-tier__info'})
                flex1 = flex5obj.find('div', attrs={'class': 'sub-tier__rank-type'}).text.strip()

                flex5obj = flex5obj.find('div', attrs={'class': 'sub-tier__league-point'})
                flex5 = flex5obj.find('span', attrs={'class': 'sub-tier__gray-text'}).text.strip()

                stro = flex5.split(' ', 1)[1]

                flex3wins = int(stro.split(' ', 1)[0][:-1])
                flex3losses = int(stro.split(' ', 1)[1][:-1])
            except:
                flex1 = "Flex 5:5 Rank"
                flex3wins = 0
                flex3losses = 0
            try:
                flexobj2 = subs[1]
                flexrank3 = flexobj2.find('div', attrs={'class': 'sub-tier__info'})
                flex2 = flexrank3.find('div', attrs={'class': 'sub-tier__rank-type'}).text.strip()
                flex3obj = flexrank3.find('div', attrs={'class': 'sub-tier__league-point'})
                flex3 = flex3obj.find('span', attrs={'class': 'sub-tier__gray-text'}).text.strip()

                stro = flex3.split(' ', 1)[1]

                flex5wins = int(stro.split(' ', 1)[0][:-1])
                flex5losses = int(stro.split(' ', 1)[1][:-1])
            except:
                flex2 = "Flex 3:3 Rank" if "Flex 5:5 Rank" == flex1 else "Flex 5:5 Rank"
                flex5wins = 0
                flex5losses = 0
            total = wins + losses + flex3wins + flex3losses + flex5wins + flex5losses

        await ctx.send('''```{name}:
    Solo: {solow}W,{solol}L
    {flex1}: {flex1w}W,{flex1l}L
    {flex2}: {flex3w}W,{flex3l}L
    Total: {total} matches```'''.format(name=newName, solow=wins, solol=losses, flex1=flex1, flex1w=flex3wins,
                                        flex1l=flex3losses, flex2=flex2, flex3w=flex5wins, flex3l=flex5losses,
                                        total=total))

    ####oldranks
    @commands.command(aliases=['oldrank'])
    async def oldranks(self,ctx, *args):
        """Gets past season ranks"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            link = "https://na.op.gg/summoner/userName=" + newstring
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            ranks = []
            for ultag in parsed_html.find_all('ul', {'class': 'PastRankList'}):
                for litag in ultag.find_all('li'):
                    ranks += [litag.text]
            lst = toMulti(ranks)
            await ctx.send('''```{name}: 
    {lst}```'''.format(name=newName, lst=lst))

    @commands.command()
    async def isglendiamond(self,ctx):
        """You probably already know the answer but try anyway"""
        name = "KingWhatsitsface"
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        link = "https://na.op.gg/summoner/userName=" + newstring
        html = r.text
        parsed_html = BeautifulSoup(html)
        str1 = parsed_html.body.find_all('div', attrs={'class': 'TierRank'})[0].text.strip()
        rankname = str1.split(' ', 1)[0]
        newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
        if rankname == 'Diamond':
            await ctx.send('''```He is Pog, Glen's rank is {str1}```''')
        else:
            await ctx.send('''```Nope, sad stuff. Glen's rank is {str1}```'''.format(str1=str1))

    @commands.command(hidden=True)
    async def forestfox(self,ctx):
        """."""
        name = "Forest Fox"
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)

        link = "https://na.op.gg/summoner/userName=" + newstring
        html = r.text
        parsed_html = BeautifulSoup(html)
        str1 = parsed_html.body.find('div', attrs={'class': 'TierRank'}).text.strip()
        newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
        ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
        ratio = ratioobj.find('span', attrs={'class': 'winratio'})

        await ctx.send('''```{name}'s rank is {str1}
    {rate}```'''.format(name=newName, str1=str1, rate=ratio.text.strip()))

    @commands.command(pass_context=True, hidden=True)
    async def match(self,ctx, *args):
        """Get player's current match information. (Never finished this)"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            link = "https://na.op.gg/summoner/userName=" + newstring
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find('div', attrs={'class': 'TierRank'}).text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            # topteam = parsed_html.body.find_all('div', attrs={'class': 'SpectateSummoner'})[0].text.strip()
            topteam = parsed_html.findAll("div", {"class": "SpectateSummoner"})

            # print(r.text)
            await ctx.send('''```{name}'s rank is {str1}```'''.format(name=newName, str1=str1))

    ######LEAGUE BLCOK