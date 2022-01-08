# Standard
import discord
import os
from discord.ext import commands
from os.path import join, dirname

# Third
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#commands bot
bot = commands.Bot(command_prefix='.', case_insensitive = True)

@bot.event
async def on_ready():
    print(f'\nBot: {bot.user}')
    print('\nCog loaded:')

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f'cogs.{file[:-3]}')

    bot.run(os.getenv('TOKEN'))