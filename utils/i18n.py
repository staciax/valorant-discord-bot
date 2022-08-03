import discord
import logging
from discord import app_commands

from typing import Optional

_log = logging.getLogger('lattebot.i18n')

class Translator(app_commands.Translator):

    async def load(self) -> None:
        print('lattebot i18n loaded')

    async def unload(self) -> None:
        print('lattebot i18n unloaded')

    async def translate(
            self,
            string: app_commands.locale_str,
            locale: discord.Locale,
            context: app_commands.TranslationContext
    ) -> Optional[str]:
        # translate string here...
        ...

