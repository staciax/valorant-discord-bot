# Standard
import discord
from discord.ext import commands, tasks
from datetime import time, datetime

# Standard
import os

# Local
from utils.api import ValorantAPI

#valorant_api
#available regions: eu, ap, na, kr | (latem, br = 'na')
MY_REGION = os.getenv('REGION')

class loop_store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.valorant_loop.start()
    
    def cog_unload(self):
        self.valorant_loop.cancel()
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')
    
    @tasks.loop(time=time(hour=0, minute=0, second=30)) #gmt 00:00 เท่ากับ เวลาไทย 7 โมงเช้า (gmt +7)
    # @tasks.loop(seconds=10) # ไว้เทสนะครับ ปิดใช้งานอันบนก่อน
    async def valorant_loop(self):
            CHANNEL_LOOP = os.getenv('CHANNEL_ID', None)
            try:
                self.channel = self.bot.get_channel(int(CHANNEL_LOOP))
                with open("accounts.txt", encoding='utf-8') as file:
                    for x in file.readlines():
                        account = x.rstrip("\n").split(";")
                        api = ValorantAPI(channel=self.channel, username=account[0], password=account[1], region=MY_REGION)
                        await api.for_loop_send()
            except ValueError:
                pass
            except:
                pass
    
    @valorant_loop.before_loop
    async def before_daily_send(self):
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(loop_store(bot))