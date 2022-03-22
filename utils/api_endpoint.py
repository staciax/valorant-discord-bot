# Standard
import requests
import urllib3

# Local
from utils.json_loader import data_read

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client_platfrom = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'

class VALORANT_API:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.session = requests.session()
        if user_id is not None:
            database = data_read('users')

            self.puuid = database[str(user_id)]['puuid']
            self.IGN = database[str(user_id)]['IGN']
            self.headers = {
                'Authorization': "Bearer " + database[str(user_id)]['rso'],
                'X-Riot-Entitlements-JWT': database[str(user_id)]['emt'],
                'X-Riot-ClientVersion': self.__get_current_version(),
                'X-Riot-ClientPlatform': client_platfrom
            }
            self.region = database[str(user_id)]['region']

    # STORE endpoints
    def fetch(self, endpoint='/') -> dict:
        data = None
        r = self.session.get(f'https://pd.{self.region}.a.pvp.net{endpoint}', headers=self.headers, verify=False)
        if r.status_code == 200:
            data = r.json()
        if data is None:
            raise RuntimeError("API response failed")
        return data

    def store_fetch_offers(self) -> dict:
        '''Get Player' offer and duration'''
        data = self.fetch(f'/store/v2/storefront/{self.puuid}')
        skin_uuid = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
        
        return skin_uuid, duration

    def store_fetch_nightmarket(self) -> dict:
        '''Get Player' offer and duration'''
        data = self.fetch(f'/store/v2/storefront/{self.puuid}')
        
        night = data['BonusStore']['BonusStoreOffers']        
        duration = data['BonusStore']['BonusStoreRemainingDurationInSeconds']

        night_market = {}
        count = 0
        for x in night:
            count += 1
            price = *x['Offer']['Cost'].values(),
            Disprice = *x['DiscountCosts'].values(),
            night_market['skin' + f'{count}'] = {
                'uuid': x['Offer']['OfferID'],
                'name': self.get_skin_name(x['Offer']['OfferID']),
                'tier': self.get_skin_tier_icon(x['Offer']['OfferID']),
                'price': price[0],
                'disprice': Disprice[0]
        }

        return night_market, duration

    def store_fetch_price(self) -> dict:
        '''Get Skin price'''
        data = self.fetch('/store/v1/offers/')
        return data

    # Contracts ENDPOINT
    
    def fetch_contracts(self) -> dict:
        '''
        Get player daily/weekly missions/contracts
        '''
        data = self.fetch(f'/contracts/v1/contracts/{self.puuid}')
        return data

    def get_content(self):
        session = requests.session()
        r = session.get(f'https://shared.{self.region}.a.pvp.net/content-service/v3/content', headers=self.headers)
        data = None
        if r.status_code == 200:
            data = r.json()
        return data
    
    def get_active_season(self):
        content = self.get_content()
        season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        if not season_id:
            return {"success":False, "error":"Failed to get Current Season."}
        self.activeSeason = season_id[0]
        return {"success":True, "data": season_id[0]}

    # USEFUL

    def get_price(self, uuid) -> str:
        skindata = data_read('skins')
        '''Get Skin price by skin uuid'''
        try:
            cost = skindata["prices"][uuid]
        except KeyError:
            cost = '-'
        return cost
    
    def get_skin_tier_icon(self, skin) -> str:
        skindata = data_read('skins')
        '''Get Skin skin tier image'''
        tier_uuid = skindata["skins"][skin]['tier']
        tier = skindata['tiers'][tier_uuid]["icon"]
        return tier

    def get_skin_name(self, uuid):
        skindata = data_read('skins')
        '''Get Skin name'''
        skin_name = skindata["skins"][uuid]['name']
        return skin_name

    def get_skin_icon(self, uuid):
        skindata = data_read('skins')
        '''Get Skin icon'''      
        skin_icon = skindata["skins"][uuid]['icon']
        return skin_icon

    def get_skin_list(self, skin_id, duration) -> dict:
        skin_count = 0
        for skin in skin_id:
            if skin_count == 0:
                skin1_name = self.get_skin_name(skin)
                skin1_icon = self.get_skin_icon(skin)
                skin1_price = self.get_price(skin)
                skin1_tier = self.get_skin_tier_icon(skin)
                skin1_uuid = skin
            elif skin_count == 1:
                skin2_name = self.get_skin_name(skin)
                skin2_icon = self.get_skin_icon(skin)
                skin2_price = self.get_price(skin)
                skin2_tier = self.get_skin_tier_icon(skin)
                skin2_uuid = skin
            elif skin_count == 2:
                skin3_name = self.get_skin_name(skin)
                skin3_icon = self.get_skin_icon(skin)
                skin3_price = self.get_price(skin)
                skin3_tier = self.get_skin_tier_icon(skin)
                skin3_uuid = skin
            elif skin_count == 3:
                skin4_name = self.get_skin_name(skin)
                skin4_icon = self.get_skin_icon(skin)
                skin4_price = self.get_price(skin)
                skin4_tier = self.get_skin_tier_icon(skin)
                skin4_uuid = skin
            skin_count += 1

        skin_source = {
            'skin1': {'name': skin1_name, 'icon': skin1_icon, 'price': skin1_price, 'tier': skin1_tier, 'uuid': skin1_uuid},
            'skin2': {'name': skin2_name, 'icon': skin2_icon, 'price': skin2_price, 'tier': skin2_tier, 'uuid': skin2_uuid},
            'skin3': {'name': skin3_name, 'icon': skin3_icon, 'price': skin3_price, 'tier': skin3_tier, 'uuid': skin3_uuid},
            'skin4': {'name': skin4_name, 'icon': skin4_icon, 'price': skin4_price, 'tier': skin4_tier, 'uuid': skin4_uuid},
            'duration': duration
        }

        return skin_source

    def get_store_offer(self):
        try:
            # get_skin
            skin_id, duration = self.store_fetch_offers()
            skin_data = self.get_skin_list(skin_id, duration)
            skin_data['name_tagline'] = self.IGN

            self.session.close()
            return skin_data
        except RuntimeError as rt:
            raise RuntimeError(f'{rt}')

    def temp_store(self, puuid, header, region):
        self.puuid = puuid
        self.headers = header
        self.region = region
        
        skin_id, duration = self.store_fetch_offers()
        skin_data = self.get_skin_list(skin_id, duration)

        return skin_data

    def temp_night(self, puuid, header, region):
        self.puuid = puuid
        self.headers = header
        self.region = region
        return self.store_fetch_nightmarket()

    def __get_current_version(self) -> str:
        data = self.session.get('https://valorant-api.com/v1/version')
        data = data.json()['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}" # return formatted version string