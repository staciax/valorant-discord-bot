# Standard
import discord
from discord.commands import slash_command, Option
from discord.ext import commands

# Standard
import os

# Local
from utils.api import ValorantAPI

#env_loader
MY_SERVER_ID = int(os.getenv('SERVER_ID'))  # don't edit this
MY_REGION = os.getenv('REGION')  # don't edit this

class valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')
    
    @slash_command(description="Shows my daily store", guild_ids=[MY_SERVER_ID]) #ถ้าอยากให้ใช้ได้ทุกเซิฟ เอาออก guild_ids ได้ นะครับ ใช้เวลาประมาณ 1 ชม ถ้าไม่ระบุ หรือ ระบุเซิฟที่บอทอยู่ ประมาณนี้ guild_ids=[929451246493003816, 840379510704046151]
    async def store(self, interaction, username: Option(str, "Input username"), password: Option(str, "Input password")):
        api = ValorantAPI(interaction, username, password, region=MY_REGION, bot=self.bot)
        await api.start()
        
def setup(bot):
    bot.add_cog(valorant(bot))