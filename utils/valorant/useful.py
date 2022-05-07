import discord
import json
import os
import contextlib
from discord.ext import commands
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Literal

from .resources import tiers as tiers_resources, points as points_emoji, get_item_type

# ---------- ACT SEASON ---------- #

def get_season_by_content(content: Dict) -> Tuple[str, str]:
    '''Get season id by content'''

    try:
        season_data = [season for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        season_id = season_data[0]['ID']
        season_end = DateUtils.iso_to_time(season_data[0]['EndTime'])
        
    except (IndexError, KeyError, TypeError):
        season_id = 'd80f3ef5-44f5-8d70-6935-f2840b2d3882'
        season_end = datetime(2022, 6, 22, 17, 0, 0)
    
    return {'id': season_id, 'end': season_end}

def calculate_level_xp(level: int) -> int: # https://github.com/giorgi-o
    """Calculate XP needed to reach a level"""
    
    level_multiplier = 750
    if level >= 2 and level <= 50:
        return 2000 + (level - 2) * level_multiplier
    elif level >= 51 and level <= 55:
        return 36500
    else:
        return 0

# ---------- TIME UTILS ---------- #

class DateUtils:

    def iso_to_time(iso: datetime) -> datetime:
        '''Convert ISO time to datetime'''
        timestamp = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z").timestamp()
        time = datetime.utcfromtimestamp(timestamp)
        return time

    def format_dt(dt: datetime, style: str=None) -> str: #style 'R' or 'd'
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        if style is None:
            return f'<t:{int(dt.timestamp())}>'
        return f'<t:{int(dt.timestamp())}:{style}>'

    @classmethod
    def format_relative(cls, dt: datetime) -> str:
        return cls.format_dt(dt, 'R')

# ---------- JSON LOADER ---------- #

def data_folder():
    # create data folder
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'data')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

class JSON:

    def read(filename: str, force=True) -> Dict:
        """Read json file"""
        try:
            with open("data/" + filename + ".json", "r", encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            from .cache import create_json
            if force:
                create_json(filename, {})
                return JSON.read(filename)        
        return data

    def save(filename: str, data: Dict) -> None:
        """Save data to json file"""
        try:
            with open("data/" + filename + ".json", 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            from .cache import create_json
            create_json(filename, {})
            return JSON.save(filename, data)

# ---------- GET DATA ---------- #

class GetItems:

    @classmethod
    def get_item_by_type(cls, Itemtype: str, uuid: str) -> Dict:
        item_type = get_item_type(Itemtype)
        if item_type == 'Agents': ...
        elif item_type == 'Contracts': return cls.get_contract(uuid)
        elif item_type == 'Sprays': return cls.get_spray(uuid)
        elif item_type == 'Gun Buddies': return cls.get_buddie(uuid)
        elif item_type == 'Player Cards': return cls.get_playercard(uuid)
        elif item_type == 'Skins': return cls.get_skin(uuid)
        elif item_type == 'Skins chroma': ...
        elif item_type == 'Player titles': return cls.get_title(uuid)
            
    def get_skin(uuid: str):
        '''Get Skin data'''
        try:
            
            skindata = JSON.read('cache')
            skin = skindata["skins"][uuid]
        except KeyError:
            raise RuntimeError('Some skin data is missing, plz use `/fix cache`')
        return skin

    def get_skin_price(uuid: str) -> str:
        """Get Skin price by skin uuid"""

        data = JSON.read('cache')
        price = data["prices"]
        try:
            cost = price[uuid]
        except:
            cost = '-'
        return cost

    def get_skin_tier_icon(skin: str) -> str:
        '''Get Skin skin tier image'''

        skindata = JSON.read('cache')
        tier_uuid = skindata["skins"][skin]['tier']
        tier = skindata['tiers'][tier_uuid]["icon"]
        return tier

    def get_spray(uuid: str) -> Dict:
        """Get Spray"""

        data = JSON.read('cache')
        spray = None
        with contextlib.suppress(Exception):
            spray = data["sprays"][uuid]  
        return spray

    def get_title(uuid: str) -> Dict:
        """Get Title"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data["titles"][uuid]     
        return title

    def get_playercard(uuid: str) -> Dict:
        """Get Playercard"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data["playercards"][uuid]     
        return title

    def get_buddie(uuid: str) -> Dict:
        """Get Buddie"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data["buddies"][uuid]     
        return title

    def get_skin_lvl_or_name(name: str, uuid: str) -> Dict:
        """Get Skin uuid by name"""
        data = JSON.read('cache')
        skin = None
        with contextlib.suppress(Exception):
            skin = data["skins"][uuid]
        with contextlib.suppress(Exception):
            if skin is None:
                skin = [data["skins"][x] for x in data["skins"] if data["skins"][x]['name'] in name][0]
        return skin

    def get_tier_name(skin_uuid: str) -> str:
        try:
            data = JSON.read('cache')
            uuid = data['skins'][skin_uuid]['tier']
            name = data['tiers'][uuid]['name']
        except KeyError:
            raise RuntimeError('Some skin data is missing, plz use `/fix cache`')
        return name

    def get_contract(uuid: str) -> Dict:
        data = JSON.read('cache')
        contract = None
        with contextlib.suppress(Exception):
            contract = data["contracts"][uuid]
        return contract

    def get_bundle(uuid: str) -> Dict:
        data = JSON.read('cache')
        bundle = None
        with contextlib.suppress(Exception):
            bundle = data["bundles"][uuid]
        return bundle

# ---------- GET EMOJI ---------- #

class GetEmoji:

    def tier(skin_uuid: str) -> discord.Emoji:
        data = JSON.read('cache')
        uuid = data['skins'][skin_uuid]['tier']
        uuid = data['tiers'][uuid]['uuid']
        emoji = tiers_resources[uuid]['emoji']
        return emoji

    @classmethod
    def tier_by_bot(cls, skin_uuid: str, bot: commands.Bot) -> discord.Emoji:
        emoji = discord.utils.get(bot.emojis, name= GetItems.get_tier_name(skin_uuid) + 'Tier')
        if emoji is None:
            return cls.tier(skin_uuid)
        return emoji

    def point_by_bot(point: Literal['ValorantPointIcon', 'RadianitePointIcon'], bot: commands.Bot) -> discord.Emoji:
        emoji = discord.utils.get(bot.emojis, name=point)
        if emoji is None:
            return points_emoji.get(point)
        return emoji

# ---------- UTILS FOR STORE EMBED ---------- #

class GetFormat:

    def offer_format(data: Dict, language: str) -> Dict:
        '''Get skins list'''

        offer_list = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]

        skin_count = 0
        skin_source = {}
        
        for uuid in offer_list:
            skin =  GetItems.get_skin(uuid)
            name, icon = skin['names'][language], skin['icon']

            price = GetItems.get_skin_price(uuid)
            tier_icon = GetItems.get_skin_tier_icon(uuid)

            if skin_count == 0:
                skin1 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 1:
                skin2 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 2:
                skin3 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 3:
                skin4 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            skin_count += 1

        skin_source = {
            'skin1': skin1,
            'skin2': skin2,
            'skin3': skin3,
            'skin4': skin4,
            'duration': duration
        }

        return skin_source

    # ---------- UTILS FOR MISSION EMBED ---------- #

    def mission_format(data: Dict, language: str) -> Dict[str, str]:
        '''Get mission format'''

        mission = data["Missions"]

        weekly = []
        daily = []
        newplayer = []
        daily_end = ''
        try:
            weekly_end = data['MissionMetadata']['WeeklyRefillTime']
        except KeyError:
            weekly_end = ''

        def get_mission_by_id(ID):
            data = JSON.read('cache')
            mission = data['missions'][ID]
            return mission
        
        for m in mission:
            mission = get_mission_by_id(m['ID'])
            *complete, = m['Objectives'].values()
            title = mission['titles'][language]
            progress = mission['progress']
            xp = mission['xp']

            format_m = f"\n{title} | **+ {xp:,} XP**\n- **`{complete[0]}/{progress}`**"

            if mission['type'] == 'EAresMissionType::Weekly':
                weekly.append(format_m)
            if mission['type'] == 'EAresMissionType::Daily':
                daily_end = m['ExpirationTime']
                daily.append(format_m)
            if mission['type'] == 'EAresMissionType::NPE':
                newplayer.append(format_m)

        misson_data = dict(daily=daily, weekly=weekly, daily_end=daily_end, weekly_end=weekly_end, newplayer=newplayer)
        return misson_data

    # ---------- UTILS FOR NIGHTMARKET EMBED ---------- #

    def nightmarket_format(offer: Dict, language: str, response: Dict) -> Dict:
        '''Get Nightmarket offers'''
        try:
            night_offer = offer['BonusStore']['BonusStoreOffers']     
        except KeyError:
            raise RuntimeError(response.get('NIGMARKET_HAS_END', 'Nightmarket has been ended'))      
        duration = offer['BonusStore']['BonusStoreRemainingDurationInSeconds']

        night_market = {}
        count = 0
        for x in night_offer:
            count += 1
            price = *x['Offer']['Cost'].values(),
            Disprice = *x['DiscountCosts'].values(),

            uuid = x['Offer']['ID']
            skin = GetItems.get_skin(uuid)
            name = skin['names'][language]
            icon = skin['icon']
            tier = GetItems.get_skin_tier_icon(uuid)

            night_market['skin' + f'{count}'] = {
                'uuid': uuid,
                'name': name,
                'tier': tier,
                'icon': icon,
                'price': price[0],
                'disprice': Disprice[0]
            }
        data = {
            'nightmarket': night_market,
            'duration': duration
        }
        return data

    # ---------- UTILS FOR BATTLEPASS EMBED ---------- #

    def __get_item_battlepass(type: str, uuid: str, language: str, response: Dict) -> Dict:
        """Get item battlepass by type and uuid"""
        
        if type == 'Currency':
            data = JSON.read('cache')
            name = data['currencies'][uuid]['names'][language]
            icon = data['currencies'][uuid]['icon']
            item_type = response.get('POINT', 'Point')
            return {"success": True, "data": {'type': item_type, 'name': '10 '+ name, 'icon': icon}}
        
        elif type == 'PlayerCard':
            data = JSON.read('cache')
            name = data['playercards'][uuid]['names'][language]
            icon = data['playercards'][uuid]['icon']['wide']
            item_type = response.get('PLAYER_CARD', 'Player Card')
            return {"success": True, "data": {'type': item_type, 'name':name, 'icon': icon}}
        
        elif type == 'Title':
            data = JSON.read('cache')
            name = data['titles'][uuid]['names'][language]
            item_type = response.get('PLAYER_TITLE', 'Title')
            return {"success": True, "data": {'type': item_type, 'name':name, 'icon': False}}
        
        elif type == 'Spray':
            data = JSON.read('cache')
            name = data['sprays'][uuid]['names'][language]
            icon = data['sprays'][uuid]['icon']
            item_type = response.get('SPRAY', 'Spray')
            return {"success": True, "data": {'type': item_type, 'name':name, 'icon': icon}}
        
        elif type == 'EquippableSkinLevel':
            data = JSON.read('cache')
            name = data['skins'][uuid]['names'][language]
            icon = data['skins'][uuid]['icon']
            item_type = response.get('SKIN', 'Skin')
            return {"success": True, "data": {'type': item_type, 'name':name, 'icon': icon}}
        
        elif type == 'EquippableCharmLevel':
            data = JSON.read('cache')
            name = data['buddies'][uuid]['names'][language]
            icon = data['buddies'][uuid]['icon']
            item_type = response.get('BUDDY', 'Buddie')
            return {"success": True, "data": {'type': item_type, 'name':name, 'icon': icon}}
        
        return {"success": False, "error": f"Failed to get : {type}"}

    def __get_contract_tier_reward(tier: int, reward: List[Dict]) -> Dict:
        '''Get tier reward'''

        data = {}
        count = 0

        for lvl in reward:
            for rw in lvl["levels"]:
                count += 1
                data[count] = rw['reward']
        
        next_reward = tier + 1
        if tier == 55: next_reward = 55
        current_reward = data[next_reward]

        return current_reward

    def __get_contracts_by_season_id(contracts: Dict, data_contracts: Dict, season_id: str, language:str) -> Dict:
        '''Get battlepass info'''

        contracts_uuid = [x for x in data_contracts['contracts'] if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id]
        if contracts_uuid:
            battlepass = [x for x in contracts if x['ContractDefinitionID'] == contracts_uuid[0]]
            TIER = battlepass[0]['ProgressionLevelReached']  
            XP = battlepass[0]['ProgressionTowardsNextLevel']
            REWARD = data_contracts['contracts'][contracts_uuid[0]]['reward']['chapters']
            ACT = data_contracts['contracts'][contracts_uuid[0]]['names'][language]

            return {"success": True, 'tier': TIER, 'xp': XP, 'reward': REWARD, 'act': ACT}
        
        return {"success": False, "error": "Failed to get battlepass info"}

    @classmethod
    def battlepass_format(cls, data: Dict, season: str, language: str, response: Dict) -> Dict:
        
        data = data['Contracts']
        contracts = JSON.read('cache')
        # data_contracts['contracts'].pop('version')

        season_id = season['id']
        season_end = season['end']

        btp = cls.__get_contracts_by_season_id(data, contracts, season_id, language)
        if btp['success']:
            tier, act, xp, reward = btp['tier'], btp['act'], btp['xp'], btp['reward']

            item_reward = cls.__get_contract_tier_reward(tier, reward)
            item = cls.__get_item_battlepass(item_reward['type'], item_reward['uuid'], language, response)

            item_name = item['data']['name']
            item_type = item['data']['type']
            item_icon = item['data']['icon']
                        
            return dict(data=dict(tier=tier, act=act, xp=xp, reward=item_name, type=item_type, icon=item_icon, end=season_end, original_type=item_reward['type']))

        raise RuntimeError(f"Failed to get battlepass info")