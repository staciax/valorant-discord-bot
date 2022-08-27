# inspired by https://github.com/colinhartigan/

from __future__ import annotations

# Standard
import json
from typing import Any, Dict, Mapping

import requests
import urllib3

from ..errors import HandshakeError, ResponseError
from .local import LocalErrorResponse

# Local
from .resources import base_endpoint, base_endpoint_glz, base_endpoint_shared, region_shard_override, shard_region_override

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    def activate(self, auth: Mapping[str, Any]) -> None:
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
            raise HandshakeError(self.locale_response().get('FAILED_ACTIVE'))

    def locale_response(self) -> LocalErrorResponse:
        """This function is used to check if the local response is enabled."""
        self.response = LocalErrorResponse('API', self.locale_code)
        return self.response

    # async def refresh_token(self) -> None:
    # cookies = self.cookie
    # cookies, accessToken, emt = await self.auth.redeem_cookies(cookies)

    # self.__build_headers()

    def fetch(self, endpoint: str = '/', url: str = 'pd', errors: Dict = {}) -> Dict:
        """fetch data from the api"""

        self.locale_response()

        endpoint_url = getattr(self, url)

        data = None

        r = requests.get(f'{endpoint_url}{endpoint}', headers=self.headers)

        try:
            data = json.loads(r.text)
        except:  # as no data is set, an exception will be raised later in the method
            pass

        if "httpStatus" not in data:
            return data

        if data["httpStatus"] == 400:
            response = LocalErrorResponse('AUTH', self.locale_code)
            raise ResponseError(response.get('COOKIES_EXPIRED'))
            # await self.refresh_token()
            # return await self.fetch(endpoint=endpoint, url=url, errors=errors)

    def put(self, endpoint: str = "/", url: str = 'pd', data: Dict = {}, errors: Dict = {}) -> Dict:
        """put data to the api"""

        self.locale_response()

        data = data if type(data) is list else json.dumps(data)

        endpoint_url = getattr(self, url)
        data = None

        r = requests.put(f'{endpoint_url}{endpoint}', headers=self.headers, data=data)
        data = json.loads(r.text)

        if data is not None:
            return data
        else:
            raise ResponseError(self.response.get('REQUEST_FAILED'))

    # contracts endpoints

    def fetch_contracts(self) -> Mapping[str, Any]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        data = self.fetch(endpoint=f'/contracts/v1/contracts/{self.puuid}', url='pd')
        return data

    # PVP endpoints

    def fetch_content(self) -> Mapping[str, Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        data = self.fetch(endpoint='/content-service/v3/content', url='shared')
        return data

    def fetch_account_xp(self) -> Mapping[str, Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        data = self.fetch(endpoint=f'/account-xp/v1/players/{self.puuid}', url='pd')
        return data

    def fetch_player_mmr(self, puuid: str = None) -> Mapping[str, Any]:
        puuid = self.__check_puuid(puuid)
        data = self.fetch(endpoint=f'/mmr/v1/players/{puuid}', url='pd')
        return data

    def fetch_name_by_puuid(self, puuid: str = None) -> Mapping[str, Any]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """
        if puuid is None:
            puuid = [self.__check_puuid()]
        elif puuid is not None and type(puuid) is str:
            puuid = [puuid]
        data = self.put(endpoint='/name-service/v2/players', url='pd', body=puuid)
        return data

    def fetch_player_loadout(self) -> Mapping[str, Any]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        data = self.fetch(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd')
        return data

    def put_player_loadout(self, loadout: Mapping) -> Mapping[str, Any]:
        """
        playerLoadoutUpdate
        Use the values from `fetch_player_loadout` excluding properties like `subject` and `version.` Loadout changes take effect when starting a new game
        """
        data = self.put(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd', body=loadout)
        return data

    # store endpoints

    def store_fetch_offers(self) -> Mapping[str, Any]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        data = self.fetch('/store/v1/offers/', url='pd')
        return data

    def store_fetch_storefront(self) -> Mapping[str, Any]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        data = self.fetch(f'/store/v2/storefront/{self.puuid}', url='pd')
        return data

    def store_fetch_wallet(self) -> Mapping[str, Any]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radiant points the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radiant points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        data = self.fetch(f'/store/v1/wallet/{self.puuid}', url='pd')
        return data

    def store_fetch_order(self, order_id: str) -> Mapping[str, Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        data = self.fetch(f'/store/v1/order/{order_id}', url='pd')
        return data

    def store_fetch_entitlements(self, item_type: Mapping) -> Mapping[str, Any]:
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
        data = self.fetch(endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}", url="pd")
        return data

    # useful endpoints

    def fetch_mission(self) -> Mapping[str, Any]:
        """
        Get player daily/weekly missions
        """
        data = self.fetch_contracts()
        mission = data["Missions"]
        return mission

    def get_player_level(self) -> Mapping[str, Any]:
        """
        Aliases `fetch_account_xp` but received a level
        """
        data = self.fetch_account_xp()['Progress']['Level']
        return data

    def get_player_tier_rank(self, puuid: str = None) -> str:
        """
        get player current tier rank
        """
        data = self.fetch_player_mmr(puuid)
        season_id = data['LatestCompetitiveUpdate']['SeasonID']
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data["QueueSkills"]['competitive']['SeasonalInfoBySeasonID']
        current_Tier = current_season[season_id]['CompetitiveTier']
        return current_Tier

    # local utility functions

    def __get_live_season(self) -> str:
        """Get the UUID of the live competitive season"""
        content = self.fetch_content()
        season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        if not season_id:
            return self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
        return season_id[0]

    def __check_puuid(self, puuid: str) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid

    def __build_urls(self) -> str:
        """
        generate URLs based on region/shard
        """
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    def __build_headers(self, headers: Mapping) -> Mapping[str, Any]:
        """build headers"""

        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = self._get_client_version()
        return headers

    def __format_region(self) -> None:
        """Format region to match from user input"""

        self.shard = self.region
        if self.region in region_shard_override.keys():
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override.keys():
            self.region = shard_region_override[self.shard]

    def _get_client_version(self) -> str:
        """Get the client version"""
        r = requests.get('https://valorant-api.com/v1/version')
        data = r.json()['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"  # return formatted version string

    def _get_valorant_version(self) -> str:
        """Get the valorant version"""
        r = requests.get('https://valorant-api.com/v1/version')
        if r.status != 200:
            return None
        data = r.json()['data']
        return data['version']
