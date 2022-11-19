from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime
    import ssl

    import aiohttp
    import discord
    import valorantx
    from bot import ValorantBot


class MixinMeta(ABC):
    """Metaclass for mixin classes."""

    if TYPE_CHECKING:
        bot: ValorantBot

    def __init__(self, *_args):
        pass
