# Standard
import discord
from discord.ext import commands, tasks
from datetime import time, datetime, timedelta

# Local
from utils.auth import Auth
from utils.store import VALORANT_API
from utils.json_loader import data_read
from utils.view_notify import Notify
from utils.useful import get_tier_emoji, format_dt

class Notify_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notifys.start()
    
    def cog_unload(self):
        self.notifys.cancel()
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')
    
    @tasks.loop(time=time(hour=0, minute=0, second=30)) #utc 00:00:15
    async def notifys(self):
        data = data_read('notifys')
        skins = data_read('skins')['skins']

        # refresh access token
        user_access_token = [x['id'] for x in data]
        final_user = list(set(user_access_token))
        
        for user in final_user:
            try:
                Auth(user_id=user).get_users()
            except:
                pass
                
        for x in data:
            chennel = self.bot.get_channel(x['channel_id'])
            skin_data = VALORANT_API(x['id']).get_store_offer()
            duration = skin_data['duration']
            
            embed = discord.Embed(color=0xfd4554)

            if x['uuid'] == skin_data['skin1']['uuid']:
                name = skin_data['skin1']['name']
                user_id = x['id']
                uuid = x['uuid']
                view = Notify(user_id, uuid, name)
                
                author = await self.bot.fetch_user(user_id)
            
                embed.description = f"{get_tier_emoji(uuid, self.bot)} **{name}** is in your daily store!\nRemaining {format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')}"
                embed.set_thumbnail(url=skin_data['skin1']['icon'])

                view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

            if x['uuid'] == skin_data['skin2']['uuid']:
                name = skin_data['skin2']['name']
                user_id = x['id']
                uuid = x['uuid']
                view = Notify(user_id, uuid, name)

                author = await self.bot.fetch_user(user_id)

                embed.description = f"{get_tier_emoji(uuid, self.bot)} **{name}** is in your daily store!\n | Remaining "
                embed.set_thumbnail(url=skin_data['skin2']['icon'])
                
                view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

            if x['uuid'] == skin_data['skin3']['uuid']:
                name = skin_data['skin3']['name']
                user_id = x['id']
                uuid = x['uuid']
                view = Notify(user_id, uuid, name)

                author = await self.bot.fetch_user(user_id)

                embed.description = f"{get_tier_emoji(uuid, self.bot)} **{name}** is in your daily store!\n | Remaining "
                embed.set_thumbnail(url=skin_data['skin3']['icon'])

                view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

            if x['uuid'] == skin_data['skin4']['uuid']:
                name = skin_data['skin4']['name']
                user_id = x['id']
                uuid = x['uuid']
                view = Notify(user_id, uuid, name)

                author = await self.bot.fetch_user(user_id)

                embed.description = f"{get_tier_emoji(uuid, self.bot)} **{name}** is in your daily store!\n | Remaining "
                embed.set_thumbnail(url=skin_data['skin4']['icon'])

                view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

    @notifys.before_loop
    async def before_daily_send(self):
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')
        
def setup(bot):
    bot.add_cog(Notify_(bot))