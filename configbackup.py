import datetime

config = {
    'redditClientID': '5FvloSDXtBoP-Q',
    'redditClientSecret': 'v6xhOeAhVb4CJSkTe6sldNT8j5E',
    'redditPass': '2K04uNpgBJG9',
    'twitConsKey': "0CtcKB78W6KHtzi9nEr3DZWZv",
    'twitConsSecret': "rq8a3Pge0gjM5wBh4LtsVsEqrssYSEJ9Ed4X6RII3KBxaLnwEd",
    'twitAccessKey': "133073551-t8uFMPnE7kkjcAJEvn1Aro4uasiWt9PBvIYEgAhU",
    'twitAccessSecret': "IGaiYenAhN7y213OhhYaiR3jm6XnAT3ysABf5Ep5s9070",
    'discordKey': 'NjM2NDQxOTc4NDY4NDMzOTMy.XcxYSQ.vJhvbFnM3YdvQs9BvReMMXg_cqs',
    'imgurClient': '8d93ec11c7a9918',
    'imgurSecret': '42740c0859345b5ecf24c4c334babb98d109ea64',
    'streamablePass': '65vHmP57vUGs',
    'saucenao': '269438df6d7ece9507da5b90214a6f1d4e657d97',
    'riotkey': 'RGAPI-61a6d9eb-1421-4435-b68e-0ac99cf7fe02'
}

casstuff = {'global': {'version_from_match': 'patch', 'default_region': "NA"},
            'plugins': {},
            'pipeline': {'Cache': {},
                         'SimpleKVDiskStore': {
                             "package": "cassiopeia_diskstore",
                             "path": "/home/bjj43/AnumuBot/cassData",
                             "expirations": {
                                 'RealmDto': datetime.timedelta(hours=6),
                                 'VersionListDto': datetime.timedelta(hours=6),
                                 'ChampionDto': 0,
                                 'ChampionListDto': 0,
                                 'RuneDto': 0,
                                 'RuneListDto': 0,
                                 'ItemDto': 0,
                                 'ItemListDto': 0,
                                 'SummonerSpellDto': 0,
                                 'SummonerSpellListDto': 0,
                                 'MapDto': 0,
                                 'MapListDto': 0,
                                 'ProfileIconDetailsDto': 0,
                                 'ProfileIconDataDto': 0,
                                 'LanguagesDto': 0,
                                 'LanguageStringsDto': 0,
                                 'ChampionRotationDto': 0,
                                 'ChampionMasteryDto': 0,
                                 'ChampionMasteryListDto': 0,
                                 'ShardStatusDto': 0,
                             }
                         },
                         'DDragon': {},
                         'RiotAPI': {'api_key': 'RGAPI-61a6d9eb-1421-4435-b68e-0ac99cf7fe02'}},
            'logging': {'print_calls': True, 'print_riot_api_key': True, 'default': 'WARNING', 'core': 'WARNING'}
            }
