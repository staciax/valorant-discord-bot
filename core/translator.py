from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Locale
from discord.app_commands import Translator as _Translator

if TYPE_CHECKING:
    from .bot import Bot


class Translator(_Translator):
    def __init__(
        self,
        bot: Bot,
        supported_locales: tuple[Locale, ...] = (
            Locale.american_english,  # default
            Locale.thai,
        ),
    ) -> None:
        super().__init__()
        self.bot: Bot = bot
        self.supported_locales: tuple[Locale, ...] = supported_locales
