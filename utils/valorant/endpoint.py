# Standard # inspired by https://github.com/colinhartigan/
import aiohttp
import urllib3
import json
from typing import Dict

# Local
from .resources import (
    region_shard_override,
    shard_region_override,
    base_endpoint,
    base_endpoint_glz,
    base_endpoint_shared
)
from .auth import Auth
from .local import LocalErrorResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class API_ENDPOINT:

    def __init__(self, session: aiohttp.ClientSession) -> None:
        
        self.session = session
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

    async def activate(self, auth: Dict) -> None:
        '''activate api'''
    
        try:
            headers = await self.__build_headers(auth['headers'])
            self.headers = headers
            # self.cookie = auth['cookie']
            self.puuid = auth['puuid']
            self.region = auth['region']
            self.player = auth['player_name']
            self.locale_code = auth.get('locale_code', 'en-US')
            self.__format_region()
            self.__build_urls()
        except:
            raise RuntimeError(self.response.get('FAILED_ACTIVE'))

    def locale_response(self) -> LocalErrorResponse:
        '''This function is used to check if the local response is enabled.'''
        self.response = LocalErrorResponse('API', self.locale_code)
        return self.response

    # async def refresh_token(self) -> None:
        # cookies = self.cookie
        # cookies, accessToken, emt = await self.auth.redeem_cookies(cookies)

        # self.__build_headers()
        
    async def fetch(self, endpoint: str='/', url: str='pd', errors: Dict={}) -> Dict:

        self.locale_response()
        endpoint_url = getattr(self, url)
        
        data = None
        r = await self.session.get(f'{endpoint_url}{endpoint}', headers=self.headers)   
                
        try:
            data = json.loads(await r.text())
        except: # as no data is set, an exception will be raised later in the method
            pass
        
        if "httpStatus" not in data:
            return data

        if data["httpStatus"] == 400:
            response = LocalErrorResponse('AUTH', self.locale_code)
            raise RuntimeError(response.get('COOKIES_EXPIRED')) 
            # await self.refresh_token()
            # return await self.fetch(endpoint=endpoint, url=url, errors=errors)

    async def put(self, endpoint: str="/", url: str='pd', body: Dict={}, errors: Dict={}) -> Dict:
    
        self.locale_response()

        body = body if type(body) is list else json.dumps(body)

        endpoint_url = getattr(self, url)
        data = None

        r = await self.session.put(f'{endpoint_url}{endpoint}', headers=self.headers, data=body)
        data = json.loads(await r.text())

        if data is not None:
            return data
        else:
            raise RuntimeError(self.response.get('REQUEST_FAILED'))

    # contracts endpoints

    async def fetch_contracts(self) -> Dict:
        '''
        Contracts_Fetch
        Get a list of contracts and completion status including match history       
        '''
        data = await self.fetch(endpoint=f'/contracts/v1/contracts/{self.puuid}', url='pd')
        return data

    # PVP endpoints

    async def fetch_content(self) -> Dict:
        '''
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        '''
        data = await self.fetch(endpoint='/content-service/v3/content', url='shared')
        return data

    async def fetch_account_xp(self) -> Dict:
        '''
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        '''
        data = await self.fetch(endpoint=f'/account-xp/v1/players/{self.puuid}', url='pd')
        return data
    
    async def fetch_player_mmr(self, puuid:str=None) -> Dict:
        puuid = self.__check_puuid(puuid)
        data = await self.fetch(endpoint=f'/mmr/v1/players/{puuid}', url='pd')
        return data
   
    async def fetch_name_by_puuid(self, puuid:str=None) -> Dict:
        '''
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        '''
        if puuid is None:
            puuid = [self.__check_puuid()]
        elif puuid is not None and type(puuid) is str:
            puuid = [puuid]
        data = await self.put(endpoint='/name-service/v2/players', url='pd', body=puuid)
        return data
    
    async def fetch_player_loadout(self) -> Dict:
        '''
        playerLoadoutUpdate
        Get the player's current loadout
        '''
        data = await self.fetch(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd')
        return data

    async def put_player_loadout(self, loadout: Dict) -> Dict:
        '''
        playerLoadoutUpdate
        Use the values from `fetch_player_loadout` excluding properties like `subject` and `version.` Loadout changes take effect when starting a new game
        '''
        data = await self.put(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd', body=loadout)
        return data

    # store endpoints

    async def store_fetch_offers(self) -> Dict:
        '''
        Store_GetOffers
        Get prices for all store items
        '''
        data = await self.fetch('/store/v1/offers/', url='pd')
        return data 

    async def store_fetch_storefront(self) -> Dict:
        '''
        Store_GetStorefrontV2
        Get the currently available items in the store
        '''
        data = await self.fetch(f'/store/v2/storefront/{self.puuid}', url='pd')
        return data 

    async def store_fetch_wallet(self) -> Dict:
        '''
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7        
        '''
        data = await self.fetch(f'/store/v1/wallet/{self.puuid}', url='pd')
        return data 

    async def store_fetch_order(self, order_id: str) -> Dict:
        '''
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        '''
        data = await self.fetch(f'/store/v1/order/{order_id}', url='pd')
        return data 
    
    async def store_fetch_entitlements(self, item_type: Dict) -> Dict:
        '''
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
        '''
        data = await self.fetch(endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}", url="pd")
        return data
    
    # useful endpoints

    async def fetch_mission(self):
        '''
        Get player daily/weekly missions
        '''
        data = await self.fetch_contracts()
        mission = data["Missions"]
        return mission

    async def get_player_level(self):
        '''
        Aliases `fetch_account_xp` but received a level
        '''
        data = await self.fetch_account_xp()['Progress']['Level']
        return data
    
    async def get_player_tier_rank(self, puuid: str=None) -> str:
        '''
        get player current tier rank
        '''
        data = await self.fetch_player_mmr(puuid)
        season_id = data['LatestCompetitiveUpdate']['SeasonID']
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data["QueueSkills"]['competitive']['SeasonalInfoBySeasonID']
        current_Tier = current_season[season_id]['CompetitiveTier']
        return current_Tier

    # local utility functions
    
    async def __get_live_season(self) -> str:
        '''Get the UUID of the live competitive season'''
        content = self.fetch_content()
        season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        if not season_id:
            return await self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
        return season_id[0]

    def __check_puuid(self, puuid: str) -> str:
        '''If puuid passed into method is None make it current user's puuid'''
        return self.puuid if puuid is None else puuid
    
    def __build_urls(self) -> str:
        '''
        generate URLs based on region/shard
        '''
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    async def __build_headers(self, headers: Dict) -> Dict:
        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = await self._get_client_version()
        return headers
            
    def __format_region(self) -> None:
        self.shard = self.region
        if self.region in region_shard_override.keys():
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override.keys():
            self.region = shard_region_override[self.shard]

    async def _get_client_version(self) -> str:
        r = await self.session.get('https://valorant-api.com/v1/version')
        data = await r.json()
        data = data['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}" # return formatted version string

    async def _get_valorant_version(self):
        r = await self.session.get('https://valorant-api.com/v1/version')
        if r.status != 200:
            return None
        data = await r.json()
        data = data['data']
        return data['version']

