import discord
import os
from discord.ext import commands
from geekbot.checks import has_role, in_channel
from geekbot.utils import send_emails

class Coordinator(commands.Cog):
    def __init__(self, bot, queue) -> None:
        self.bot = bot
        self.queue = queue

    # ----- COMMANDS ----- #

    # REMOVE ROLE FROM USER #
    @commands.command(
        name="removerole",
        brief="Remove role from member",
        help="Removes the specified role from the specified member"
    )
    @has_role("Coordinator")
    @in_channel(["geek-waiting-room"])
    async def remove_role(self, ctx, role: discord.Role, member: discord.Member):
        await member.remove_roles(role)


    # EMAIL LOG FILE CONTENTS #
    @commands.command(
        name="emaillogs",
        brief="Email old tickets",
        help="This command looks for old ticket logs \
            and emails them to the geek email"
    )
    @has_role("Coordinator")
    @in_channel(["geek-waiting-room"])
    async def email_logs(self, ctx):
        log_files = os.listdir('logs/')

        if len(log_files) == 0:
            if ctx != None:
                await ctx.send(f"Sent 0 logs")
            return

        send_emails()
        await ctx.send(f"Sent {len(log_files)} logs")

    # PURGE FINISHED TICKETS #
    @commands.command(
        name="purge",
        brief="Delete old tickets",
        help="This command deletes all 'Finished' tickets. \
            Use after !emaillogs"
    )
    @has_role("Coordinator")
    @in_channel(["geek-waiting-room"])
    async def purge_finished_tickets(self, ctx):
        finished_tickets_category = discord.utils.get(
            ctx.guild.categories,
            name="Finished Tickets"
        )

        num_tickets = len(finished_tickets_category.channels)

        if num_tickets > 0:
            for channel in finished_tickets_category.channels:
                await channel.delete()

            await ctx.send(f"Deleted {num_tickets} ticket{'s' if num_tickets > 1 else ''}")