import discord
from geekbot import utils
from discord.ext import commands
from geekbot.checks import in_channel, in_ticket_channel


class Student(commands.Cog):
    def __init__(self, bot, queue) -> None:
        self.bot = bot
        self.queue = queue

    # ----- EVENT LISTENERS ----- #

    # ADD STUDENT TO QUEUE #
    @commands.Cog.listener()
    @in_channel(["get-tech-support"])
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if user != self.bot.user:
            if str(reaction) in ["💻"]:
                message = reaction.message
                message.author = user
                ctx = discord.ext.commands.Context(
                    author=user,
                    channel=reaction.message.channel,
                    guild=reaction.message.guild,
                    prefix="!",
                    message=message
                )

                # await reaction.message.channel.send("We will assist you shortly")
                if ctx.author not in self.queue:
                    self.queue.appendleft(ctx.author)

                    # await ctx.send(f"{ctx.author.name} has been added to the queue")

                    tickets_category = discord.utils.get(
                        ctx.guild.categories,
                        name="Tickets"
                    )

                    tickets = list(filter(
                        lambda channel: channel.name == f"{ctx.author.name.lower()}-ticket",
                        tickets_category.channels
                    ))

                    if len(tickets) > 0:
                        # await ctx.send(f"A ticket already exists for {ctx.author.name}")
                        pass
                    else:

                        member_role = await utils.assign_user_role(ctx, ctx.author)

                        geek_role = utils.get_geek_role(ctx)

                        # assign permissions
                        overwrites = {
                            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                            member_role: discord.PermissionOverwrite(read_messages=True),
                            geek_role: discord.PermissionOverwrite(read_messages=True)
                        }

                        new_channel = await ctx.guild.create_text_channel(
                            f"{ctx.author.name} Ticket",
                            category=tickets_category,
                            role=member_role,
                            overwrites=overwrites
                        )

                        # send a welcome message to the channel
                        await new_channel.send(
                            f'Hello {ctx.author.name}! Please join the waiting'
                            f' room channel and provide the following information for quality assurance: Full name, 901 number,'
                            f' EKU email, phone number, address/dorm hall and room number, and a brief description of your problem. '
                        )

                        # await ctx.send(f"A ticket has been created for {ctx.author.name}: {new_channel.mention}")

                        geek_waiting_room = discord.utils.get(
                            ctx.guild.channels,
                            name="geek-waiting-room"
                        )

                        await geek_waiting_room.send(
                            f"Member added to queue! " +
                            f"There {'are' if len(self.queue) > 1 else 'is'} " +
                            f"currently {len(self.queue)} student{'s' if len(self.queue) > 1 else ''} " +
                            f"in the queue."
                        )
                # else:
                #     await ctx.send(f"{ctx.author.name} is already in queue")
            await reaction.remove(user)

    # ----- COMMANDS ----- #

    # REMOVE SELF FROM QUEUE #
    @commands.command(
        name="removeme",
        brief="Removes message author from the queue.",
        help="This command removes the message author from the queue and deletes the ticket. Use this command if \
             your problem has been solved without Geek assistance."
    )
    @in_ticket_channel()
    async def remove_from_queue(self, ctx):
        if ctx.author in self.queue:
            self.queue.remove(ctx.author)

            tickets_category = discord.utils.get(
                ctx.guild.categories,
                name="Tickets"
            )

            await ctx.channel.delete()

            await ctx.send(f"{ctx.author.name} has been removed from the queue.")
        else:
            await ctx.send(f"{ctx.author.name} is not in the queue.")
