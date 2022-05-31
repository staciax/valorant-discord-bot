
"""
WAIT FOR DISCORD.PY SUPPORTING SLASH LOCALIZATION
"""

from __future__ import annotations

import os
import contextlib
from typing import Optional, Dict, Union, List, Tuple, Any, Callable
from discord.app_commands import Command, ContextMenu, Group
from contextvars import ContextVar

_current_locale = ContextVar("_current_locale", default="en-US")

discord_locale = [
    'da', # Danish
    'de', # German
    'en-GB', # English (UK)
    'en-US', # English (US)
    'es-ES', # Spanish (Spain)
    'fr', # French
    'hr', # Croatian
    'it', # Italian
    'lt', # Lithuanian
    'hu', # Hungarian
    'nl', # Dutch
    'no', # Norwegian
    'pl', # Polish
    'pt-BR', # Portuguese (Brazil)
    'ro', # Romanian
    'fi', # Finnish
    'sv-SE', # Swedish (Sweden)
    'vi', # Vietnamese
    'tr', # Turkish
    'cs', # Czech
    'el', # Greek
    'bg', # Bulgarian
    'ru', # Russian
    'uk', # Ukrainian
    'hi', # Hindi
    'th', # Thai
    'zh-CN', # Chinese (China)
    'ja', # Japanese
    'zh-TW', # Chinese (Taiwan)
    'ko', # Korean
]

valorant_locale_overwrite = {
    'en-US': 'en-US', # american_english 
    'en-GB': 'en-US', # british_english
    'zh-CN': 'zh-CN', # chinese 
    'zh-TW': 'zh-TW', # taiwan_chinese
    'fr'   : 'fr-FR', # french
    'de'   : 'de-DE', # german
    'it'   : 'it-IT', # italian
    'ja'   : 'ja-JP', # japanese
    'ko'   : 'ko-KR', # korean
    'pl'   : 'pl-PL', # polish
    'pt-BR': 'pt-BR', # portuguese_brazil 
    'ru'   : 'ru-RU', # russian
    'es-ES': 'es-ES', # spanish
    'th'   : 'th-TH', # thai 
    'tr'   : 'tr-TR', # turkish
    'vi'   : 'vi-VN', # vietnamese
}

def set_interaction_locale(locale: Optional[str]) -> None:
    ...

def reload_interaction_locales() -> None:
    ...