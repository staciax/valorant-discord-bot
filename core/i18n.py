from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar, overload  # noqa: UP035

from discord import Locale

__all__ = (
    'I18n',
    'cog_i18n',
)

if TYPE_CHECKING:
    from discord.ext import commands

    T = TypeVar('T')
    CogT = TypeVar('CogT', bound=commands.Cog)


_log = logging.getLogger(__name__)


def get_path(
    cog_folder: Path,
    locale: str,
    fmt: str = 'json',
) -> Path:
    return cog_folder / 'locales' / 'strings' / f'{locale}.{fmt}'


# i18ns: dict[str, I18n] = {}
# TODO: add i18n to bot


class I18n:
    def __init__(
        self,
        name: str,
        file_location: str | Path,
        *,
        supported_locales: list[Locale] | None = None,
        read_only: bool = False,
        load_later: bool = False,
        # global_i18n: bool = False,
    ) -> None:
        self.cog_folder: Path = Path(file_location).resolve().parent
        self.cog_name: str = name
        self.supported_locales: list[Locale] = supported_locales or [Locale.american_english]
        self.read_only: bool = read_only
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self._data: dict[str, dict[str, dict[str, str]]] = {}
        if load_later:
            self.loop.create_task(self.load())
        else:
            self._load()
        # i18ns[self.cog_name] = self

    def __call__(self, key: str, locale: Locale | str | None = None) -> str:
        if locale is None:
            locale = Locale.american_english

        if isinstance(locale, Locale):
            locale = locale.value

        # default to american english
        if locale not in self._data:
            locale = Locale.american_english

        text = self.get_text(key, locale)
        if text is None:
            _log.warning(f'found key:{key!r} locale:{locale}')
            return key

        return text

    def __contains__(self, locale: Locale | str) -> bool:
        if isinstance(locale, Locale):
            locale = locale.value
        return locale in self._data

    async def load(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self._load)

    def _load(self) -> None:
        for locale in self.supported_locales:
            self.load_from_file(locale.value)
        if not self.read_only:
            self.loop.create_task(self.save())
        _log.info(f'loaded cogs.{self.cog_name}')

    def load_from_file(self, locale: str) -> None:
        locale_path = get_path(self.cog_folder, locale)
        if not locale_path.exists():
            self._data[locale] = {}

        with contextlib.suppress(IOError, FileNotFoundError):
            with locale_path.open(encoding='utf-8') as file:
                self._data[locale] = json.load(file)

    async def save(self) -> None:
        for locale in self._data:
            async with self.lock:
                await self.loop.run_in_executor(None, self._dump, locale)
        _log.debug(f'saved i18n: {self.cog_name}')

    def _dump(self, locale: str) -> None:
        if locale not in self._data:
            self._data[locale] = {}

        locale_path = get_path(self.cog_folder, locale)
        with contextlib.suppress(IOError, FileExistsError):
            if not locale_path.parent.exists():
                locale_path.parent.mkdir(parents=True)
                _log.debug(f'created {locale_path.parent}')

        data = self._data[locale]

        with locale_path.open('w', encoding='utf-8') as file:
            json.dump(data.copy(), file, indent=4, ensure_ascii=False)
            _log.debug(f'saved i18n: {self.cog_name} in {locale}')

    def get_locale(self, locale: str, default: Any = None) -> dict[str, str] | Any | None:
        """Retrieve a locale entry."""
        return self._data.get(locale, default)

    async def remove_locale(self, locale: str) -> None:
        """Remove a locale."""
        self._data.pop(locale, None)
        await self.save()

    async def add_locale(self, locale: str) -> None:
        """Add a locale."""
        if locale in self._data:
            return
        self._data[locale] = {}
        await self.save()

    @overload
    def get_text(self, key: str, locale: Locale | str) -> str | None: ...

    @overload
    def get_text(self, key: str, locale: Locale | str, default: T) -> str | T | None: ...

    def get_text(self, key: str, locale: Locale | str, default: T | None = None) -> str | T | None:
        if isinstance(locale, Locale):
            locale = locale.value

        locale_data = self.get_locale(locale)
        if locale_data is None:
            return None

        return locale_data.get(key, default)


# i18n = I18n()


def cog_i18n(i18n: I18n) -> Callable[[type[CogT]], type[CogT]]:
    def decorator(cog_class: type[CogT]) -> type[CogT]:
        setattr(cog_class, '__i18n__', i18n)  # noqa: B010
        return cog_class

    return decorator
