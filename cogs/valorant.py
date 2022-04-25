import discord
import contextlib
from discord.ext import commands, tasks
from discord import Interaction, app_commands, ui
from datetime import datetime
from typing import Literal
from difflib import get_close_matches

# Local
from utils.valorant.useful import get_season_by_content
from utils.valorant.embed import Embed, embed_store, embed_mission, embed_point, embed_nightmarket, embed_battlepass
from utils.valorant.view import TwoFA_UI, BaseBundle
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.db import DATABASE
from utils.valorant.local import InteractionLanguage, ResponseLanguage
from utils.valorant.cache import get_cache, get_valorant_version
from utils.valorant.resources import setup_emoji

season_id = 'd929bc38-4ab6-7da4-94f0-ee84f8ac141e'
season_end = datetime(2022, 4, 26, 17, 0, 0)
current_season = season_id, season_end

class ValorantCog(commands.Cog, name='Valorant'):
    """Valorant API Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.reload_cache.start()

    def cog_unload(self) -> None:
        self.reload_cache.cancel()

    def funtion_reload_cache(self, force=False):
        with contextlib.suppress(Exception):
            cache = self.db.read_cache()
            valorant_version = get_valorant_version()
            if valorant_version != cache['ValorantVersion'] or force:
                get_cache()
                cache = self.db.read_cache()
                cache['valorant_version'] = valorant_version
                self.db.insert_cache(cache)
                print('Updated cache')

    @tasks.loop(minutes=30)
    async def reload_cache(self) -> None:
        self.funtion_reload_cache()

    @reload_cache.before_loop
    async def before_reload_cache(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.db: DATABASE = self.bot.db
        self.endpoint: API_ENDPOINT = self.bot.endpoint

    async def get_endpoint(self, user_id: int, auth:dict = {}) -> API_ENDPOINT:
        if not auth:
            data = await self.db.is_data(user_id)
        else:
            data = auth
        endpoint = self.endpoint
        await endpoint.activate(data)
        return endpoint

    async def get_temp_auth(self, username: str, password: str):
        auth = self.db.auth
        return await auth.temp_auth(username, password)

    @app_commands.command(description='Log in with your Riot acoount')
    @app_commands.describe(username='Input username', password='Input password')
    async def login(self, interaction: Interaction, username: str, password: str) -> None:

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        user_id = interaction.user.id
        auth = self.db.auth
        auth.language = language
        authenticate = await auth.authenticate(username, password)

        if authenticate['auth'] == 'response':
            await interaction.response.defer(ephemeral=True)
            login = await self.db.login(user_id, authenticate)

            if login['auth']:
                embed = Embed(f"{response.get('SUCCESS', 'Successfully logged in')} **{login['player']}!**")
                return await interaction.followup.send(embed=embed, ephemeral=True)

            raise RuntimeError(f"{response.get('FAILED', 'Failed to log in')}")

        elif authenticate['auth'] == '2fa':
            cookies = authenticate['cookie']
            message = authenticate['message']
            modal = TwoFA_UI(interaction, self.db, cookies, message)
            await interaction.response.send_modal(modal)

    @app_commands.command(description='Logout and Delete your account from database')
    async def logout(self, interaction: Interaction) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        user_id = interaction.user.id
        if logout := self.db.logout(user_id):
            if logout:
                #f"Successfully logged out!"
                embed = Embed(response.get('SUCCESS', 'Successfully logged out!'))
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            raise RuntimeError(response.get('FAILED', 'Failed to logout, plz try again!'))

    @app_commands.command(description="Shows your daily store in your accounts")
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    async def store(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)
        
        # check if user is logged in
        is_private_message = False
        if username is not None and password is not None:
            is_private_message = True

        await interaction.response.defer(ephemeral=is_private_message)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild)

        # endpoint
        if username is None and password is None:  # for user if logged in
            endpoint = await self.get_endpoint(interaction.user.id)
        elif username is not None and password is not None: # for quick check store
            temp_auth = await self.get_temp_auth(username, password)
            endpoint = await self.get_endpoint(interaction.user.id, temp_auth)
        elif username or password: 
            raise RuntimeError(f"Please provide both username and password!")

        # fetch skin price
        skin_price = await endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = await endpoint.store_fetch_storefront()
        embeds = embed_store(endpoint.player, data, language, response, self.bot)

        if not is_private_message:
            return await interaction.followup.send(embeds=embeds)
        await interaction.followup.send(content='\u200b')
        await interaction.channel.send(embeds=embeds)

    @app_commands.command(description='View your remaining Valorant and Riot Points (VP/RP)')
    async def point(self, interaction: Interaction) -> None:

        await interaction.response.defer()
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild)
        
        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id)

        # data
        data = await endpoint.store_fetch_wallet()
        embed = embed_point(endpoint.player, data, language, response, self.bot)

        await interaction.followup.send(embed=embed)

    @app_commands.command(description='View your daily/weekly mission progress')
    async def mission(self, interaction: Interaction) -> None:

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id)

        # data
        data = await endpoint.fetch_contracts()
        embed = embed_mission(endpoint.player, data, language, response)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(description='Show skin offers on the nightmarket')
    async def nightmarket(self, interaction: Interaction) -> None:

        await interaction.response.defer()

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild)

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id)

        # fetch skin price
        skin_price = await endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = await endpoint.store_fetch_storefront()
        embeds = embed_nightmarket(endpoint.player, data, language, response)

        await interaction.followup.send(embeds=embeds)

    @app_commands.command(description='View your battlepass current tier')
    async def battlepass(self, interaction: Interaction) -> None:

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id)

        # data
        data = await endpoint.fetch_contracts()
        content = await endpoint.fetch_content()
        season = get_season_by_content(content)
        embed = embed_battlepass(endpoint.player, data, season, language, response)

        await interaction.response.send_message(embed=embed)

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="inspect a specific bundle")
    @app_commands.describe(bundle="The name of the bundle you want to inspect!")
    async def bundle(self, interaction: Interaction, bundle: str) -> None:
        
        await interaction.response.defer()

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild)

        # cache
        cache = self.db.read_cache()

        # default language language
        bundle_language = 'en-US'

        # find bundle
        find_bundle_entries = [cache['bundles'][i] for i in cache['bundles'] if get_close_matches(bundle.lower(), [cache['bundles'][i]['names'][bundle_language].lower()])]
        
        # bundle view
        view = BaseBundle(interaction, find_bundle_entries)
        await view.start()
    
    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Show the current featured bundles")
    async def bundles(self, interaction: Interaction) -> None:

        await interaction.response.defer()
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id)

        # default bundle language
        bundle_language = 'en-US' # or bundle_language = language

        # data
        bundle_entries = await endpoint.store_fetch_storefront()

        # bundle view
        view = BaseBundle(interaction, bundle_entries)
        await view.start_furture()

    # ---------- ROAD MAP ---------- #

    # @app_commands.command()
    # async def contract(self, interaction: Interaction) -> None:
    #     # change agent contract

    # @app_commands.command()
    # async def party(self, interaction: Interaction) -> None:
    #     # curren party
    #     # pick agent
    #     # current map

    # @app_commands.command()
    # async def career(self, interaction: Interaction) -> None:
    #     # match history
    
    # ---------- DEBUGs ---------- #

    # hybird command
    @app_commands.command(description='Command debug for the bot')
    async def debug(self, interaction: Interaction, debug: Literal['Skin Price', 'Emoji not loaded', 'Cache']) -> None:

        await interaction.response.defer(ephemeral=True)
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, language)
        
        if debug == 'Skin Price':
            # endpoint
            endpoint = await self.get_endpoint(interaction.user.id)

            # fetch skin price
            skin_price = await endpoint.store_fetch_offers()
            self.db.insert_skin_price(skin_price, force=True)

            await interaction.response.send_message(embed=Embed(response.get('SUCCESS', 'Successfully updated skin price!')))

        elif debug == 'Emoji':
            await setup_emoji(self.bot, interaction.guild)
            await interaction.response.send_message(embed=Embed(response.get('SUCCESS', 'Successfully updated emoji!')))
        
        elif debug == 'Reload Cache':
            await self.funtion_reload_cache(force=True)
            await interaction.response.send_message(embed=Embed(response.get('SUCCESS', 'Successfully reloaded cache!')))
            
    # ---------- CREDITs ---------- #

    @app_commands.command(description='Shows basic information about the bot.')
    async def about(self, interaction: Interaction) -> None:
        
        owner_id = 240059262297047041
        owner_url = f'https://discord.com/users/{owner_id}'
        github_project = 'https://github.com/staciax/ValorantStoreChecker-discord-bot'
        support_url = 'https://discord.gg/FJSXPqQZgz'
        
        embed = discord.Embed(color=0xffffff)
        embed.set_author(name='ᴠᴀʟᴏʀᴀɴᴛ ʙᴏᴛ ᴘʀᴏᴊᴇᴄᴛ', url=github_project)
        embed.set_thumbnail(url='https://i.imgur.com/ZtuNW0Z.png')
        embed.add_field(
            name='ᴀʙᴏᴜᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ:',
            value=f"ᴏᴡɴᴇʀ: [ꜱᴛᴀᴄɪᴀ.#7475]({owner_url}, '┐(・。・┐) ♪')",
            inline=False
        )
        view = ui.View()
        view.add_item(ui.Button(label='ᴅᴇᴠ ᴅɪꜱᴄᴏʀᴅ', url=owner_url, emoji='<:stacia_icon:948850880617250837>',row=0))
        view.add_item(ui.Button(label='ɢɪᴛʜᴜʙ', url=github_project, emoji='<:github_icon:966706759697842176>', row=0))
        view.add_item(ui.Button(label='ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ', url=support_url, emoji='<:latte_support:941971854728511529>', row=1))
        view.add_item(ui.Button(label='ᴅᴏɴᴀᴛᴇ', url='https://tipme.in.th/renlyx', emoji='<:tipme:967989967697608754>', row=1))
        view.add_item(ui.Button(label='ᴋᴏ-ꜰɪ', url='https://ko-fi.com/staciax', emoji='<:kofi:967989830476779620>', row=1))

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(ValorantCog(bot))