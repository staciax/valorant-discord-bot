import discord
import contextlib
from discord.ext import commands, tasks
from discord import Interaction, app_commands, ui
from typing import Literal
from discord.utils import MISSING

# Local
from utils.valorant import (
    get_season_by_content,
    Embed,
    Generate_Embed,
    TwoFA_UI,
    BaseBundle,
    share_button,
    InteractionLanguage,
    ResponseLanguage,
    get_cache,
    get_valorant_version,
    setup_emoji,
    API_ENDPOINT,
    DATABASE,
)

def owner_only() -> app_commands.check:
    async def predicate(interaction: Interaction):
        return await interaction.client.is_owner(interaction.user)
    return app_commands.check(predicate)

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

    async def get_endpoint(self, user_id: int, locale_code: str = None, username:str= None, password: str = None) -> API_ENDPOINT:
        if username is not None and password is not None:
            auth = self.db.auth
            auth.local_code = locale_code
            data = await auth.temp_auth(username, password)
        elif username or password:
            raise RuntimeError(f"Please provide both username and password!")
        else:
            data = await self.db.is_data(user_id, locale_code)
        data['locale_code'] = locale_code
        endpoint = self.endpoint
        await endpoint.activate(data)
        return endpoint

    @app_commands.command(description='Log in with your Riot acoount')
    @app_commands.describe(username='Input username', password='Input password')
    async def login(self, interaction: Interaction, username: str, password: str) -> None:

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        auth = self.db.auth
        auth.locale_code = interaction.locale
        authenticate = await auth.authenticate(username, password)

        if authenticate['auth'] == 'response':
            await interaction.response.defer(ephemeral=True)
            login = await self.db.login(user_id, authenticate, interaction.locale)

            if login['auth']:
                embed = Embed(f"{response.get('SUCCESS')} **{login['player']}!**")
                return await interaction.followup.send(embed=embed, ephemeral=True)

            raise RuntimeError(f"{response.get('FAILED')}")

        elif authenticate['auth'] == '2fa':
            cookies = authenticate['cookie']
            message = authenticate['message']
            label = authenticate['label']
            modal = TwoFA_UI(interaction, self.db, cookies, message, label, response)
            await interaction.response.send_modal(modal)

    @app_commands.command(description='Logout and Delete your account from database')
    async def logout(self, interaction: Interaction) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        if logout := self.db.logout(user_id, interaction.locale):
            if logout:
                embed = Embed(response.get('SUCCESS'))
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            raise RuntimeError(response.get('FAILED'))

    @app_commands.command(description="Shows your daily store in your accounts")
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    @app_commands.guild_only()
    async def store(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)
        
        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        
        await interaction.response.defer(ephemeral=is_private_message)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # get endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # fetch skin price
        skin_price = await endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = await endpoint.store_fetch_storefront()
        embeds = Generate_Embed.store(endpoint.player, data, language, response, self.bot)

        await interaction.followup.send(embeds=embeds, view=share_button(interaction, embeds) if is_private_message else MISSING)

    @app_commands.command(description='View your remaining Valorant and Riot Points (VP/RP)')
    @app_commands.guild_only()
    async def point(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        
        await interaction.response.defer(ephemeral=is_private_message)
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild, interaction.locale)
        
        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, locale_code=interaction.locale)

        # data
        data = await endpoint.store_fetch_wallet()
        embed = Generate_Embed.point(endpoint.player, data, language, response, self.bot)

        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    @app_commands.command(description='View your daily/weekly mission progress')
    async def mission(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # data
        data = await endpoint.fetch_contracts()
        embed = Generate_Embed.mission(endpoint.player, data, language, response)

        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    @app_commands.command(description='Show skin offers on the nightmarket')
    async def nightmarket(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        
        await interaction.response.defer(ephemeral=is_private_message)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # fetch skin price
        skin_price = await endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = await endpoint.store_fetch_storefront()
        embeds = Generate_Embed.nightmarket(endpoint.player, data, self.bot, language, response)

        await interaction.followup.send(embeds=embeds, view=share_button(interaction, embeds) if is_private_message else MISSING)

    @app_commands.command(description='View your battlepass current tier')
    async def battlepass(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # data
        data = await endpoint.fetch_contracts()
        content = await endpoint.fetch_content()
        season = get_season_by_content(content)

        embed = Generate_Embed.battlepass(endpoint.player, data, season, language, response)
        
        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="inspect a specific bundle")
    @app_commands.describe(bundle="The name of the bundle you want to inspect!")
    @app_commands.guild_only()
    async def bundle(self, interaction: Interaction, bundle: str) -> None:
        
        await interaction.response.defer()

        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # setup emoji 
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # cache
        cache = self.db.read_cache()

        # default language language
        default_language = 'en-US'

        # find bundle
        find_bundle_en_US = [cache['bundles'][i] for i in cache['bundles'] if bundle.lower() in cache['bundles'][i]['names'][default_language].lower()]
        find_bundle_locale = [cache['bundles'][i] for i in cache['bundles'] if bundle.lower() in cache['bundles'][i]['names'][language].lower()]
        find_bundle = find_bundle_en_US if len(find_bundle_en_US) > 0 else find_bundle_locale

        # bundle view
        view = BaseBundle(interaction, find_bundle, response, language)
        await view.start()
    
    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Show the current featured bundles")
    async def bundles(self, interaction: Interaction) -> None:

        await interaction.response.defer()
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)

        # data
        bundle_entries = await endpoint.store_fetch_storefront()

        # bundle view
        view = BaseBundle(interaction, bundle_entries, response, language)
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
    @app_commands.command(description='The command debug for the bot')
    @app_commands.describe(bug="The bug you want to fix")
    @app_commands.guild_only()
    @owner_only()
    async def debug(self, interaction: Interaction, bug: Literal['Skin price not loading', 'Emoji not loading', 'Cache not loading']) -> None:

        await interaction.response.defer(ephemeral=True)
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = ResponseLanguage(interaction.command.name, interaction.locale)
        
        if bug == 'Skin price not loading':
            # endpoint
            endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)

            # fetch skin price
            skin_price = await endpoint.store_fetch_offers()
            self.db.insert_skin_price(skin_price, force=True)

        elif bug == 'Emoji not loading':
            await setup_emoji(self.bot, interaction.guild, interaction.locale, force=True)
        
        elif bug == 'Cache not loading':
            self.funtion_reload_cache(force=True)

        success = response.get('SUCCESS')
        await interaction.followup.send(embed=Embed(success.format(bug=bug)))
            
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
        view.add_item(ui.Button(label='ᴅᴇᴠ ᴅɪꜱᴄᴏʀᴅ', url=owner_url, row=0))
        view.add_item(ui.Button(label='ɢɪᴛʜᴜʙ', url=github_project, row=0))
        view.add_item(ui.Button(label='ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ', url=support_url,  row=1))
        view.add_item(ui.Button(label='ᴅᴏɴᴀᴛᴇ', url='https://tipme.in.th/renlyx', row=1))
        view.add_item(ui.Button(label='ᴋᴏ-ꜰɪ', url='https://ko-fi.com/staciax', row=1))

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(ValorantCog(bot))