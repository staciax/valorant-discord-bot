from __future__ import annotations

import asyncio
import logging
import os

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

from .translator import Translator
from .tree import Tree

load_dotenv()

INITIAL_EXTENSIONS = (
    # 'cogs.admin',
    # 'cogs.errors',
    # 'cogs.notify',
    # 'cogs.valorant',
)

log = logging.getLogger(__name__)


class Bot(commands.Bot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo
    tree: Tree
    translator: Translator

    def __init__(self) -> None:
        # intents
        intents = discord.Intents.default()
        # intents.message_content = True

        # allow mentions
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)

        super().__init__(
            [],
            case_insensitive=True,
            intents=intents,
            allowed_mentions=allowed_mentions,
            help_command=None,
            tree_cls=Tree,
        )

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=":)",
            )
        )

        log.info('Ready: %s (ID: %s)', self.user, self.user.id)

    async def on_message(self, message: discord.Message, /) -> None:
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.translator = Translator(self)
        await self.tree.set_translator(self.translator)

        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        await self.cogs_load()

        # await self.tree.sync()

    async def cogs_load(self) -> None:
        await asyncio.gather(*[self.load_extension(extension) for extension in INITIAL_EXTENSIONS])

    async def cogs_unload(self) -> None:
        await asyncio.gather(*[self.unload_extension(extension) for extension in INITIAL_EXTENSIONS])

    async def load_extension(self, name: str, *, package: str | None = None) -> None:
        try:
            await super().load_extension(name, package=package)
        except Exception as e:
            log.error('failed to load extension %s', name, exc_info=e)
            raise e
        else:
            log.info('loaded extension %s', name)

    async def unload_extension(self, name: str, *, package: str | None = None) -> None:
        try:
            await super().unload_extension(name, package=package)
        except Exception as e:
            log.error('failed to unload extension %s', name, exc_info=e)
            raise e
        else:
            log.info('unloaded extension %s', name)

    async def reload_extension(self, name: str, *, package: str | None = None) -> None:
        try:
            await super().reload_extension(name, package=package)
        except Exception as e:
            log.error('failed to reload extension %s', name, exc_info=e)
            raise e
        else:
            log.info('reloaded extension %s', name)

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def start(self) -> None:
        token = os.getenv('DISCORD_TOKEN')
        assert token is not None, 'DISCORD_TOKEN is not set'
        return await super().start(token, reconnect=True)
