from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.ui.embed import Embed

if TYPE_CHECKING:
    from core.bot import Bot

log = logging.getLogger(__name__)


class Event(commands.Cog, name='events'):
    """Bot Events."""

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @discord.utils.cached_property
    def webhook(self) -> discord.Webhook:
        load_dotenv()
        wh_id = os.getenv('WEBHOOK_GUILD_ID')
        assert wh_id is not None, 'WEBHOOK_GUILD_ID is not set'
        wh_token = os.getenv('WEBHOOK_GUILD_TOKEN')
        assert wh_token is not None, 'WEBHOOK_GUILD_TOKEN is not set'
        hook = discord.Webhook.partial(int(wh_id), wh_token, session=self.bot.session)
        return hook

    async def send_guild_stats(self, embed: discord.Embed, guild: discord.Guild) -> None:
        """Send guild stats to webhook."""
        member_count = guild.member_count or 1

        embed.description = (
            f'**ɴᴀᴍᴇ:** {discord.utils.escape_markdown(guild.name)} • `{guild.id}`\n' f'**ᴏᴡɴᴇʀ:** `{guild.owner_id}`'
        )
        embed.add_field(name='ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ', value=f'{member_count}', inline=True)
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=f'ᴛᴏᴛᴀʟ ɢᴜɪʟᴅꜱ: {len(self.bot.guilds)}')

        if guild.me:
            embed.timestamp = guild.me.joined_at

        await self.webhook.send(embed=embed, silent=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Call when bot joins a guild."""

        embed = Embed(title='ᴊᴏɪɴᴇᴅ ꜱᴇʀᴠᴇʀ').success()
        await self.send_guild_stats(embed, guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Call when bot leaves a guild."""
        embed = Embed(title='ʟᴇꜰᴛ ꜱᴇʀᴠᴇʀ').error()
        await self.send_guild_stats(embed, guild)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Event(bot))
