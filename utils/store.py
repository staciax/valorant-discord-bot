# Standard
import requests
import urllib3

# Local
from utils.json_loader import data_read

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VALORANT_API:
    def __init__(self, user_id=None):
        self.user_id = user_id
        if user_id is not None:
            database = data_read('users')

            self.puuid = database[str(user_id)]['puuid']
            self.IGN = database[str(user_id)]['IGN']
            self.headers = {
                'Authorization': "Bearer " + database[str(user_id)]['rso'],
                'X-Riot-Entitlements-JWT': database[str(user_id)]['emt']
            }
            self.region = database[str(user_id)]['region']
        self.session = requests.session()

    # STORE endpoints
    def fetch(self, endpoint='/') -> dict:
        data = None
        r = self.session.get('https://pd.{region}.a.pvp.net{endpoint}'.format(region=self.region, endpoint=endpoint), headers=self.headers, verify=False)
        if r.status_code == 200:
            data = r.json()
        if data is None:
            raise RuntimeError("Failed to fetch store")
        return data

    def store_fetch_offers(self) -> dict:
        '''Get Player' offer and duration'''
        data = self.fetch('/store/v2/storefront/{puuid}'.format(puuid=self.puuid))
        skin_uuid = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
        
        return skin_uuid, duration

    def store_fetch_nightmarket(self) -> dict:
        '''Get Player' offer and duration'''
        data = self.fetch('/store/v2/storefront/{puuid}'.format(puuid=self.puuid))
        
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