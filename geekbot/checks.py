import discord
from discord import channel
from discord.ext import commands


def has_role(role: str):
    async def predicate(ctx):
        geek_role = discord.utils.find(
            lambda r: r.name == role,
            ctx.guild.roles
        )
        return geek_role in ctx.author.roles
    return commands.check(predicate)

def in_channel(channels_names):
    async def predicate(ctx):
        return ctx.channel.name in channels_names
    return commands.check(predicate)

def in_ticket_channel():
    async def predicate(ctx):
        return "-ticket" in ctx.channel.name
    return commands.check(predicate)
