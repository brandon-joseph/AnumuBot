import discord
import random
from discord.ext import commands
import asyncio
import strawpoll
from cv2 import cv2
import numpy as np
import time
import praw
import requests




reddit = praw.Reddit(client_id='5FvloSDXtBoP-Q',
                     client_secret='v6xhOeAhVb4CJSkTe6sldNT8j5E',
                     password='2K04uNpgBJG9',
                     user_agent='Anumubot by /u/Rayzor324',
                     username='AnumuBot')
reddit.read_only = True

def getPosts(sub,n):
    main = []
    for submission in reddit.subreddit(sub).top(time_filter='day',limit=n):
        main += [[submission.title,submission.url]]

    for submis in main:
         print(submis[0] + '\n' + submis[1] + '\n')

getPosts('shitpostcrusaders',5)
# for post in posts:
#     url = (post.url)
#     file_name = url.split("/")
#     if len(file_name) == 0:
#         file_name = re.findall("/(.*?)", url)
#     file_name = file_name[-1]
#     if "." not in file_name:
#         file_name += ".jpg"
#     print(file_name)
# r = requests.get(url)
# with open(file_name,"wb") as f:
#     f.write(r.content)
#     print(submission.title)
