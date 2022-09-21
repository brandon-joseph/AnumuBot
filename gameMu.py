import config, requests
from discord.ext import commands
from bs4 import BeautifulSoup
import cassiopeia as cass

#cass.apply_settings(config.casstuff)
cass.set_riot_api_key(config.config['riotkey'])
gchamps = cass.get_champions(region="NA")


def listToString(lst):
    main = ""
    for item in lst:
        main += item + " "
    main = main.strip()
    return main


def toMulti(lst):
    base = """"""
    count = 1
    for i in lst:
        if count == len(lst):
            break
        base += i + " \n "
        count += 1
    base += i
    return base


class League(commands.Cog):
    #######LEAGUE BLOCK

    """
    opgg(self,ctx,name) gets name's op.gg, assuming they're on NA
    """

    @commands.command()
    async def opgg(self, ctx, *args):
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

    @commands.command(hidden=True)
    async def ropgg(self, ctx, region, *args):
        """Gets name's op.gg, has region support, can do euw,kr,jp,ru,etc."""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://" + region + ".op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            await ctx.send("https://" + region + ".op.gg/summoner/userName=" + newstring)

    @commands.command(aliases=['ranks'])
    async def rank(self, ctx, *args):
        """Gets League account name's rank"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
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

    ###region

    @commands.command(hidden=True)
    async def Rrank(self, ctx, region, *args):
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
    @commands.command(hidden=True, aliases=['winratio', 'wr'])
    async def winrate(self, ctx, *args):
        """Gets winrates of all Ranked Playlists. Hidden. Can also !wr"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            html = r.text
            parsed_html = BeautifulSoup(html)
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

            try:
                ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
                ratio = ratioobj.find('span', attrs={'class': 'winratio'})
                rat = ratio.text.strip()
            except:
                rat = "N/A"

        await ctx.send('''```{name}: 
Solo: {rate}
5v5: {flex5}
3v3: {flex3}```'''.format(name=newName, rate=rat, flex5=flexratio5, flex3=flexrank3))

    ####match count
    @commands.command(aliases=['mc'])
    async def matchcount(self, ctx, *args):
        """Gets count of all ranked matches. Can also !mc."""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            html = r.text
            parsed_html = BeautifulSoup(html)
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]

            level = parsed_html.body.find('span', attrs={'class': 'Level tip'}).text.strip()
            try:
                subs = parsed_html.body.find_all('div', attrs={'class': 'sub-tier'})
                ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
                wins = int(ratioobj.find('span', attrs={'class': 'wins'}).text.strip()[:-1])
                losses = int(ratioobj.find('span', attrs={'class': 'losses'}).text.strip()[:-1])
            except:
                wins = 0
                losses = 0

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
            totalS = wins + losses
            total2 =  flex3wins + flex3losses
            total3 = flex5wins + flex5losses

            fl2 = flex1[5:8]
            fl3 = flex2[5:8]


            await ctx.send('''```{name}, level {level}:
----------------------------------------
Solo: {solow}W,{solol}L | {t1} solo matches
----------------------------------------
{flex1}: {flex1w}W,{flex1l}L | {t2} {fl2} matches
----------------------------------------
{flex2}: {flex3w}W,{flex3l}L | {t3} {fl3} matches
----------------------------------------
Total: {total} matches```'''.format(name=newName, solow=wins, solol=losses, flex1=flex1, flex1w=flex3wins,
                                    flex1l=flex3losses, flex2=flex2, flex3w=flex5wins, flex3l=flex5losses,
                                    total=total, level=level,t1=totalS,t2=total2,t3=total3,fl2=fl2,fl3=fl3))

    ####oldranks
    @commands.command(aliases=['oldrank'])
    async def oldranks(self, ctx, *args):
        """Gets past season ranks"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            html = r.text
            parsed_html = BeautifulSoup(html)
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            level = parsed_html.body.find('span', attrs={'class': 'Level tip'}).text.strip()
            ranks = []
            for ultag in parsed_html.find_all('ul', {'class': 'PastRankList'}):
                for litag in ultag.find_all('li'):
                    ranks += [litag.text]
            lst = toMulti(ranks)
            await ctx.send('''```{name}, level {level}: 
    {lst}```'''.format(name=newName, level=level, lst=lst))

    @commands.command()
    async def isglendiamond(self, ctx):
        """You probably already know the answer but try anyway"""
        name = "KingWhatsitsface"
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
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
    async def forestfox(self, ctx):
        """."""
        name = "Forest Fox"
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)

        html = r.text
        parsed_html = BeautifulSoup(html)
        str1 = parsed_html.body.find('div', attrs={'class': 'TierRank'}).text.strip()
        newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
        ratioobj = parsed_html.body.find('div', attrs={'class': 'TierInfo'})
        ratio = ratioobj.find('span', attrs={'class': 'winratio'})

        await ctx.send('''```{name}'s rank is {str1}
    {rate}```'''.format(name=newName, str1=str1, rate=ratio.text.strip()))

    @commands.command(hidden=True)
    async def match(self, ctx, *args):
        """Get player's current match information. (Never finished this)"""
        name = listToString(args)
        newstring = (str(name)).replace(" ", "+")
        url = "https://na.op.gg/summoner/userName=" + newstring
        r = requests.get(url)
        if "This summoner is not registered at OP.GG. Please check spelling." in r.text:
            await ctx.send("User doesn't exist probably maybe")
        else:
            html = r.text
            parsed_html = BeautifulSoup(html)
            str1 = parsed_html.body.find('div', attrs={'class': 'TierRank'}).text.strip()
            newName = parsed_html.body.find('div', attrs={'class': 'Information'}).text.strip().splitlines()[0]
            # topteam = parsed_html.body.find_all('div', attrs={'class': 'SpectateSummoner'})[0].text.strip()
            topteam = parsed_html.findAll("div", {"class": "SpectateSummoner"})

            # print(r.text)
            await ctx.send('''```{name}'s rank is {str1}```'''.format(name=newName, str1=str1))

    @commands.command()
    async def level(self, ctx, *args):
        """Gets level of league account"""
        name = listToString(args)
        try:
            kal = cass.Summoner(name=name, region='NA')
            await ctx.send('''```{name}'s level is {str1}```'''.format(name=kal.name, str1=kal.level))
        except:
            await ctx.send("User doesn't exist probably maybe")

    ######LEAGUE BLCOK

    @commands.command()
    async def goodwith(self, ctx, name):
        """Returns champs account has above mastery 6 with (slow)"""
        await ctx.send("Working..."
                       "")
        kalturi = cass.Summoner(name=name, region='NA')
        good_with = kalturi.champion_masteries.filter(lambda cm: cm.level >= 6)
        names = []
        for item in good_with:
            names.append(item.champion.name)
        await ctx.send('```{nam}\'s best champions: \n'.format(nam=name) + pretlist(names) + '```')

    @commands.command()
    async def champ(self, ctx, name, champname):
        """Gets information about champ's use on account
        """
        await ctx.send("Working...")
        try:
            kal = cass.Summoner(name=name, region='NA')
            mast = toDict(kal.champion_masteries)
            champ = mast[champname]

            time = champ.last_played.format('YYYY-MM-DD HH:mm:ss')

            nam = kal.name
            champnam = champ.champion.name
            chest = champ.chest_granted
            lp = time
            lvl = champ.level
            pts = champ.points


            await ctx.send(f'''```{nam}'s {champnam}: \n
Chest Granted: {chest}
Last played: {lp}
Mastery level: {lvl}
Points: {pts}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command()
    async def lore(self,ctx,champname):
        """Gets lore of champion"""
        try:
          #  champs = cass.get_champions(region="NA")
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            lore = champ.lore
            await ctx.send(f'''```{name}: \n
{lore}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command(aliases = ['rd'])
    async def releasedate(self, ctx,  champname):
        """Gets release date of champion. 35% success rate"""
        try:
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            date = champ.release_date.format('YYYY-MM-DD')
            await ctx.send(f'''```{name}'s release date: \n
{date}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")


    @commands.command()
    async def allytips(self,ctx,champname):
        """Gets ally tips for champ"""
        try:
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            tips = prettyList(champ.ally_tips)
            await ctx.send(f'''```{name}:
{tips}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command()
    async def enemytips(self,ctx,champname):
        """Gets enemy tips for champ"""
        try:
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            tips = prettyList(champ.enemy_tips)
            await ctx.send(f'''```{name}:
{tips}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command()
    async def diff(self,ctx,champname):
        """Gets riots evaluation of champ"""
        try:
          #  champs = cass.get_champions(region="NA")
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            attack = champ.info.attack
            defense = champ.info.defense
            magic = champ.info.magic
            difficulty = champ.info.difficulty
            await ctx.send(f'''```{name}: \n
Attack: {attack}/10
Defense: {defense}/10
Magic: {magic}/10
Difficulty: {difficulty}/10```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command()
    async def skins(self,ctx,champname):
        """Gets skin list of champion"""
        try:
          #  champs = cass.get_champions(region="NA")
            dic = miniDic(gchamps)
            champ = dic[champname]
            name = champ.name
            skins = []
            for i in champ.skins: skins.append(i.name)
            skins = skins[1:]
            num = len(skins)
            await ctx.send(f'''```{name}, {num} skins: \n
{pretlist(skins)}```''')
        except:
            await ctx.send("Bad input or bad something else not sure")

    @commands.command()
    async def pp(self, ctx, *args):
        """Gets profile pic of league account. 50% failure rate
        """
        name = listToString(args)
        print(name)
        await ctx.send("Working...")
        try:
            kal = cass.Summoner(name=name, region='NA')
            print(kal.exists)
            await ctx.send(f'''{kal.name}'s profile pic: \n
{kal.profile_icon.url}''')
        except:
            await ctx.send("Bad input or bad something else not sure")






def toDict(lst):
    dic = {}
    for champ in lst:
        dic[champ.champion.name] = champ
    return dic


def miniDic(lst):
    dic = {}
    for champ in lst:
        dic[champ.name] = champ
    return dic

def pretlist(lst):
    result = ''
    for i in lst:
        result += i + ", "
    return result[:-2]



def prettyList(lst):
    acc = '\n'
    for i in lst:
        acc += i + '\n\n'
    return acc
