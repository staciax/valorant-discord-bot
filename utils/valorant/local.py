import json
import contextlib
from typing import Dict

Locale = {
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

def InteractionLanguage(local_code: str) -> str:
    return Locale.get(str(local_code), 'en-US')

def __LocalRead(filename: str) -> Dict:
    data = {}
    try:
        with open(f"languages/{filename}.json", "r", encoding='utf-8') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        return __LocalRead('en-US')
    return data

def ResponseLanguage(command_name: str, local_code: str) -> Dict:
    local_code = __verify_localcode(local_code)
    local = {}
    with contextlib.suppress(KeyError):
        local_dict = __LocalRead(local_code)
        local = local_dict['commands'][str(command_name)]
    return local

def LocalErrorResponse(value: str, local_code: str) -> Dict:
    local_code = __verify_localcode(local_code)
    local = {}
    with contextlib.suppress(KeyError):
        local_dict = __LocalRead(local_code)
        local = local_dict['errors'][value]
    return local
    
def __verify_localcode(local_code: str) -> str:
    if local_code in ['en-US', 'en-GB']:
        return 'en-US'
    return local_code
