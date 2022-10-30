from __future__ import annotations

import os
import sys
import traceback

import aiohttp
import discord
from datetime import datetime
from discord import utils
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, ExtensionNotFound, NoEntryPointError
from dotenv import load_dotenv

from utils.i18n import Translator

load_dotenv()
class ValorantBot(commands.Bot):
    """ Discord bot that shows your infomation and more without opening VALORANT by using the (kind-of-private-)game API. """
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:

        # intents
        intents = discord.Intents.default()

        # allowed_mentions
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)


        super().__init__(
            command_prefix=[],
            help_command=None,
            case_insensitive=True,
            intents=intents,
            allowed_mentions=allowed_mentions,
        )

        # bot stuff
        self.launch_time = f'<t:{round(datetime.now().timestamp())}:R>'
        self.version = '4.0.0a'

        # bot theme
        self.theme_primacy = 0xffffff
        self.theme_secondary = 0x111111

        # bot invite link
        self.invite_permission = 280576
        self.invite_url = discord.utils.oauth_url(
            self.application_id,
            permissions=discord.Permissions(self.invite_permission),
        )

        # i18n stuff
        self.translator: Translator = utils.MISSING

        # http session stuff
        self.session: aiohttp.ClientSession = utils.MISSING

        # extensions
        self.initial_extensions = [
            'cogs.admin',
            'cogs.errors',
            'cogs.valorant'
        ]

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:

        print(f"Logged in as: {self.user}", end='\n')
        print(f"Version: {self.version}", end='\n')

        # bot presence
        activity_text = f"valorant v{self.version}"
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=activity_text,
            )
        )

    async def setup_hook(self) -> None:

        # session
        if self.session is utils.MISSING:
            self.session = aiohttp.ClientSession()

        # i18n
        if self.translator is utils.MISSING:
            self.translator = Translator()
            await self.tree.set_translator(self.translator)

        # bot info
        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

        # load cogs
        await self.load_cogs()

        # tree sync application commands
        await self.tree.sync()

    async def load_cogs(self) -> None:
        for ext in self.initial_extensions:
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
        return await super().start(os.getenv('TOKEN'), reconnect=True)
