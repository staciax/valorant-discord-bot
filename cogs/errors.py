from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

import discord
from discord import Interaction
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    CommandNotFound as AppCommandNotFound,
    CommandOnCooldown,
    MissingPermissions,
)
from discord.ext import commands
from discord.ext.commands import BadLiteralArgument, CheckFailure, CommandNotFound, MissingRequiredArgument

from utils.errors import (
    AuthenticationError,
    BadArgument,
    DatabaseError,
    HandshakeError,
    NotOwner,
    ResponseError,
    ValorantBotError,
)

if TYPE_CHECKING:
    from bot import ValorantBot

app_cmd_scope = 'https://cdn.discordapp.com/attachments/934041100048535563/979410875226128404/applications.commands.png'


class ErrorHandler(commands.Cog):
    """Error handler"""

    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        """Handles errors for all application commands."""

        if self.bot.debug is True:
            traceback.print_exception(type(error), error, error.__traceback__)

        error_message = 'An unknown error occurred, sorry'
        # if isinstance(error, CommandInvokeError):
        #     error = error.original
        if isinstance(error, NotOwner):
            error_message = 'You are not the owner of this bot.'
        elif isinstance(error, BadArgument):
            error_message = 'Bad argument.'
        elif isinstance(
            error, (ValorantBotError | ResponseError | HandshakeError | DatabaseError | AuthenticationError)
        ):
            error_message = error
        elif isinstance(error, ResponseError):
            error_message = 'Empty response from Riot server.'
        elif isinstance(error, HandshakeError):
            error_message = 'Could not connect to Riot server.'
        elif isinstance(error, (CommandOnCooldown | AppCommandNotFound | MissingPermissions | BotMissingPermissions)):
            error = error
        # else:
        #     traceback.print_exception(type(error), error)

        embed = discord.Embed(description=f'{str(error_message)[:2000]}', color=0xFE676E)
        if interaction.response.is_done():
            return await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context[ValorantBot], error: Exception) -> None:
        embed = discord.Embed(color=0xFE676E)

        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, CheckFailure):
            cm_error = 'Only owners can run this command!'
        elif isinstance(error, MissingRequiredArgument):
            cm_error = "You didn't pass a required argument!"
            if ctx.command and ctx.command.name in ['sync', 'unsync']:
                cm_error = 'You need to specify a sync type: `guild` or `global`'
        elif hasattr(error, 'original'):
            if isinstance(error.original, discord.Forbidden):  # type: ignore
                cm_error = "Bot don't have permission to run this command."
                if ctx.command and ctx.command.name in ['sync', 'unsync']:
                    cm_error = "Bot don't have permission `applications.commands` to sync."
                    embed.set_image(url=app_cmd_scope)
            elif isinstance(error.original, discord.HTTPException):  # type: ignore
                cm_error = 'An error occurred while processing your request.'
        elif isinstance(error, BadLiteralArgument):
            cm_error = f"**Invalid literal:** {', '.join(error.literals)}"
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            cm_error = 'An unknown error occurred, sorry'

        embed.description = cm_error
        await ctx.send(embed=embed, delete_after=30, ephemeral=True)


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(ErrorHandler(bot))
