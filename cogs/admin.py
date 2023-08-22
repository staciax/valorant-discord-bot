from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from core.checks import bot_has_permissions, owner_only

if TYPE_CHECKING:
    from core.bot import Bot


class Admin(commands.Cog, name='admin'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(name='sync', description='Syncs the application commands to Discord.')
    @app_commands.describe(guild_id='target guild id')
    @bot_has_permissions(send_messages=True)
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @owner_only()
    async def sync_tree(self, interaction: discord.Interaction[Bot], guild_id: str | None = None) -> None:
        await interaction.response.defer(ephemeral=True)

        if guild_id is not None and guild_id.isdigit():
            obj = discord.Object(id=int(guild_id))
            await self.bot.tree.sync(guild=obj)
            return
        synced = await self.bot.tree.sync()

        content = f'sync tree: {len(synced)}'
        if guild_id is not None:
            content += f' : `{guild_id}`'

        await interaction.followup.send(content, ephemeral=True, silent=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Admin(bot), guild=discord.Object(id=bot.support_guild_id))
