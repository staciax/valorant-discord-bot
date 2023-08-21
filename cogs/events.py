from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from core.bot import Bot

log = logging.getLogger(__name__)


class Events(commands.Cog, name='events'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot:
            return

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info('Joined guild: %s (ID: %s)', guild.name, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        log.info('Left guild: %s (ID: %s)', guild.name, guild.id)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Events(bot))
