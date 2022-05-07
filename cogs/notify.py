# Standard
import discord
import traceback
from discord import Interaction, app_commands, HTTPException, Forbidden
from discord.ext import commands, tasks
from datetime import time, timedelta
from datetime import datetime
from difflib import get_close_matches
from typing import Literal, Tuple

# Local
from utils.valorant import (
    Embed,
    Generate_Embed,
    GetItems,
    GetEmoji,
    JSON,
    DateUtils, 
    InteractionLanguage,
    ResponseLanguage, 
    DATABASE,
    API_ENDPOINT, 
    NotifyViewList,
    NotifyView,
    create_json, 
    setup_emoji,
    LocalErrorResponse
)

class Notify(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.notifys.start()

    def cog_unload(self) -> None:
        self.notifys.cancel()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.db: DATABASE = self.bot.db
        self.endpoint: API_ENDPOINT = self.bot.endpoint

    async def get_endpoint_and_data(self, user_id: int) -> Tuple[API_ENDPOINT, dict]:
        data = await self.db.is_data(user_id)
        endpoint = self.endpoint
        await endpoint.activate(data)
        return endpoint, data

    async def send_notify(self) -> None:
        notify_users = self.db.get_user_is_notify()
        notify_data = JSON.read('notifys')
        
        for user_id in notify_users:
            try:
                # get guild language
                # guild_locale = [guild.preferred_locale for guild in self.bot.guilds if channel in guild.channels]
                # if not guild_locale: guild_locale = ['en-US']
                
                # endpoint
                endpoint, data = await self.get_endpoint_and_data(int(user_id))
                
                # offer
                offer = await endpoint.store_fetch_storefront()
                skin_offer_list = offer["SkinsPanelLayout"]["SingleItemOffers"]
                duration = offer["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
                
                # auhor
                author = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                channel_send = author if data['dm_message'] else self.bot.get_channel(int(data['notify_channel']))
                
                # language response
                try:
                    locale_code = data['locale_code']
                except KeyError:
                    locale_code = 'en-US'
                
                language = InteractionLanguage(locale_code)
                response = ResponseLanguage('notify_send', locale_code)

                user_skin_list = [skin for skin in notify_data if skin['id'] == str(user_id)]
                user_skin_list_uuid = [skin['uuid'] for skin in notify_data if skin['id'] == str(user_id)]

                if data['notify_mode'] == 'Specified':
                    skin_notify_list = list(set(skin_offer_list).intersection(set(user_skin_list_uuid)))
                    for noti in user_skin_list:
                        if noti['uuid'] in skin_notify_list:
                            uuid = noti['uuid']
                            skin = GetItems.get_skin(uuid)
                            name = skin['names'][language]
                            icon = skin['icon']
                            emoji = GetEmoji.tier_by_bot(uuid, self.bot)

                            notify_send:str = response.get('RESPONSE_SPECIFIED')
                            duration = DateUtils.format_relative(datetime.utcnow() + timedelta(seconds=duration))

                            embed = Embed(notify_send.format(emoji=emoji, name=name, duration=duration), color=0xfd4554)
                            embed.set_thumbnail(url=icon)
                            view = NotifyView(user_id, uuid, name, ResponseLanguage('notify_add', locale_code))
                            view.message = await channel_send.send(content=f'||{author.mention}||', embed=embed, view=view)
                
                elif data['notify_mode'] == 'All':
                    embeds = Generate_Embed.notify_all_send(endpoint.player, offer, language, response, self.bot)
                    await channel_send.send(content=f'||{author.mention}||', embeds=embeds)
            
            except (KeyError, FileNotFoundError):
                print(f'{user_id} is not in notify list')
            except Forbidden:
                print("Bot don't have perm send notification message.")
                continue
            except HTTPException:
                print("Bot Can't send notification message.")
                continue
            except Exception as e:
                print(e)
                traceback.print_exception(type(e), e, e.__traceback__)
                continue

    @tasks.loop(time=time(hour=0, minute=0, second=10)) #utc 00:00:15
    # @tasks.loop(seconds=10)
    async def notifys(self) -> None:
        __verify_time = datetime.utcnow()
        if __verify_time.hour == 0 and __verify_time.minute <= 10:
            await self.send_notify()
        
    @notifys.before_loop
    async def before_daily_send(self) -> None:
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')

    notify = app_commands.Group(name='notify', description='Notify commands')

    @notify.command(name='add', description='Set a notification when a specific skin is available on your store')
    @app_commands.describe(skin='The name of the skin you want to notify')
    @app_commands.guild_only()
    async def notify_add(self, interaction: Interaction, skin: str) -> None:

        await interaction.response.defer()

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage('notify_add', interaction.locale)

        # # setup emoji 
        # await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # check file if or not
        create_json('notifys', [])
        
        # get cache
        skindata = self.db.read_cache()

        # find skin
        skin_list = [skindata['skins'][x]['names'][language] for x in skindata['skins']] # get skin list
        skin_name = get_close_matches(skin, skin_list, 1) # get skin close match

        if skin_name:
            notify_data = JSON.read('notifys')

            find_skin = [x for x in skindata['skins'] if skindata['skins'][x]['names'][language] == skin_name[0]]
            skin_uuid = find_skin[0]
            skin_source = skindata['skins'][skin_uuid]

            name = skin_source['names'][language]
            icon = skin_source['icon']
            uuid = skin_source['uuid']

            emoji = GetEmoji.tier_by_bot(skin_uuid, self.bot)

            for skin in notify_data:
                if skin['id'] == str(interaction.user.id) and skin['uuid'] == skin_uuid:
                    skin_already = response.get('SKIN_ALREADY_IN_LIST')
                    raise RuntimeError(skin_already.format(emoji=emoji, skin=name))

            payload = dict(id=str(interaction.user.id), uuid=skin_uuid)

            try:
                notify_data.append(payload)
                JSON.save('notifys', notify_data)
            except AttributeError:
                notify_data = [payload]
                JSON.save('notifys', notify_data)

            # check if user is notify is on
            userdata = JSON.read('users') 
            notify_mode = userdata.get('notify_mode')
            if notify_mode is None:
                userdata[str(interaction.user.id)]['notify_mode'] = 'Specified'
                userdata[str(interaction.user.id)]['DM_Message'] = True
                JSON.save('users', userdata)

            success = response.get('SUCCESS')
            embed = Embed(success.format(emoji=emoji, skin=name))
            embed.set_thumbnail(url=icon)

            view = NotifyView(interaction.user.id, uuid, name, response)
            await interaction.followup.send(embed=embed, view=view)
            return

        raise RuntimeError("Not found skin")
    
    @notify.command(name='list', description='View skins you have set a for notification.')
    async def notify_list(self, interaction: Interaction) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage('notify_list', interaction.locale)

        await self.db.is_data(interaction.user.id) # check if user is in db
        view = NotifyViewList(interaction, response)
        await view.start()

    @notify.command(name='mode', description='Change notification mode/channel.')
    @app_commands.describe(mode='Select the mode you want to change.')
    async def notify_mode(self, interaction: Interaction,  mode: Literal['Specified Skin','All Skin', 'Off']) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage('notify_mode', interaction.locale)
        db_response = LocalErrorResponse('DATABASE', interaction.locale)
 
        await self.db.is_login(interaction.user.id, db_response) # check if user is logged in
        self.db.check_notify_list(interaction.user.id) # check total notify list
        self.db.change_notify_mode(interaction.user.id, mode) # change notify mode

        success = response.get("SUCCESS")
        turn_off = response.get("TURN_OFF")

        embed = Embed(success.format(mode=mode))
        if mode == 'Specified Skin':
            embed.set_image(url='https://i.imgur.com/RF6fHRY.png')
        elif mode == 'All Skin':
            embed.set_image(url='https://i.imgur.com/Gedqlzc.png')
        elif mode == 'Off':
            embed.description = turn_off
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @notify.command(name='channel', description='Change notification channel.')
    @app_commands.describe(channel='Select the channel you want to change.')
    async def notify_channel(self, interaction: Interaction, channel: Literal['DM Message', 'Channel']) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage('notify_channel', interaction.locale)
        db_response = LocalErrorResponse('DATABASE', interaction.locale)
 
        await self.db.is_login(interaction.user.id, db_response) # check if user is logged in
        self.db.check_notify_list(interaction.user.id) # check total notify list
        self.db.change_notify_channel(interaction.user.id, channel, interaction.channel_id) # change notify channel
        
        channel = '**DM Message**' if channel == 'DM Message' else f'{interaction.channel.mention}'

        embed = discord.Embed(description=response.get('SUCCESS').format(channel=channel), color=0x77dd77)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @notify.command(name='test', description='Testing notification')
    async def notify_test(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

        # language
        language = InteractionLanguage(interaction.locale)
        response_test = ResponseLanguage('notify_test', interaction.locale)
        response_send = ResponseLanguage('notify_send', interaction.locale)
        response_add = ResponseLanguage('notify_add', interaction.locale)

        # notify list
        notify_data = JSON.read('notifys')
        
        # get user data and offer
        endpoint, data = await self.get_endpoint_and_data(int(interaction.user.id))
        offer = await endpoint.store_fetch_storefront()

        # offer data
        duration = offer["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
        user_skin_list = [skin for skin in notify_data if skin['id'] == str(interaction.user.id)]
        
        if len(user_skin_list) == 0:
            empty_list = response_test.get('EMPTY_LIST')
            raise RuntimeError(empty_list)

        channel_send = interaction.user if data['dm_message'] else self.bot.get_channel(int(data['notify_channel']))
        
        try:
            if data['notify_mode'] == 'Specified':
                for noti in user_skin_list:
                    uuid = noti['uuid']
                    skin = GetItems.get_skin(uuid)

                    name = skin['names'][language]
                    icon = skin['icon']
                    emoji = GetEmoji.tier_by_bot(uuid, self.bot)

                    notify_send:str = response_send.get('RESPONSE_SPECIFIED')
                    duration = DateUtils.format_relative(datetime.utcnow() + timedelta(seconds=duration))

                    embed = Embed(notify_send.format(emoji=emoji, name=name, duration=duration), color=0xfd4554)
                    embed.set_thumbnail(url=icon)
                    view = NotifyView(interaction.user.id, uuid, name, response_add)
                    view.message = await channel_send.send(embed=embed, view=view)
                    break
            
            elif data['notify_mode'] == 'All':
                embeds = Generate_Embed.notify_all_send(endpoint.player, offer, language, response_send, self.bot)
                await channel_send.send(embeds=embeds)
             
            else:
                raise RuntimeError(response_test.get('NOTIFY_TURN_OFF'))
        
        except Forbidden:
            if channel_send == interaction.user:
                raise RuntimeError(response_test.get('PLEASE_ALLOW_DM_MESSAGE'))
            else:
                raise RuntimeError(response_test.get('BOT_MISSING_PERM'))
        except HTTPException:
            raise RuntimeError(response_test.get('FAILED_SEND_NOTIFY'))
        except Exception as e:
            print(e)
            raise RuntimeError(f"{response_test.get('FAILED_SEND_NOTIFY')} - {e}")
        else:
            await interaction.followup.send(embed=Embed(response_test.get('NOTIFY_IS_WORKING'), color=0x77dd77), ephemeral=True)
    
async def setup(bot) -> None:
    await bot.add_cog(Notify(bot))