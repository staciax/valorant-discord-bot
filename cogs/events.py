from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from discord.app_commands import Command, ContextMenu

    from core.bot import Bot

log = logging.getLogger(__name__)


class Events(commands.Cog, name='events'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction[Bot],
        app_command: Command | ContextMenu,
    ) -> None:
        if await self.bot.is_owner(interaction.user):
            return

        destination = None
        if interaction.guild is None:
            destination = 'Private Message'
        else:
            destination = f'#{interaction.channel} ({interaction.guild})'

        log.info(f'{interaction.created_at}: {interaction.user} in {destination}: /{app_command.qualified_name})')

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
