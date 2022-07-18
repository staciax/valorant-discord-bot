from __future__ import annotations

import asyncio
import logging
import urllib3
import aiohttp
from typing import (
    Any,
    ClassVar,
    Optional,
    NoReturn,
    Mapping,
    TypeVar,
    Coroutine,
    Dict,
    Union,
    TYPE_CHECKING
)

from .enums import Region, QueueID

class Route:
    BASE_URL: ClassVar[str] = "https://pd.{shard}.a.pvp.net"
    BASE_GLZ_URL: ClassVar[str] = "https://glz-{region}-1.{shard}.a.pvp.net"
    BASE_SHARD_URL: ClassVar[str] = "https://shared.{shard}.a.pvp.net"

    def __init__(
            self,
            method: str,
            path: str,
            endpoint_type="pd",
            region: str = "ap"
    ):
        self.method = method
        self.path = path
        self.endpoint_type = endpoint_type

        self.region: Optional[Region] = getattr(Region, region.upper())
        self.shard = self.region.shard

        url = ""
        if endpoint_type == "pd":
            url = self.BASE_URL.format(shard=self.shard)
        elif endpoint_type == "glz":
            url = self.BASE_GLZ_URL.format(region=self.region, shard=self.region)
        elif endpoint_type == "shared":
            url = self.BASE_SHARD_URL.format(shard=self.shard)

        self.url: str = url + path

class HTTPClient:

    def __init__(self, *args, **kwargs: Any) -> None:
        pass