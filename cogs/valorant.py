from __future__ import annotations

import contextlib
from typing import Literal, TYPE_CHECKING

from discord import app_commands, Interaction, ui
from discord.ext import commands, tasks
from discord.utils import MISSING

from utils.checks import owner_only
from utils.errors import (
    ValorantBotError
)
from utils.valorant import cache as Cache, useful, view as View
from utils.valorant.db import DATABASE
from utils.valorant.embed import Embed, GetEmbed
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.local import ResponseLanguage
from utils.valorant.resources import setup_emoji
from utils.i18n import ValorantTranslator

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot


class ValorantCog(commands.Cog, name='Valorant'):
    """Valorant API Commands"""

    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        self.endpoint: API_ENDPOINT = None
        self.db: DATABASE = None
        self.reload_cache.start()

    def cog_unload(self) -> None:
        self.reload_cache.cancel()

    def funtion_reload_cache(self, force=False) -> None:
        """ Reload the cache """
        with contextlib.suppress(Exception):
            cache = self.db.read_cache()
            valorant_version = Cache.get_valorant_version()
            if valorant_version != cache['valorant_version'] or force:
                Cache.get_cache()
                cache = self.db.read_cache()
                cache['valorant_version'] = valorant_version
                self.db.insert_cache(cache)
                print('Updated cache')

    @tasks.loop(minutes=30)
    async def reload_cache(self) -> None:
        """ Reload the cache every 30 minutes """
        self.funtion_reload_cache()

    @reload_cache.before_loop
    async def before_reload_cache(self) -> None:
        """ Wait for the bot to be ready before reloading the cache """
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ When the bot is ready """
        self.db = DATABASE()
        self.endpoint = API_ENDPOINT()

    async def get_endpoint(self, user_id: int, locale_code: str = None, username: str = None, password: str = None) -> API_ENDPOINT:
        """ Get the endpoint for the user """
        if username is not None and password is not None:
            auth = self.db.auth
            auth.locale_code = locale_code
            data = await auth.temp_auth(username, password)
        elif username or password:
            raise ValorantBotError(f"Please provide both username and password!")
        else:
            data = await self.db.is_data(user_id, locale_code)
        data['locale_code'] = locale_code
        endpoint = self.endpoint
        endpoint.activate(data)
        return endpoint

    @app_commands.command(description='Log in with your Riot acoount')
    @app_commands.describe(username='Input username', password='Input password')
    # @dynamic_cooldown(cooldown_5s)
    async def login(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24],
        password: app_commands.Range[str, 1, 128]
    ) -> None:
        ...

    @app_commands.command(description='Logout and Delete your account from database')
    # @dynamic_cooldown(cooldown_5s)
    async def logout(self, interaction: Interaction) -> None:
        ...

    @app_commands.command(description="Shows your daily store in your accounts")
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def store(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24] = None,
        password: app_commands.Range[str, 1, 128] = None
    ) -> None:
        ...

    @app_commands.command(description='View your remaining Valorant and Riot Points (VP/RP)')
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def point(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24] = None,
        password: app_commands.Range[str, 1, 128] = None
    ) -> None:
        ...

    @app_commands.command(description='View your daily/weekly mission progress')
    # @dynamic_cooldown(cooldown_5s)
    async def mission(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24] = None,
        password: app_commands.Range[str, 1, 128] = None
    ) -> None:
        ...

    @app_commands.command(description='Show skin offers on the nightmarket')
    # @dynamic_cooldown(cooldown_5s)
    async def nightmarket(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24] = None,
        password: app_commands.Range[str, 1, 128] = None
    ) -> None:
        ...

    @app_commands.command(description='View your battlepass current tier')
    # @dynamic_cooldown(cooldown_5s)
    async def battlepass(
        self,
        interaction: Interaction,
        username: app_commands.Range[str, 1, 24] = None,
        password: app_commands.Range[str, 1, 128] = None
    ) -> None:
        ...

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="inspect a specific bundle")
    @app_commands.describe(bundle="The name of the bundle you want to inspect!")
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def bundle(self, interaction: Interaction, bundle: str) -> None:
        ...

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Show the current featured bundles")
    # @dynamic_cooldown(cooldown_5s)
    async def bundles(self, interaction: Interaction) -> None:
        ...

    # credit https://github.com/giorgi-o
    # https://github.com/giorgi-o/SkinPeek/wiki/How-to-get-your-Riot-cookies
    @app_commands.command()
    @app_commands.describe(cookie="Your cookie")
    async def cookies(self, interaction: Interaction, cookie: str) -> None:
        ...

    # ---------- DEBUGs ---------- #

    @app_commands.command(description='The command debug for the bot')
    @app_commands.describe(bug="The bug you want to fix")
    @app_commands.guild_only()
    @owner_only()
    async def debug(self, interaction: Interaction, bug: Literal['Skin price not loading', 'Emoji not loading', 'Cache not loading']) -> None:
        ...


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(ValorantCog(bot))
