import asyncio
import datetime
import logging
import os
from typing import Any

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

from .translator import Translator
from .tree import Tree

load_dotenv()

log = logging.getLogger(__name__)

description = 'A valorant bot made by discord: stacia.(240059262297047041)'

INITIAL_EXTENSIONS = (
    # 'cogs.about',
    # 'cogs.admin',
    # 'cogs.errors',
    # 'cogs.events',
    # 'cogs.help',
    # 'cogs.stats',
    # 'cogs.test',
    # 'cogs.valorant',
    # 'cogs.ipc', # someday maybe
)

INVITE_PERMISSIONS = 280576


class Bot(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo
    tree: Tree
    session: aiohttp.ClientSession

    def __init__(self) -> None:
        # intents
        intents = discord.Intents.none()
        intents.guilds = True
        intents.emojis_and_stickers = True
        # intents.dm_messages = True

        # allowed_mentions
        allowed_mentions = discord.AllowedMentions(
            roles=False,
            everyone=False,
            replied_user=False,
            users=True,
        )

        super().__init__(
            command_prefix=[],
            help_command=None,
            allowed_mentions=allowed_mentions,
            case_insensitive=True,
            intents=intents,
            description=description,
            enable_debug_events=True,
            tree_cls=Tree,
            activity=discord.Activity(type=discord.ActivityType.listening, name='valorant bot ♡ ₊˚'),
        )
        self.support_guild_id: int = 1097859504906965042
        self.support_invite_url: str = 'https://discord.gg/mKysT7tr2v'

        # self.db: DatabaseConnection = DatabaseConnection('sqlite:///database.db')

    @property
    def owner(self) -> discord.User:
        """Returns the bot owner."""
        return self.bot_app_info.owner

    @property
    def support_guild(self) -> discord.Guild | None:
        if self.support_guild_id is None:
            raise ValueError('Support guild ID is not set.')
        return self.get_guild(self.support_guild_id)

    # @property
    # def valorant(self) -> commands.Cog | None:
    #     return self.get_cog('valorant')

    def get_invite_url(self) -> str:
        scopes = ('bot', 'applications.commands')  # reportArgumentType
        permissions = discord.Permissions(INVITE_PERMISSIONS)
        return discord.utils.oauth_url(
            self.application_id,  # type: ignore[reportArgumentType]
            permissions=permissions,
            scopes=scopes,
        )

    # setuphook

    async def cogs_load(self) -> None:
        await asyncio.gather(*[self.load_extension(extension) for extension in INITIAL_EXTENSIONS])

    async def cogs_unload(self) -> None:
        await asyncio.gather(*[self.unload_extension(extension) for extension in INITIAL_EXTENSIONS])

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        self.translator = Translator(self)
        await self.tree.set_translator(self.translator)

        self.bot_app_info = await self.application_info()
        self.owner_ids = [self.bot_app_info.owner.id]

        await self.cogs_load()
        # await self.tree.insert_model_to_commands()

    async def on_ready(self) -> None:
        if not hasattr(self, 'launch_time'):
            self.launch_time: datetime.datetime = datetime.datetime.now()

        log.info(
            f'logged in as: {self.user} '
            + (f'activity: {self.activity.name} ' if self.activity is not None else '')
            + f'servers: {len(self.guilds)} '
            + f'users: {sum(guild.member_count for guild in self.guilds if guild.member_count is not None)}'
        )

    async def on_message(self, message: discord.Message, /) -> None:
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        log.exception('Ignoring exception in %s', event_method)

    async def tree_sync(self, guild_only: bool = False) -> None:
        # tree sync application commands
        if not guild_only:
            await self.tree.sync()
        sync_guilds = [self.support_guild_id]
        for guild_id in sync_guilds:
            try:
                await self.tree.sync(guild=discord.Object(id=guild_id))
            except Exception as e:
                log.error(f'Failed to sync guild {guild_id}.', exc_info=e)

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
        await self.cogs_unload()
        await self.session.close()
        await super().close()

    async def start(self) -> None:
        token = os.getenv('DISCORD_TOKEN')
        if token is None:
            raise RuntimeError('No token provided.')
        await super().start(token=token, reconnect=True)
