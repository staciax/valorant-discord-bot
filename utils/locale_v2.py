"""
DEMO TRANSLATION
"""
from __future__ import annotations

import os
from contextvars import ContextVar
from typing import Optional

discord_locale = [
    'da',  # Danish
    'de',  # German
    'en-GB',  # English (UK)
    'en-US',  # English (US)
    'es-ES',  # Spanish (Spain)
    'fr',  # French
    'hr',  # Croatian
    'it',  # Italian
    'lt',  # Lithuanian
    'hu',  # Hungarian
    'nl',  # Dutch
    'no',  # Norwegian
    'pl',  # Polish
    'pt-BR',  # Portuguese (Brazil)
    'ro',  # Romanian
    'fi',  # Finnish
    'sv-SE',  # Swedish (Sweden)
    'vi',  # Vietnamese
    'tr',  # Turkish
    'cs',  # Czech
    'el',  # Greek
    'bg',  # Bulgarian
    'ru',  # Russian
    'uk',  # Ukrainian
    'hi',  # Hindi
    'th',  # Thai
    'zh-CN',  # Chinese (China)
    'ja',  # Japanese
    'zh-TW',  # Chinese (Taiwan)
    'ko',  # Korean
]

valorant_locale_overwrite = {
    'en-US': 'en-US',  # american_english
    'en-GB': 'en-US',  # british_english
    'zh-CN': 'zh-CN',  # chinese
    'zh-TW': 'zh-TW',  # taiwan_chinese
    'fr': 'fr-FR',  # french
    'de': 'de-DE',  # german
    'it': 'it-IT',  # italian
    'ja': 'ja-JP',  # japanese
    'ko': 'ko-KR',  # korean
    'pl': 'pl-PL',  # polish
    'pt-BR': 'pt-BR',  # portuguese_brazil
    'ru': 'ru-RU',  # russian
    'es-ES': 'es-ES',  # spanish
    'th': 'th-TH',  # thai
    'tr': 'tr-TR',  # turkish
    'vi': 'vi-VN',  # vietnamese
}

_current_locale = ContextVar("_current_locale", default="en-US")
_valorant_current_locale = ContextVar("_valorant_current_locale", default="en-US")


def get_interaction_locale() -> str:
    """Get the bot locale"""
    return str(_current_locale.get())


def set_interaction_locale(locale: Optional[str]) -> None:
    """Set the locale for bot"""
    _current_locale.set(locale)


def get_valorant_locale() -> str:
    """Get the locale for valorant api"""
    valorant_locale = valorant_locale_overwrite.get(str(_valorant_current_locale.get()), "en-US")
    return valorant_locale


def set_valorant_locale(locale: Optional[str]) -> None:
    """Set the locale for valorant api"""

    language_files = os.listdir('languages')
    locale_json = str(locale) + '.json'
    if locale_json not in language_files:
        _valorant_current_locale.set("en-US")
    _valorant_current_locale.set(locale)


class ValorantTranslator:
    """Translate valorant item name"""

    def __str__(self) -> str:
        locale = get_valorant_locale()
        return locale

    def lower(self) -> str:
        locale = get_valorant_locale()
        return locale.lower()


class Translator:
    """Translate valorant item name"""

    def __str__(self) -> str:
        locale = get_interaction_locale()
        return locale

    def lower(self) -> str:
        locale = get_interaction_locale()
        return locale.lower()
