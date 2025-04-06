"""
I WILL REMOVE THIS FILE AFTER THE LOCALIZATION V2 IS DONE
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

# credit by /giorgi-o/

Locale = {
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


def InteractionLanguage(local_code: str) -> str:
    return Locale.get(str(local_code), 'en-US')


def local_read(filename: str) -> dict[str, Any]:
    path = Path(__file__).parent.parent / 'languages' / f'{filename}.json'
    if not path.exists():
        return local_read('en-US')

    data: dict[str, Any] = json.loads(path.read_text(encoding='utf-8'))
    return data


def ResponseLanguage(command_name: str, local_code: str) -> dict[str, Any]:
    local_code = __verify_localcode(local_code)
    local = {}
    with contextlib.suppress(KeyError):
        local_dict = local_read(local_code)
        local = local_dict['commands'][str(command_name)]
    return local


def LocalErrorResponse(value: str, local_code: str) -> dict[str, Any]:
    local_code = __verify_localcode(local_code)
    local = {}
    with contextlib.suppress(KeyError):
        local_dict = local_read(local_code)
        local = local_dict['errors'][value]
    return local


def __verify_localcode(local_code: str) -> str:
    if local_code in ('en-US', 'en-GB'):  # noqa: PLR6201
        return 'en-US'
    return local_code
