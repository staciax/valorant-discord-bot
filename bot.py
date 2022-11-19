from __future__ import annotations

import asyncio
import os
import sys
import traceback

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, ExtensionNotFound, NoEntryPointError
from dotenv import load_dotenv

from utils.valorant.cache import get_cache

load_dotenv()

initial_extensions = ['cogs.admin', 'cogs.errors', 'cogs.notify', 'cogs.valorant']


class ValorantBot(commands.Bot):
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:

        # intents required
        intents = discord.Intents.default()

        super().__init__(command_prefix=[], case_insensitive=True, intents=intents)
        self.session: aiohttp.ClientSession = discord.utils.MISSING
        self._version = '4.0.0dev0'
        self._activity_status = ''
        self._activity_type = discord.ActivityType.listening
        # self.tree.interaction_check = self.interaction_check

    # @staticmethod
    # async def interaction_check(interaction: discord.Interaction) -> bool:
    #     return True

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        await self.tree.sync()

        # bot presence
        activity_type = discord.ActivityType.listening
        await self.change_presence(activity=discord.Activity(type=activity_type, name=self._activity_status))

    async def setup_hook(self) -> None:

        if self.session is discord.utils.MISSING:
            self.session = aiohttp.ClientSession()

        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

        await self.load_cogs()

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

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def start(self) -> None:
        if discord_token := os.getenv('TOKEN'):
            await super().start(discord_token, reconnect=True)
        else:
            raise ValueError('No token provided.')

async def run_bot() -> None:
    bot = ValorantBot()
    async with bot:
        await bot.start()

if __name__ == '__main__':
    asyncio.run(run_bot())
