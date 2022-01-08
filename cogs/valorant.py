# Standard
import discord
from discord.commands import slash_command, Option
from discord.ext import commands, tasks
from datetime import time, datetime

# Standard
import os

# Local
from utils.api import ValorantAPI

#valorant_api
#available regions: eu, ap, na, kr | (latem, br = 'na')

#slash_server_id
MY_SERVER_ID = int(os.getenv('SLASH_SERVER_ID'))

class valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')
    
    @slash_command(description="Shows my daily store", guild_ids=[MY_SERVER_ID]) #Input your server id
    async def store(self, interaction, username: Option(str, "Input username"), password: Option(str, "Input password")):
        api = ValorantAPI(interaction, username, password, region='ap')
        await api.start()

        
def setup(bot):
    bot.add_cog(valorant(bot))