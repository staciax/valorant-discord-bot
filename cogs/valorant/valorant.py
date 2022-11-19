from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING

from utils.checks import owner_only, cooldown_5s
from utils.errors import ValorantBotError
from discord.app_commands.checks import dynamic_cooldown
from discord.app_commands import locale_str as T_

from .notify import Notify

if TYPE_CHECKING:
    from bot import ValorantBot


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    This allows the metaclass used for proper type detection to
    coexist with discord.py's metaclass
    """

    pass


class Valorant(Notify, commands.Cog, metaclass=CompositeMetaClass):
    """Valorant API Commands"""

    def __init__(self, bot: ValorantBot) -> None:
        super().__init__()
        self.bot: ValorantBot = bot
        self.db: Optional[Any] = None

    async def cog_load(self) -> None:
        self.reload_cache_task.start()
        self.notify_task.start()

    async def cog_unload(self) -> None:
        self.reload_cache_task.cancel()
        self.notify_task.cancel()

    def reload_cache(self, force=False) -> None:
        ...

    @tasks.loop(minutes=30)
    async def reload_cache_task(self) -> None:
        self.reload_cache()

    @reload_cache_task.before_loop
    async def before_reload_cache(self) -> None:
        """Wait for the bot to be ready before reloading the cache"""
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        ...

    async def get_valorant_user(self) -> None:
        ...

    @app_commands.command(description=T_('Log in with your Riot acoount'))
    @app_commands.describe(username=T_('Input username'), password=T_('Input password'))
    @dynamic_cooldown(cooldown_5s)
    async def login(self, interaction: Interaction, username: str, password: str) -> None:
        ...
        # await interaction.response.defer(ephemeral=True)

    @app_commands.command(description=T_('Logout and Delete your account from database'))
    @dynamic_cooldown(cooldown_5s)
    async def logout(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        ...

    @app_commands.command(description=T_("Shows your daily store in your accounts"))
    @app_commands.describe(username=T_('Input username (without login)'), password=T_('password (without login)'))
    @app_commands.guild_only()
    @dynamic_cooldown(cooldown_5s)
    async def store(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        ...

    @app_commands.command(description=T_('View your remaining Valorant and Riot Points (VP/RP)'))
    @app_commands.guild_only()
    @dynamic_cooldown(cooldown_5s)
    async def point(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        ...

    @app_commands.command(description=T_('View your daily/weekly mission progress'))
    @dynamic_cooldown(cooldown_5s)
    async def mission(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        ...

    @app_commands.command(description=T_('Show skin offers on the nightmarket'))
    @dynamic_cooldown(cooldown_5s)
    async def nightmarket(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        ...

    @app_commands.command(description=T_('View your battlepass current tier'))
    @dynamic_cooldown(cooldown_5s)
    async def battlepass(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        ...

    @app_commands.command(description=T_("inspect a specific bundle"))
    @app_commands.describe(bundle=T_("The name of the bundle you want to inspect!"))
    @app_commands.guild_only()
    @dynamic_cooldown(cooldown_5s)
    async def bundle(self, interaction: Interaction, bundle: str) -> None:

        await interaction.response.defer()

    @app_commands.command(description=T_("Show the current featured bundles"))
    @dynamic_cooldown(cooldown_5s)
    async def bundles(self, interaction: Interaction) -> None:

        await interaction.response.defer()

    @app_commands.command()
    @app_commands.describe(cookie=T_("Your cookie"))
    async def cookies(self, interaction: Interaction, cookie: str) -> None:
        ...

    @app_commands.command(description=T_('The command debug for the bot'))
    @app_commands.describe(bug=T_("The bug you want to fix"))
    @app_commands.guild_only()
    @owner_only()
    async def debug(
        self, interaction: Interaction, bug: Literal['Skin price not loading', 'Emoji not loading', 'Cache not loading']
    ) -> None:
        await interaction.response.defer(ephemeral=True)


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Valorant(bot))
