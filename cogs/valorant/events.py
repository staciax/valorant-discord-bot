import discord
from discord.ext import commands

from ._abc import MixinMeta

class Events(MixinMeta):

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Called when Bot leaves a guild"""

        # TODO : Remove all user data from the database