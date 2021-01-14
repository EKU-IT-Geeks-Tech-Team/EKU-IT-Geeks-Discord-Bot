import discord
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


async def log_message_history(self, channel):
    time = datetime.now()

    # get message history for user channel
    messages = await channel.history().flatten()

    # create log filename using channel name and date
    log_file = f"logs/{channel.name}_{time.strftime('%m%d%Y_%H%M%S')}.txt"

    # write history to a file
    with open(log_file, "w") as f:
        f.write(f'Closed at {time}\n')
        f.writelines("\n".join([message.content for message in messages]))

    # print("Log written")

def get_ticket_channel(ctx, member: discord.Member):
    tickets_category = discord.utils.get(
        ctx.guild.categories,
        name="Tickets"
    )

    tickets = list(filter(
        lambda channel: channel.name == f"{member.name.lower().replace(' ', '-')}-ticket",
        tickets_category.channels
    ))

    if len(tickets) > 0:
        return tickets[0]

def get_geek_role(ctx):
    return get_role(ctx.guild, "Geeks")


def is_geek(member: discord.Member):
    return has_role(member, 'Geeks')


def get_role(guild: discord.Guild, role: str):
    return discord.utils.find(
        lambda x: x.name == role, guild.roles
    )


def has_role(member: discord.Member, role: str):
    return discord.utils.find(
        lambda x: x.name == role, member.roles
    ) != None


async def add_role(member: discord.Member, r: discord.Role):
    await member.add_roles(r)


async def remove_role(member: discord, role: str):
    r = discord.utils.find(
        lambda x: x.name == role, member.roles
    )
    await member.remove_roles(r)


async def assign_user_role(ctx, member: discord.Member):
    role_name = ctx.author.name.lower().replace(" ", "-")

    # check to see if a role already exists for member
    member_role = get_role(ctx.guild, role_name)

    # create one if not
    if not member_role:
        member_role = await ctx.guild.create_role(name=role_name)

    # add role to member
    await add_role(ctx.author, member_role)

    return member_role

def send_emails():
        log_files = os.listdir(os.path.join(os.getcwd(), 'logs/'))

        if len(log_files) == 0:
            return

        port = 465  # For SSL
        bot_email = os.getenv("BOT_EMAIL")
        bot_password = os.getenv("EMAIL_PASSWORD")

        receiver_email = os.getenv("RECEIVER_EMAIL")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Discord Logs ({datetime.now().strftime('%m/%d/%Y')})"
        message["From"] = bot_email
        message["To"] = receiver_email

        html = ""

        for file in log_files:
            with open(os.path.join(os.getcwd(), f"logs/{file}"), "r") as f:
                file_contents = "<br><br>".join(f.readlines())
                html += f"""\
{file_contents}

<hr>

"""

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)



        try:
            # SMTP_SSL Example
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server_ssl.ehlo() # optional, called by login()
            server_ssl.login(bot_email, bot_password)  
            # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
            server_ssl.sendmail(bot_email, receiver_email, message.as_string())
            #server_ssl.quit()
            server_ssl.close()
            print('successfully sent the mail')

            for file in log_files:
                os.remove(os.path.join(os.getcwd(), f"logs/{file}"))

        except:
            print("failed to send mail")