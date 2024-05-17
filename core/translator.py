from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from discord import Locale
from discord.app_commands.commands import Command, ContextMenu, Group, Parameter
from discord.app_commands.models import Choice
from discord.app_commands.translator import (
    TranslationContextLocation as TCL,
    Translator as _Translator,
    locale_str,
)
from discord.ext import commands
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from discord.app_commands import TranslationContext

    from .bot import Bot

    Localizable = Command | Group | ContextMenu | Parameter | Choice

T = TypeVar('T')
CogT = TypeVar('CogT', bound=commands.Cog)

_log = logging.getLogger(__name__)

# i know this is bad, but it works for now
# in the future, i'll make this better


class OptionLocalization(BaseModel):
    display_name: str
    description: str
    choices: dict[str | int | float, str] | None = Field(default=None)


class ContextMenuLocalization(BaseModel):
    name: str


class AppCommandLocalization(ContextMenuLocalization):
    description: str
    options: dict[str, OptionLocalization] | None = Field(default=None)


def get_path(
    cog_folder: Path,
    locale: str,
    *,
    fmt: str = 'json',
) -> Path:
    return cog_folder / 'locales' / 'app_commands' / f'{locale}.{fmt}'


def get_parameter_payload(
    parameter: Parameter,
    data: OptionLocalization | None = None,
    *,
    merge: bool = True,
) -> OptionLocalization:
    payload = OptionLocalization(
        display_name=parameter.display_name,
        description=parameter.description,
    )

    if parameter.choices:
        payload.choices = {str(choice.value): choice.name for choice in parameter.choices}

    if data and merge:
        if data.display_name and (data.display_name != payload.display_name):
            payload.display_name = data.display_name

        if (data.description and data.description != '…') and (data.description != payload.description):
            payload.description = data.description

        if parameter.choices:
            payload.choices = {}
            for choice in parameter.choices:
                if data.choices and str(choice.value) in data.choices:
                    payload.choices[str(choice.value)] = data.choices[str(choice.value)]
                else:
                    payload.choices[str(choice.value)] = choice.name

    return payload


def get_app_command_payload(
    command: Command | Group,
    data: AppCommandLocalization | None = None,
    *,
    merge: bool = True,
) -> AppCommandLocalization:
    payload = AppCommandLocalization(
        name=command.name,
        description=command.description,
    )

    if data and merge:
        if data.name != command.name:
            payload.name = data.name

        if data.description != command.description and data.description != '…':
            payload.description = data.description

    if isinstance(command, Group):
        return payload

    if command.parameters:
        payload.options = {param.name: get_parameter_payload(param) for param in command.parameters}

        if data and merge:
            payload.options = {
                param.name: get_parameter_payload(
                    param,
                    (data.options[param.name] if data.options and param.name in data.options else None),
                    merge=True,
                )
                for param in command.parameters
            }

    return payload


class Translator(_Translator):
    def __init__(
        self,
        bot: Bot,
        supported_locales: list[Locale] | None = None,
    ) -> None:
        super().__init__()
        self.bot: Bot = bot
        self.supported_locales: list[Locale] = supported_locales or [
            Locale.american_english,  # default
            Locale.thai,
        ]
        self._app_command_localizations: dict[str, dict[str, AppCommandLocalization]] = {}
        self._context_menu_localizations: dict[str, dict[str, ContextMenuLocalization]] = {}
        self._other_localizations: dict[str, dict[str, Any]] = {}
        self.lock: asyncio.Lock = asyncio.Lock()

    async def load(self) -> None:
        _log.info('loaded')

    async def unload(self) -> None:
        _log.info('unloaded')

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> str | None:
        localizable: Localizable = context.data
        tcl: TCL = context.location

        if locale == Locale.american_english:
            return None

        if locale not in self.supported_locales:
            return None

        if locale.value not in self._app_command_localizations:
            return None

        if tcl != TCL.other:
            translations = self._app_command_localizations.get(locale.value, {})
        elif isinstance(localizable, ContextMenu):
            translations = self._context_menu_localizations.get(locale.value, {})
        else:
            translations = {}

        keys = self._build_localize_keys(tcl, localizable)

        def find_value_by_keys(data: Any, keys: list[str]) -> str | None:
            _string = data.copy()
            for k in keys:
                try:
                    _string = _string[k]
                except KeyError:
                    return None

            if not isinstance(_string, str):
                _log.debug(f'not a string: {string.message} for {locale.value} (tcl: {tcl})')
                return None

            return _string

        locale_string = find_value_by_keys(translations, keys)

        if locale_string is None:
            _log.debug(
                f'not found:{string.message!r} locale:{locale.value} tcl:{tcl.name} type:{type(localizable).__qualname__}'
            )

        _log.info(f'{string.message!r} locale:{locale.value} tcl:{context.location.name} -> {locale_string!r}')
        return locale_string

    def _build_localize_keys(
        self,
        tcl: TCL,
        localizable: Localizable,
    ) -> list[str]:
        keys = []

        if tcl in [TCL.command_name, TCL.group_name] and isinstance(localizable, Command | Group | ContextMenu):
            keys.extend([localizable.qualified_name, 'name'])
            self.__latest_command = localizable

        elif tcl in [TCL.command_description, TCL.group_description] and isinstance(localizable, Command | Group):
            keys.extend([localizable.qualified_name, 'description'])

        elif tcl == TCL.parameter_name and isinstance(localizable, Parameter):
            keys.extend([
                localizable.command.qualified_name,
                'options',
                localizable.name,
                'display_name',
            ])
            self.__latest_parameter = localizable

        elif tcl == TCL.parameter_description and isinstance(localizable, Parameter):
            keys.extend([
                localizable.command.qualified_name,
                'options',
                localizable.name,
                'description',
            ])

        elif tcl == TCL.choice_name:
            if (
                self.__latest_command is not None
                and self.__latest_parameter is not None
                and isinstance(localizable, Choice)
            ):
                keys.extend([
                    self.__latest_command.qualified_name,
                    'options',
                    self.__latest_parameter.name,
                    'choices',
                    str(localizable.value),
                ])

        return keys

    # app commands

    async def load_from_files(self, cog_name: str, cog_folder: str | Path) -> None:
        for locale in self.supported_locales:
            locale_path = get_path(Path(cog_folder).resolve().parent, locale.value)

            if not locale_path.exists():
                continue

            if locale.value not in self._app_command_localizations:
                self._app_command_localizations[locale.value] = {}

            async with self.lock:
                with locale_path.open('r', encoding='utf-8') as file:
                    self._app_command_localizations[locale.value].update(json.load(file))

        _log.debug(f'loaded app command localizations for {cog_name}')

    async def save_to_files(
        self,
        app_commands: list[str],
        cog_name: str,
        cog_folder: str | Path,
    ) -> None:
        # for locale, localization in self._app_command_localizations.items():

        for locale in self.supported_locales:
            locale_path = get_path(Path(cog_folder).resolve().parent, locale.value)

            if not locale_path.parent.exists():
                locale_path.parent.mkdir(parents=True)
                _log.debug(f'created {locale_path.parent}')

            localizations = self._app_command_localizations.get(locale.value, {})
            entries = {
                command: localization for command, localization in localizations.items() if command in app_commands
            }
            entries = dict(sorted(entries.items()))

            with locale_path.open('w', encoding='utf-8') as file:
                json.dump(entries, file, indent=4, ensure_ascii=False)
                _log.debug(f'saved app command localizations for {cog_name} in {locale}')

    def get_app_command_localization(
        self,
        locale: str,
        command: Command | Group,
    ) -> AppCommandLocalization | None:
        if locale not in self._app_command_localizations:
            return None
        if command.qualified_name not in self._app_command_localizations[locale]:
            return None
        return self._app_command_localizations[locale][command.qualified_name]

    def add_app_command_localization(self, command: Command | Group) -> None:
        for locale in self.supported_locales:
            if locale.value not in self._app_command_localizations:
                self._app_command_localizations[locale.value] = {}

            self._app_command_localizations[locale.value][command.qualified_name] = get_app_command_payload(
                command,
                self.get_app_command_localization(locale.value, command),
                merge=True,
            )

    def remove_app_command_localization(self, command: Command | Group) -> None:
        for locale in self.supported_locales:
            self._app_command_localizations.setdefault(locale.value, {}).pop(command.qualified_name, None)

    # context menus

    # TODO: add context menu localization
