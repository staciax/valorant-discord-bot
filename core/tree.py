from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from .bot import Bot


log = logging.getLogger(__name__)


class Tree(app_commands.CommandTree['Bot']):
    async def interaction_check(self, interaction: discord.Interaction[Bot], /) -> bool:
        user = interaction.user
        guild = interaction.guild
        locale = interaction.locale
        command = interaction.command

        if await self.client.is_owner(user):
            return True

        return True

    async def sync(self, *, guild: discord.abc.Snowflake | None = None) -> list[app_commands.AppCommand]:
        synced = await super().sync(guild=guild)
        if synced:
            log.info('synced %s application commands %s' % (len(synced), f'for guild {guild.id}' if guild else ''))
        return synced

    async def on_error(
        self,
        interaction: discord.Interaction['Bot'],
        error: app_commands.AppCommandError,
        /,
    ) -> None:
        await super().on_error(interaction, error)
