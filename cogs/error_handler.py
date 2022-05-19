import discord
import traceback
from discord import Interaction
from discord.ext import commands
from discord.app_commands import (
    AppCommandError,
    CommandInvokeError,
    CommandNotFound,
    MissingPermissions,
    BotMissingPermissions
)
from typing import Union

class ErrorHandler(commands.Cog):
    """Error handler"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
    
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        """ Handles errors for all application commands."""

        if isinstance(error, CommandInvokeError):
            error = error.original
            traceback.print_exception(type(error), error, error.__traceback__)
        elif isinstance(error, Union[CommandNotFound, MissingPermissions, BotMissingPermissions]):
            error = error
        else:
            error = f"An unknown error occurred, sorry"
            traceback.print_exception(type(error), error, error.__traceback__)
        
        embed = discord.Embed(description=f'{str(error)[:2000]}', color=0xfe676e)
        if interaction.response.is_done():
            return await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))