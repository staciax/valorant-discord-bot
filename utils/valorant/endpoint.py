# inspired by https://github.com/colinhartigan/

from __future__ import annotations

# Standard
import json
from typing import Any

import requests

from ..errors import HandshakeError, ResponseError
from .local import LocalErrorResponse

# Local
from .resources import (
    base_endpoint,
    base_endpoint_glz,
    base_endpoint_shared,
    region_shard_override,
    shard_region_override,
)


class API_ENDPOINT:
    def __init__(self) -> None:
        from .auth import Auth

        self.auth = Auth()

        # self.headers = {}
        # self.puuid = ''
        # self.player = ''
        # self.region = ''
        # self.shard = ''
        # self.pd = ''
        # self.shared = ''
        # self.glz = ''

        # client platform
        self.client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'

        # language
        self.locale_code = 'en-US'

    def activate(self, auth: dict[str, Any]) -> None:
        """activate api"""

        try:
            headers = self.__build_headers(auth['headers'])
            self.headers = headers
            # self.cookie = auth['cookie']
            self.puuid = auth['puuid']
            self.region = auth['region']
            self.player = auth['player_name']
            self.locale_code = auth.get('locale_code', 'en-US')
            self.__format_region()
            self.__build_urls()
        except Exception as e:
            print(e)
            raise HandshakeError(self.locale_response().get('FAILED_ACTIVE')) from e

    def locale_response(self) -> dict[str, Any]:
        """This function is used to check if the local response is enabled."""
        self.response = LocalErrorResponse('API', self.locale_code)
        return self.response

    # async def refresh_token(self) -> None:
    # cookies = self.cookie
    # cookies, accessToken, emt = await self.auth.redeem_cookies(cookies)

    # self.__build_headers()

    def fetch(self, endpoint: str = '/', url: str = 'pd', errors: dict[str, Any] | None = None) -> dict[str, Any]:
        """fetch data from the api"""

        self.locale_response()

        endpoint_url = getattr(self, url)

        data = None

        r = requests.get(f'{endpoint_url}{endpoint}', headers=self.headers)

        try:  # noqa: SIM105
            data = json.loads(r.text)
        except Exception:
            pass

        if 'httpStatus' not in data:  # type: ignore
            return data  # type: ignore

        if r.status_code == 400:
            response = LocalErrorResponse('AUTH', self.locale_code)
            raise ResponseError(response.get('COOKIES_EXPIRED'))
            # await self.refresh_token()
            # return await self.fetch(endpoint=endpoint, url=url, errors=errors)
        return {}

    def put(
        self,
        endpoint: str = '/',
        url: str = 'pd',
        data: dict[str, Any] | list[Any] | None = None,
        errors: dict[str, Any] | None = None,
    ) -> Any:
        """put data to the api"""

        self.locale_response()

        endpoint_url = getattr(self, url)

        r = requests.put(f'{endpoint_url}{endpoint}', headers=self.headers, data=data)
        data = json.loads(r.text)

        if data is None:
            raise ResponseError(self.response.get('REQUEST_FAILED'))

        return data

    # contracts endpoints

    def fetch_contracts(self) -> dict[str, Any]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.fetch(endpoint=f'/contracts/v1/contracts/{self.puuid}', url='pd')

    # PVP endpoints

    def fetch_content(self) -> dict[str, Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.fetch(endpoint='/content-service/v3/content', url='shared')

    def fetch_account_xp(self) -> dict[str, Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.fetch(endpoint=f'/account-xp/v1/players/{self.puuid}', url='pd')

    def fetch_player_mmr(self, puuid: str | None = None) -> dict[str, Any]:
        puuid = self.__check_puuid(puuid)
        return self.fetch(endpoint=f'/mmr/v1/players/{puuid}', url='pd')

    def fetch_name_by_puuid(self, puuid: str | None = None) -> dict[str, Any]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """
        if puuid is None:
            puuids = [self.__check_puuid()]
        elif puuid is not None and type(puuid) is str:
            puuids = [puuid]
        return self.put(endpoint='/name-service/v2/players', url='pd', data=puuids)

    def fetch_player_loadout(self) -> dict[str, Any]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        return self.fetch(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd')

    def put_player_loadout(self, loadout: dict[str, Any]) -> dict[str, Any]:
        """
        playerLoadoutUpdate
        Use the values from `fetch_player_loadout` excluding properties like `subject` and `version.` Loadout changes take effect when starting a new game
        """
        return self.put(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd', data=loadout)

    # store endpoints

    def store_fetch_offers(self) -> dict[str, Any]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        return self.fetch('/store/v1/offers/', url='pd')

    def store_fetch_storefront(self) -> dict[str, Any]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        return self.fetch(f'/store/v2/storefront/{self.puuid}', url='pd')

    def store_fetch_wallet(self) -> dict[str, Any]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radiant points the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radiant points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        return self.fetch(f'/store/v1/wallet/{self.puuid}', url='pd')

    def store_fetch_order(self, order_id: str) -> dict[str, Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.fetch(f'/store/v1/order/{order_id}', url='pd')

    def store_fetch_entitlements(self, item_type: dict) -> dict[str, Any]:
        """
        Store_GetEntitlements
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in `fetch_content` to know what items are owned.
        Category names and IDs:

        `ITEMTYPEID:`
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': 'Agents'\n
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': 'Contracts',\n
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': 'Sprays',\n
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': 'Gun Buddies',\n
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': 'Player Cards',\n
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': 'Skins',\n
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': 'Skins chroma',\n
        'de7caa6b-adf7-4588-bbd1-143831e786c6': 'Player titles',\n
        """
        return self.fetch(endpoint=f'/store/v1/entitlements/{self.puuid}/{item_type}', url='pd')

    # useful endpoints

    def fetch_mission(self) -> dict[str, Any]:
        """
        Get player daily/weekly missions
        """
        data = self.fetch_contracts()
        return data['Missions']

    def get_player_level(self) -> dict[str, Any]:
        """
        Aliases `fetch_account_xp` but received a level
        """
        return self.fetch_account_xp()['Progress']['Level']

    def get_player_tier_rank(self, puuid: str | None = None) -> str:
        """
        get player current tier rank
        """
        data = self.fetch_player_mmr(puuid)
        season_id = data['LatestCompetitiveUpdate']['SeasonID']
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data['QueueSkills']['competitive']['SeasonalInfoBySeasonID']
        return current_season[season_id]['CompetitiveTier']

    # local utility functions

    def __get_live_season(self) -> str:
        """Get the UUID of the live competitive season"""
        content = self.fetch_content()
        season_id = [season['ID'] for season in content['Seasons'] if season['IsActive'] and season['Type'] == 'act']
        if not season_id:
            return self.fetch_player_mmr()['LatestCompetitiveUpdate']['SeasonID']
        return season_id[0]

    def __check_puuid(self, puuid: str | None = None) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid

    def __build_urls(self) -> None:
        """
        generate URLs based on region/shard
        """
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    def __build_headers(self, headers: dict[str, Any]) -> dict[str, Any]:
        """build headers"""
        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = self._get_client_version()
        return headers

    def __format_region(self) -> None:
        """Format region to match from user input"""

        self.shard = self.region
        if self.region in region_shard_override:
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override:
            self.region = shard_region_override[self.shard]

    def _get_client_version(self) -> str:
        """Get the client version"""
        r = requests.get('https://valorant-api.com/v1/version')
        data = r.json()['data']
        return f'{data["branch"]}-shipping-{data["buildVersion"]}-{data["version"].split(".")[3]}'  # return formatted version string

    def _get_valorant_version(self) -> str | None:
        """Get the valorant version"""
        r = requests.get('https://valorant-api.com/v1/version')
        if r.status_code != 200:
            return None
        data = r.json()['data']
        return data['version']
