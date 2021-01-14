from geekbot.checks import in_ticket_channel, has_role, in_channel
from geekbot.utils import get_ticket_channel, get_role
import discord
import os
from discord.ext import commands
from datetime import datetime

# Documentation for defing a check as a decorator
# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#checks

class Geek(commands.Cog):
    def __init__(self, bot, queue) -> None:
        self.bot = bot
        self.queue = queue

    # ----- EVENT LISTENERS ----- #

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            get_tech_support = discord.utils.get(
                guild.text_channels,
                name="get-tech-support"
            )
            await get_tech_support.purge()

            waiting_room = discord.utils.get(
                guild.voice_channels,
                name="Waiting Room"
            )

            message = await get_tech_support.send(
                "React to this message to request Tech Support!\n\n" +
                "A ticket will be created for you upon reaction.\n" +
                f"Please join the {waiting_room.mention} voice channel once you have a ticket."
            )
            await message.add_reaction("💻")

    # ----- COMMANDS ----- #

    # PRINT QUEUE #
    @commands.command(
        name="queue",
        brief="Print members is queue",
        help="This command prints out all \
            members currently in the queue (in order)"
    )
    @has_role("Geeks")
    @in_channel(["geek-waiting-room"])
    async def print_queue(self, ctx):
        await ctx.send(
            [member.name for member in self.queue]
        )

    # MOVE USERS TO VOICE #
    @commands.command(
        name="voice",
        brief="Move user(s) to voice",
        help="This command moves any specified members " \
            "(along with the message author) to " \
            "any available voice channel"
        )
    @has_role("Geeks")
    async def move_users_to_voice(self, ctx, *members: discord.Member):
        voice_channels = list(filter(
            lambda vc: vc.name == "Geek Help Channel",
            ctx.guild.voice_channels
        ))

        for vc in voice_channels:
            if len(vc.members) == 0:
                for member in members:
                    await member.edit(voice_channel=vc)
                await ctx.author.edit(voice_channel=vc)
                break
    
    # MANUALLY REMOVE MEMBER FROM QUEUE #
    @commands.command(
        name="remove",
        brief="Remove student from queue",
        help="This command removes a student from the queue (ticket is not deleted)."
    )
    @has_role("Geeks")
    @in_channel(["geek-waiting-room"])
    async def remove(self, ctx, member: discord.Member):
        role_name = member.name.lower().replace(" ", "-")
        member.remove_roles(role_name)

        self.queue.remove(member)
        await ctx.send(f"{member.name} has been remove from the queue")

    # MANUALLY ADD MEMBER TO QUEUE #
    @commands.command(
        name="add",
        brief="Add student to queue",
        help="This command adds a student to the queue (does not create ticket)."
    )
    @has_role("Geeks")
    @in_channel(["geek-waiting-room"])
    async def add(self, ctx, member: discord.Member):
        self.queue.appendleft(member)
        await ctx.send(f"{member.name} has been added to the queue")

    # ASSIST NEXT MEMBER IN QUEUE #
    @commands.command(
        name="assist",
        brief="Assist next student in queue.",
        help="This command removes next student (or student passed as a parameter) \
            from the queue and returns a link to their ticket"
    )
    @has_role("Geeks")
    @in_channel(["geek-waiting-room"])
    async def help_member_in_queue(self, ctx, member: discord.Member = None):
        if member:
            self.queue.remove(member)
        else:
            member = self.queue.pop()
        await ctx.send(f"{member.name} has been removed from the queue")

        ticket = get_ticket_channel(ctx, member)

        await ctx.send(f"{member.name}'s Ticket: {ticket.mention}")

    # DELETE MEMBER TICKETS #
    @commands.command(
        name="deletetickets",
        brief="Delete student tickets",
        help="This command deletes all tickets of specified member."
    )
    @has_role("Geeks")
    @in_channel(["geek-waiting-room"])
    async def delete_tickets(self, ctx, member: discord.Member):
        tickets_category = discord.utils.get(
            ctx.guild.categories,
            name="Tickets"
        )

        for channel in tickets_category.channels:
            if channel.name == f"{member.name.lower()}-ticket":
                # print(f"Deleted Channel: {channel}")
                await channel.delete()

    # CLOSE CURRENT TICKET #
    @commands.command(
        name="close",
        brief="Close current ticket.",
        help="This command closes the current ticket \
            and moves it to 'Finished'"
    )
    @has_role("Geeks")
    @in_ticket_channel()
    async def close_ticket(self, ctx):
        await ctx.send(f"Closing ticket: {ctx.channel.name}")

        member_role = get_role(
            ctx.guild,
            ctx.channel.name.replace("-ticket", "")
        )

        member = discord.utils.find(
            lambda x: member_role in x.roles,
            [member async for member in ctx.guild.fetch_members(limit=None)]
        )

        print(member)

        # in case !close is run before !assist
        try:
            self.queue.remove(member)
        except:
            print("member not in queue")

        # print(f"member_role: {member_role}")

        finished_tickets_category = discord.utils.find(
            lambda x: x.name == 'Finished Tickets',
            ctx.guild.categories
        )

        # print(finished_tickets_category)

        time = datetime.now()

        # get message history for user channel
        messages = await ctx.channel.history().flatten()

        # print(messages)

        # create log filename using channel name and date
        log_file = f"logs/{ctx.channel.name}_{time.strftime('%m%d%Y_%H%M%S')}.txt"
        log_file = os.path.join(os.getcwd(), log_file)
        # print(log_file)

        messages = messages[::-1]

        # write history to a file
        with open(log_file, "w+") as f:
            # print('Please do not spam!')
            for message in messages:
                f.writelines(f"{message.author.name}: {message.content}\n")

        await ctx.channel.send('Ticket has been set to closed.')

        await ctx.channel.edit(category=finished_tickets_category)
        
        geek_voice_channel = discord.utils.get(
                    ctx.guild.voice_channels,
                    name="Geek Waiting Room"
        )

        try:
            await ctx.author.edit(voice_channel=geek_voice_channel)
        except Exception as e:
            print("Geek not in voice")

        if member != ctx.author:
            try:
                await member.edit(voice_channel=None)
            except:
                print("User not in voice")

        await member_role.delete()

        geek_waiting_room = discord.utils.get(
            ctx.guild.channels,
            name="geek-waiting-room"
        )

        await ctx.send(f"{ctx.author.name}, please head back to the waiting room: {geek_waiting_room.mention}")

    # ----- ERROR HANDLERS ----- #

    @help_member_in_queue.error
    async def help_member_in_queue_error(self, ctx, error):
        # if member does not exist in guild
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send('I could not find that member...')

        elif isinstance(error, commands.errors.CommandInvokeError):

            # if try to pop from empty queue
            if isinstance(error.original, IndexError):
                await ctx.send('The queue is empty')

            # if try to remove member from queue that does not currently exist in queue
            elif isinstance(error.original, ValueError):
                member = list(filter(
                    lambda x: type(x) == discord.Member,
                    ctx.args
                ))[0]
                await ctx.send(f"{member.name} is not in the queue")
            else:
                print("UNHANDLED ERROR:", error)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print(f"ERROR: {ctx.author.name}' tried to use command '{ctx.command.qualified_name}' in channel '{ctx.channel.name}'")
