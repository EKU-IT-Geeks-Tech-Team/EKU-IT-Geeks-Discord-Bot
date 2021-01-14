import os
import discord
from discord.ext import commands
from collections import deque as Queue


bot = commands.Bot(command_prefix='!')

env = os.getenv("ENV")

if env == "development":
    from jishaku import jsk
    bot.load_extension("jishaku")
    
queue = Queue()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
