from geekbot import bot, queue
from geekbot.cogs.geek import Geek
from geekbot.cogs.student import Student
from geekbot.cogs.coordinator import Coordinator
import os


def run():
    ''' cogs are like groups of commands that we can add to our bot
    allows us to seperate things out '''
    bot.add_cog(Geek(bot, queue))
    bot.add_cog(Student(bot, queue))
    bot.add_cog(Coordinator(bot, queue))

    TOKEN = os.getenv('TOKEN', None)
    bot.run(TOKEN)

if __name__ == "__main__":
    run()