from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from .bot import LatteMaid


log = logging.getLogger(__name__)


class Tree(app_commands.CommandTree['LatteMaid']):
    async def interaction_check(self, interaction: discord.Interaction[LatteMaid], /) -> bool:
        user = interaction.user
        # guild = interaction.guild
        # locale = interaction.locale
        command = interaction.command

        if await self.client.is_owner(user):
            return True

        # if interaction.type is discord.InteractionType.application_command:
        if interaction.user and isinstance(command, app_commands.ContextMenu | app_commands.Command):
            ...

        return True

    async def sync(self, *, guild: discord.abc.Snowflake | None = None) -> list[app_commands.AppCommand]:
        synced = await super().sync(guild=guild)
        if synced:
            log.info('synced {} application commands {}'.format(len(synced), f'for guild {guild.id}' if guild else ''))
        return synced

    async def on_error(
        self,
        interaction: discord.Interaction[LatteMaid],
        error: app_commands.AppCommandError,
        /,
    ) -> None:
        await super().on_error(interaction, error)

    async def insert_model_to_commands(self) -> None:
        server_app_commands = await self.fetch_commands(with_localizations=True)
        for server in server_app_commands:
            command = self.get_command(server.name, type=server.type)
            if command is None:
                log.warning('not found command: %s (type: %s)', server.name, server.type.name)
                continue
            command.extras['model'] = server

    async def fake_translator(self, *, guild: discord.abc.Snowflake | None = None) -> None:
        if self.translator is None:
            return
        commands = self._get_all_commands(guild=guild)
        for command in commands:
            await command.get_translated_payload(self.translator)

    # wait for discord adding this feature
    # fetch_commands with localizations
    # https://github.com/Rapptz/discord.py/pull/9452

    async def fetch_commands(
        self,
        *,
        guild: discord.abc.Snowflake | None = None,
        with_localizations: bool = False,
    ) -> list[app_commands.AppCommand]:
        if self.client.application_id is None:
            raise app_commands.errors.MissingApplicationID

        application_id = self.client.application_id

        from discord.http import Route

        if guild is None:
            commands = await self._http.request(
                Route(
                    'GET',
                    '/applications/{application_id}/commands',
                    application_id=application_id,
                ),
                params={'with_localizations': int(with_localizations)},
            )
        else:
            commands = await self._http.request(
                Route(
                    'GET',
                    '/applications/{application_id}/guilds/{guild_id}/commands',
                    application_id=application_id,
                    guild_id=guild.id,
                ),
                params={'with_localizations': int(with_localizations)},
            )

        return [app_commands.AppCommand(data=data, state=self._state) for data in commands]
