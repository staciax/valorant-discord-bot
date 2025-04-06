from __future__ import annotations

import asyncio
import os
import sys
import traceback

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, ExtensionNotFound, NoEntryPointError

from utils import locale_v2
from utils.valorant.cache import get_cache

initial_extensions = ['cogs.admin', 'cogs.errors', 'cogs.notify', 'cogs.valorant']

# intents required
intents = discord.Intents.default()
intents.message_content = True

BOT_PREFIX = '-'

# todo claer white space


class ValorantBot(commands.Bot):
    debug: bool
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)
        self.session: aiohttp.ClientSession | None = None
        self.bot_version = '3.6.0'
        self.tree.interaction_check = self.interaction_check  # type: ignore[method-assign]

    @staticmethod
    async def interaction_check(interaction: discord.Interaction) -> bool:
        locale_v2.set_interaction_locale(
            interaction.locale  # type: ignore[arg-type]
        )  # bot responses localized # wait for update # type: ignore[arg-type]
        locale_v2.set_valorant_locale(interaction.locale)  # type: ignore[arg-type]
        return True

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        await self.tree.sync()
        print(f'\nLogged in as: {self.user}\n\n BOT IS READY !')
        print(f'Version: {self.bot_version}')

        # bot presence
        activity_type = discord.ActivityType.listening
        await self.change_presence(activity=discord.Activity(type=activity_type, name='(╯•﹏•╰)'))

    async def setup_hook(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        try:
            self.owner_id = int(os.getenv('OWNER_ID'))  # type: ignore
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

        self.setup_cache()
        await self.load_cogs()
        # await self.tree.sync()

    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
            except (
                ExtensionNotFound,
                NoEntryPointError,
                ExtensionFailed,
            ):
                print(f'Failed to load extension {ext}.', file=sys.stderr)
                traceback.print_exc()

    @staticmethod
    def setup_cache() -> None:
        try:
            with open('data/cache.json', encoding='utf-8'):
                ...
        except FileNotFoundError:
            get_cache()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await super().close()

    async def start(self, debug: bool = False) -> None:  # type: ignore[override]
        self.debug = debug
        return await super().start(os.getenv('DISCORD_TOKEN'), reconnect=True)  # type: ignore


def run_bot() -> None:
    bot = ValorantBot()
    asyncio.run(bot.start())


if __name__ == '__main__':
    run_bot()
