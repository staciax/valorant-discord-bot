from enum import Enum

__all__ = (
    'Region',
    'Shard'
)


class Region(Enum):
    NA = 'na'
    EU = 'eu'
    LATAM = 'latam'
    BR = 'br'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'

    def __str__(self) -> str:
        return self._region_shard_override

    @property
    def shard(self) -> str:
        return getattr(Shard, self.value.upper())

    @property
    def _region_shard_override(self) -> str:
        if self.shard == self.PBE.value:
            return self.NA.value
        return self.value

class Shard(Enum):
    NA = 'na'
    EU = 'eu'
    LATAM = 'na'
    BR = 'na'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'

    def __str__(self) -> str:
        return self.value

class ItemType(Enum):
    Agent = '01bb38e1-da47-4e6a-9b3d-945fe4655707'
    Buddy = 'dd3bf334-87f3-40bd-b043-682a57a8dc3a'
    Contract = 'f85cb6f7-33e5-4dc8-b609-ec7212301948'
    Skin = 'e7c63390-eda7-46e0-bb7a-a6abdacd2433'
    SkinChroma = '3ad1b2b2-acdb-4524-852f-954a76ddae0a'
    Spray = 'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475'
    PlayerCard = '3f296c07-64c3-494c-923b-fe692a4fa1bd'
    PlayerTitle = 'de7caa6b-adf7-4588-bbd1-143831e786c6'

    def __str__(self) -> str:
        return self.value