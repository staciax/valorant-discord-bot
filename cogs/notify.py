from __future__ import annotations

import traceback
from datetime import datetime, time, timedelta
from difflib import get_close_matches
from typing import TYPE_CHECKING, Any, Literal, Tuple

# Standard
import discord
from discord import Forbidden, HTTPException, Interaction, app_commands
from discord.ext import commands, tasks

from utils.errors import ValorantBotError
from utils.locale_v2 import ValorantTranslator
from utils.valorant import view as View
from utils.valorant.cache import create_json
from utils.valorant.db import DATABASE
from utils.valorant.embed import Embed, GetEmbed
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.local import ResponseLanguage
from utils.valorant.useful import JSON, GetEmoji, GetItems, format_relative

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot


class Notify(commands.Cog):
    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        self.endpoint: API_ENDPOINT = None
        self.db: DATABASE = None
        self.notifys.start()

    def cog_unload(self) -> None:
        self.notifys.cancel()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.db = DATABASE()
        self.endpoint = API_ENDPOINT()

    async def get_endpoint_and_data(self, user_id: int) -> Tuple[API_ENDPOINT, Any]:
        data = await self.db.is_data(user_id, 'en-US')
        endpoint = self.endpoint
        endpoint.activate(data)
        return endpoint, data

    async def send_notify(self) -> None:
        notify_users = self.db.get_user_is_notify()
        notify_data = JSON.read('notifys')

        for user_id in notify_users:
            try:

                # endpoint
                endpoint, data = await self.get_endpoint_and_data(int(user_id))

                # offer
                offer = endpoint.store_fetch_storefront()
                skin_offer_list = offer["SkinsPanelLayout"]["SingleItemOffers"]
                duration = offer["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]

                # author
                author = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                channel_send = author if data['dm_message'] else self.bot.get_channel(int(data['notify_channel']))

                # get guild language
                guild_locale = 'en-US'
                get_guild_locale = [guild.preferred_locale for guild in self.bot.guilds if channel_send in guild.channels]
                if len(get_guild_locale) > 0:
                    guild_locale = guild_locale[0]

                response = ResponseLanguage('notify_send', guild_locale)

                user_skin_list = [skin for skin in notify_data if skin['id'] == str(user_id)]
                user_skin_list_uuid = [skin['uuid'] for skin in notify_data if skin['id'] == str(user_id)]

                if data['notify_mode'] == 'Specified':
                    skin_notify_list = list(set(skin_offer_list).intersection(set(user_skin_list_uuid)))
                    for noti in user_skin_list:
                        if noti['uuid'] in skin_notify_list:
                            uuid = noti['uuid']
                            skin = GetItems.get_skin(uuid)
                            name = skin['names'][guild_locale]
                            icon = skin['icon']
                            emoji = GetEmoji.tier_by_bot(uuid, self.bot)

                            notify_send: str = response.get('RESPONSE_SPECIFIED')
                            duration = format_relative(datetime.utcnow() + timedelta(seconds=duration))

                            embed = Embed(notify_send.format(emoji=emoji, name=name, duration=duration), color=0xFD4554)
                            embed.set_thumbnail(url=icon)
                            view = View.NotifyView(user_id, uuid, name, ResponseLanguage('notify_add', guild_locale))
                            view.message = await channel_send.send(content=f'||{author.mention}||', embed=embed, view=view)

                elif data['notify_mode'] == 'All':
                    embeds = GetEmbed.notify_all_send(endpoint.player, offer, response, self.bot)
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

    @tasks.loop(time=time(hour=0, minute=0, second=10))  # utc 00:00:15
    async def notifys(self) -> None:
        __verify_time = datetime.utcnow()
        if __verify_time.hour == 0:
            await self.send_notify()

    @notifys.before_loop
    async def before_daily_send(self) -> None:
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')

    notify = app_commands.Group(name='notify', description='Notify commands')

    @notify.command(name='add', description='Set a notification when a specific skin is available on your store')
    @app_commands.describe(skin='The name of the skin you want to notify')
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def notify_add(self, interaction: Interaction, skin: str) -> None:

        await interaction.response.defer()

        await self.db.is_data(interaction.user.id, interaction.locale)  # check if user is in db

        # language

        response = ResponseLanguage('notify_add', interaction.locale)

        # # setup emoji
        # await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # check file whether
        create_json('notifys', [])

        # get cache
        skin_data = self.db.read_cache()

        # find skin
        skin_list = sum(
            [list(skin_data['skins'][x]['names'].values()) for x in skin_data['skins']], []
        )  # get skin list with multilingual names
        skin_name = get_close_matches(skin, skin_list, 1)  # get skin close match

        if skin_name:
            notify_data = JSON.read('notifys')

            find_skin = [x for x in skin_data['skins'] if skin_name[0] in skin_data['skins'][x]['names'].values()]
            skin_uuid = find_skin[0]
            skin_source = skin_data['skins'][skin_uuid]

            name = skin_source['names'][str(VLR_locale)]
            icon = skin_source['icon']
            uuid = skin_source['uuid']

            emoji = GetEmoji.tier_by_bot(skin_uuid, self.bot)

            for skin in notify_data:
                if skin['id'] == str(interaction.user.id) and skin['uuid'] == skin_uuid:
                    skin_already = response.get('SKIN_ALREADY_IN_LIST')
                    raise ValorantBotError(skin_already.format(emoji=emoji, skin=name))

            payload = dict(id=str(interaction.user.id), uuid=skin_uuid)

            try:
                notify_data.append(payload)
                JSON.save('notifys', notify_data)
            except AttributeError:
                notify_data = [payload]
                JSON.save('notifys', notify_data)

            # check if user is notify is on
            userdata = JSON.read('users')
            notify_mode = userdata.get('notify_mode', None)
            if notify_mode is None:
                userdata[str(interaction.user.id)]['notify_mode'] = 'Specified'
                userdata[str(interaction.user.id)]['DM_Message'] = True
                JSON.save('users', userdata)

            success = response.get('SUCCESS')
            embed = Embed(success.format(emoji=emoji, skin=name))
            embed.set_thumbnail(url=icon)

            view = View.NotifyView(interaction.user.id, uuid, name, response)
            await interaction.followup.send(embed=embed, view=view)
            return

        raise ValorantBotError(response.get('NOT_FOUND'))

    @notify.command(name='list', description='View skins you have set a for notification.')
    # @dynamic_cooldown(cooldown_5s)
    async def notify_list(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

        response = ResponseLanguage('notify_list', interaction.locale)

        await self.db.is_data(interaction.user.id, interaction.locale)  # check if user is in db
        view = View.NotifyViewList(interaction, response)
        await view.start()

    @notify.command(name='mode', description='Change notification mode/channel.')
    @app_commands.describe(mode='Select the mode you want to change.')
    # @dynamic_cooldown(cooldown_5s)
    async def notify_mode(self, interaction: Interaction, mode: Literal['Specified Skin', 'All Skin', 'Off']) -> None:

        await interaction.response.defer(ephemeral=True)

        # language
        response = ResponseLanguage('notify_mode', interaction.locale)

        await self.db.is_data(interaction.user.id, interaction.locale)  # check if user is in db

        if mode == 'Specified Skin':  # Check notify list if use mode specified skin
            self.db.check_notify_list(interaction.user.id)  # check total notify list

        self.db.change_notify_mode(interaction.user.id, mode)  # change notify mode

        success = response.get("SUCCESS")
        turn_off = response.get("TURN_OFF")

        embed = Embed(success.format(mode=mode))
        if mode == 'Specified Skin':
            embed.set_image(url='https://i.imgur.com/RF6fHRY.png')
        elif mode == 'All Skin':
            embed.set_image(url='https://i.imgur.com/Gedqlzc.png')
        elif mode == 'Off':
            embed.description = turn_off

        await interaction.followup.send(embed=embed, ephemeral=True)

    @notify.command(name='channel', description='Change notification channel.')
    @app_commands.describe(channel='Select the channel you want to change.')
    # @dynamic_cooldown(cooldown_5s)
    async def notify_channel(self, interaction: Interaction, channel: Literal['DM Message', 'Channel']) -> None:

        await interaction.response.defer(ephemeral=True)

        # language
        response = ResponseLanguage('notify_channel', interaction.locale)

        await self.db.is_data(interaction.user.id, interaction.locale)  # check if user is in db

        self.db.check_notify_list(interaction.user.id)  # check total notify list
        self.db.change_notify_channel(interaction.user.id, channel, interaction.channel_id)  # change notify channel

        channel = '**DM Message**' if channel == 'DM Message' else f'{interaction.channel.mention}'

        embed = discord.Embed(description=response.get('SUCCESS').format(channel=channel), color=0x77DD77)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @notify.command(name='test', description='Testing notification')
    # @dynamic_cooldown(cooldown_5s)
    async def notify_test(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

        # language
        response_test = ResponseLanguage('notify_test', interaction.locale)
        response_send = ResponseLanguage('notify_send', interaction.locale)
        response_add = ResponseLanguage('notify_add', interaction.locale)

        # notify list
        notify_data = JSON.read('notifys')

        # get user data and offer
        endpoint, data = await self.get_endpoint_and_data(int(interaction.user.id))
        offer = endpoint.store_fetch_storefront()

        # offer data
        duration = offer["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
        user_skin_list = [skin for skin in notify_data if skin['id'] == str(interaction.user.id)]

        if len(user_skin_list) == 0:
            empty_list = response_test.get('EMPTY_LIST')
            raise ValorantBotError(empty_list)

        channel_send = interaction.user if data['dm_message'] else self.bot.get_channel(int(data['notify_channel']))

        try:
            if data['notify_mode'] == 'Specified':
                for notify in user_skin_list:
                    uuid = notify['uuid']
                    skin = GetItems.get_skin(uuid)

                    name = skin['names'][str(VLR_locale)]
                    icon = skin['icon']
                    emoji = GetEmoji.tier_by_bot(uuid, self.bot)

                    notify_send: str = response_send.get('RESPONSE_SPECIFIED')
                    duration = format_relative(datetime.utcnow() + timedelta(seconds=duration))

                    embed = Embed(notify_send.format(emoji=emoji, name=name, duration=duration), color=0xFD4554)
                    embed.set_thumbnail(url=icon)
                    view = View.NotifyView(interaction.user.id, uuid, name, response_add)
                    view.message = await channel_send.send(embed=embed, view=view)
                    break

            elif data['notify_mode'] == 'All':
                embeds = GetEmbed.notify_all_send(endpoint.player, offer, response_send, self.bot)
                await channel_send.send(embeds=embeds)

            else:
                raise ValorantBotError(response_test.get('NOTIFY_TURN_OFF'))

        except Forbidden:
            if channel_send == interaction.user:
                raise ValorantBotError(response_test.get('PLEASE_ALLOW_DM_MESSAGE'))
            raise ValorantBotError(response_test.get('BOT_MISSING_PERM'))
        except HTTPException:
            raise ValorantBotError(response_test.get('FAILED_SEND_NOTIFY'))
        except Exception as e:
            print(e)
            raise ValorantBotError(f"{response_test.get('FAILED_SEND_NOTIFY')} - {e}")
        else:
            await interaction.followup.send(
                embed=Embed(response_test.get('NOTIFY_IS_WORKING'), color=0x77DD77), ephemeral=True
            )

    # @notify.command(name='manage', description='Manage notification list.')
    # @owner_only()
    # async def notify_manage(self, interaction: Interaction) -> None:
    #     ...


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Notify(bot))
