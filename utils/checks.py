from typing import  Optional

import discord
from discord import Interaction, app_commands


def owner_only() -> app_commands.check:
    async def predicate(interaction: Interaction) -> bool:
        return await interaction.client.is_owner(interaction.user)  # type: ignore

    return app_commands.check(predicate)


def cooldown_5s(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if interaction.user.id == interaction.client.owner_id:  # type: ignore
        return None
    return app_commands.Cooldown(1, 5)
