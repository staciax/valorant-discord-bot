from __future__ import annotations

from abc import ABC
from discord.utils import MISSING

from utils import cache

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bot import ValorantBot
    from valorant import Client as ValorantClient

class MixinMeta(ABC):
    """ Metaclass for mixin classes. """

    def __init__(self, *_args):
        self.bot: ValorantBot = MISSING
        self.valorant_client: Optional[ValorantClient] = MISSING

    @cache.cache()
    async def get_riot_account(self, *, user_id: int) -> Any:
        ...