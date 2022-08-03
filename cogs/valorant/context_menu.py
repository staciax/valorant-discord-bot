from __future__ import annotations

from discord import Interaction, Member
from discord.app_commands.checks import dynamic_cooldown
from utils.checks import cooldown_5s

# from ._embeds import Embed
from ._abc import MixinMeta
# from ._enums import (
#     ContentTier as ContentTierEmoji,
#     Point as PointEmoji,
# )

from utils.errors import CommandError
# from utils.formats import format_relative

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from valorant.models import StoreFront, Wallet

class ContextMenu(MixinMeta):
    ...