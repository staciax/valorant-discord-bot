from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable  # noqa: UP035

from discord import Colour, Embed as DiscordEmbed

if TYPE_CHECKING:
    from datetime import datetime

    from discord.types.embed import EmbedType
    from typing_extensions import Self

# fmt: off
__all__ = (
    'Embed',
)
# fmt: on


class Embed(DiscordEmbed):
    def __init__(
        self,
        *,
        colour: int | Colour | None = 0xFFFFFF,
        color: int | Colour | None = 0xFFFFFF,
        title: Any | None = None,
        type: EmbedType = 'rich',
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None,
        fields: Iterable[tuple[str, str]] = (),
        field_inline: bool = False,
        custom_id: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            color=color,
            colour=colour,
            title=title,
            type=type,
            description=description,
            url=url,
            timestamp=timestamp,
        )
        self.custom_id: str | None = custom_id
        self.extra: dict[str, Any] = kwargs
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    def add_empty_field(self, *, inline: bool = False) -> Self:
        self.add_field(name='\u200b', value='\u200b', inline=inline)
        return self

    def empty_title(self) -> Self:
        self.title = '\u200b'
        return self

    def move_image_to_thumbnail(self) -> Self:
        if self.image and not self.thumbnail:
            self.set_thumbnail(url=self.image.url)
            self.set_image(url=None)
        return self

    def move_thumbnail_to_image(self) -> Self:
        if self.thumbnail and not self.image:
            self.set_image(url=self.thumbnail.url)
            self.set_thumbnail(url=None)
        return self

    def secondary(self) -> Self:
        self.colour = 0x111111
        return self

    def tertiary(self) -> Self:
        self.colour = 0x222222
        return self

    def purple(self) -> Self:
        self.colour = 0xC0AEE0
        return self

    def dark_purple(self) -> Self:
        self.colour = 0x8B7DB5
        return self

    def dark(self) -> Self:
        self.colour = 0x0F1923
        return self

    def success(self) -> Self:
        self.colour = 0x8BE28B
        return self

    def error(self) -> Self:
        self.colour = 0xFF6961
        return self

    def warning(self) -> Self:
        self.colour = 0xFDFD96
        return self

    def info(self) -> Self:
        self.colour = 0x60DCC4
        return self

    def danger(self) -> Self:
        self.colour = 0xFC5C5C
        return self

    def light(self) -> Self:
        self.colour = 0xCBCCD6
        return self

    def white(self) -> Self:
        self.colour = Colour.light_embed()
        return self

    def dark_theme(self) -> Self:
        self.colour = Colour.dark_theme()
        return self

    def blurple(self) -> Self:
        self.colour = Colour.blurple()
        return self
