# Standard
import discord
from discord.ext import commands, tasks
from datetime import time, datetime, timedelta

# Local
from utils.auth import Auth
from utils.store import VALORANT_API
from utils.json_loader import data_read, config_read
from utils.view_notify import Notify
from utils.useful import get_tier_emoji, format_dt, embed_giorgio_notify, notify_send
from utils.pillow import generate_image

class Notify_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notifys.start()
    
    def cog_unload(self):
        self.notifys.cancel()
         
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')
    
    @tasks.loop(time=time(hour=0, minute=0, second=15)) #utc 00:00:15
    async def notifys(self):
        
        config = config_read()
        design = config['embed_design']
        notify_mode = config['notify_mode']

        if notify_mode == 'Spectified':
            # NOTIFY IN YOUR LIST
            try:
                data = data_read('notifys')
                user_access_token = [x['id'] for x in data]
                final_user = list(set(user_access_token))
                
                # refresh access token
                for user in final_user:
                    try:
                        Auth(user_id=user).get_users()
                    except:
                        pass
            
                for x in data:
                    chennel = self.bot.get_channel(x['channel_id'])
                    skin_data = VALORANT_API(x['id']).get_store_offer()
                    duration = skin_data['duration']
                    duration = format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')
                    
                    embed = discord.Embed(color=0xfd4554)

                    if x['uuid'] == skin_data['skin1']['uuid']:
                        name = skin_data['skin1']['name']
                        user_id = x['id']
                        uuid = x['uuid']
                        icon = skin_data['skin1']['icon']
                        view = Notify(user_id, uuid, name)
                        author = await self.bot.fetch_user(user_id)
                        embed = notify_send(get_tier_emoji(uuid, self.bot), name, duration, icon)
                        view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

                    if x['uuid'] == skin_data['skin2']['uuid']:
                        name = skin_data['skin2']['name']
                        user_id = x['id']
                        uuid = x['uuid']
                        view = Notify(user_id, uuid, name)
                        icon = skin_data['skin2']['icon']
                        author = await self.bot.fetch_user(user_id)
                        embed = notify_send(get_tier_emoji(uuid, self.bot), name, duration, icon)
                        view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

                    if x['uuid'] == skin_data['skin3']['uuid']:
                        name = skin_data['skin3']['name']
                        user_id = x['id']
                        uuid = x['uuid']
                        icon = skin_data['skin3']['icon']
                        view = Notify(user_id, uuid, name)
                        author = await self.bot.fetch_user(user_id)
                        embed = notify_send(get_tier_emoji(uuid, self.bot), name, duration, icon)
                        view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

                    if x['uuid'] == skin_data['skin4']['uuid']:
                        name = skin_data['skin4']['name']
                        user_id = x['id']
                        uuid = x['uuid']
                        icon = skin_data['skin4']['icon']
                        view = Notify(user_id, uuid, name)
                        author = await self.bot.fetch_user(user_id)
                        embed = notify_send(get_tier_emoji(uuid, self.bot), name, duration, icon)
                        view.message = await chennel.send(content=f'||{author.mention}||', embed=embed, view=view)

            except (KeyError, FileNotFoundError):
                pass
            except Exception as e:
                print(f'Notify Spectified error - {e}')

        elif notify_mode == 'All':

            # NOTIFY ALL SKIN
            try:
                user_data = data_read('users')

                for user in user_data:
                    data_ = Auth(user_id=user).get_users()
                    skin_list = VALORANT_API(user).get_store_offer()
                    
                    channel = self.bot.get_channel(int(data_['channel']))
                    duration = skin_list['duration']
                    
                    if design == 'ꜱᴛᴀᴄɪᴀ.#7475':

                        file_ = generate_image(skin_list)
                        embed = discord.Embed(description=f"**Daily Store for {data_['IGN']}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=skin_list['duration'])), 'R')}",color=0xfd4554)
                        embed.set_image(url='attachment://store-offers.png') 
                        await channel.send(file=file_, embed=embed)
                    
                    elif design == 'Giorgio#0609':

                        skin1 = skin_list['skin1']
                        skin2 = skin_list['skin2']
                        skin3 = skin_list['skin3']
                        skin4 = skin_list['skin4']

                        embed = discord.Embed(color=0xfd4554)
                        embed.description = f"Daily store for **{data_['IGN']}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=skin_list['duration'])), 'R')}"

                        embed1 = embed_giorgio_notify(self.bot, skin1['uuid'], skin1['name'], skin1['price'], skin1['icon'])
                        embed2 = embed_giorgio_notify(self.bot, skin2['uuid'], skin2['name'], skin2['price'], skin2['icon'])
                        embed3 = embed_giorgio_notify(self.bot, skin3['uuid'], skin3['name'], skin3['price'], skin3['icon'])
                        embed4 = embed_giorgio_notify(self.bot, skin4['uuid'], skin4['name'], skin4['price'], skin4['icon'])

                        await channel.send(embeds=[embed, embed1, embed2, embed3, embed4])
                
            except (KeyError, FileNotFoundError):
                pass
            except Exception as e:
                print(f'Notify all error - {e}')

    @notifys.before_loop
    async def before_daily_send(self):
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')
        
def setup(bot):
    bot.add_cog(Notify_(bot))