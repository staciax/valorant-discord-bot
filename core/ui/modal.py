from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands, ui
from discord.utils import MISSING

if TYPE_CHECKING:
    from core.bot import Bot


class Modal(ui.Modal):
    def __init__(
        self,
        interaction: discord.Interaction[Bot],
        *,
        title: str = MISSING,
        timeout: float | None = None,
        custom_id: str = MISSING,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.original_interaction: discord.Interaction[Bot] = interaction
        self.locale: discord.Locale = interaction.locale

    async def on_error(self, interaction: discord.Interaction[Bot], error: Exception) -> None:
        command = interaction.command or self.original_interaction.command

        if command is not None and command._has_any_error_handlers():
            if isinstance(command, app_commands.Command):
                await command._invoke_error_handlers(interaction, error)  # type: ignore
            elif isinstance(command, app_commands.ContextMenu):
                if hasattr(command, '__binding__') is not None:
                    # make sure we have a context menu binding
                    await command.on_error(interaction, error)  # type: ignore
            return

        # if we don't have any error handlers, just dispatch the event
        interaction.client.dispatch('modal_error', interaction, error, self)

        # Make sure we know what the error actually is
        # traceback.print_tb(error.__traceback__)
