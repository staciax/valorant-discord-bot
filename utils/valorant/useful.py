from __future__ import annotations

import contextlib
import json
import os
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import discord
from dotenv import load_dotenv

from ..errors import ValorantBotError
from ..locale_v2 import ValorantTranslator
from .resources import get_item_type, points as points_emoji, tiers as tiers_resources

load_dotenv()
global on_replit
on_replit = bool(os.getenv('ON_REPLIT'))

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot

current_season_id = '99ac9283-4dd3-5248-2e01-8baf778affb4'
current_season_end = datetime(2022, 8, 24, 17, 0, 0)


def is_valid_uuid(value: str) -> bool:
    """
    Checks if a string is a valid UUID.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


# ---------- ACT SEASON ---------- #


def get_season_by_content(content: dict) -> dict[str, Any]:
    """Get season id by content"""

    try:
        season_data = [season for season in content['Seasons'] if season['IsActive'] and season['Type'] == 'act']
        season_id = season_data[0]['ID']
        season_end = iso_to_time(season_data[0]['EndTime'])

    except (IndexError, KeyError, TypeError):
        season_id = current_season_id
        season_end = current_season_end

    return {'id': season_id, 'end': season_end}


def calculate_level_xp(level: int) -> int:  # https://github.com/giorgi-o
    """Calculate XP needed to reach a level"""

    level_multiplier = 750
    if 2 <= level <= 50:
        return 2000 + (level - 2) * level_multiplier
    elif 51 <= level <= 55:
        return 36500
    else:
        return 0


# ---------- TIME UTILS ---------- #


def iso_to_time(iso: str) -> datetime:
    """Convert ISO time to datetime"""
    timestamp = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S%z').timestamp()
    time = datetime.utcfromtimestamp(timestamp)
    return time


def format_dt(dt: datetime, style: str | None = None) -> str:
    """datatime to time format"""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'


def format_relative(dt: datetime) -> str:
    """datatime to relative time format"""
    return format_dt(dt, 'R')


# ---------- JSON LOADER ---------- #


def data_folder() -> None:
    """Get the data folder"""
    # create data folder
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'data')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)


class JSON:
    @staticmethod
    def read(filename: str, force: bool = True) -> dict[str, Any]:
        """Read json file"""
        try:
            if on_replit:
                from replit import db  # type: ignore

                data = db[filename]
            else:
                with open('data/' + filename + '.json', encoding='utf-8') as json_file:
                    data = json.load(json_file)
        except (FileNotFoundError, KeyError):
            from .cache import create_json

            if force:
                create_json(filename, {})
                return JSON.read(filename, False)
        return data

    @staticmethod
    def save(filename: str, data: dict[str, Any]) -> None:
        """Save data to json file"""
        try:
            if on_replit:
                from replit import db  # type: ignore

                db[filename] = data
            else:
                with open('data/' + filename + '.json', 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, indent=2, ensure_ascii=False)
        except (FileNotFoundError, KeyError):
            from .cache import create_json

            create_json(filename, {})
            return JSON.save(filename, data)


# ---------- GET DATA ---------- #


class GetItems:
    @classmethod
    def get_item_by_type(cls, Itemtype: str, uuid: str) -> dict[str, Any]:  # type: ignore
        """Get item by type"""

        item_type = get_item_type(Itemtype)
        if item_type == 'Agents':
            ...
        elif item_type == 'Contracts':
            return cls.get_contract(uuid)
        elif item_type == 'Sprays':
            return cls.get_spray(uuid)
        elif item_type == 'Gun Buddies':
            return cls.get_buddie(uuid)
        elif item_type == 'Player Cards':
            return cls.get_playercard(uuid)
        elif item_type == 'Skins':
            return cls.get_skin(uuid)
        elif item_type == 'Skins chroma':
            ...
        elif item_type == 'Player titles':
            return cls.get_title(uuid)

    @staticmethod
    def get_skin(uuid: str) -> dict[str, Any]:
        """Get Skin data"""
        try:
            skin_data = JSON.read('cache')
            skin = skin_data['skins'][uuid]
        except KeyError as e:
            raise ValorantBotError('Some skin data is missing, plz use `/debug cache`') from e
        return skin

    @staticmethod
    def get_skin_price(uuid: str) -> str:
        """Get Skin price by skin uuid"""

        data = JSON.read('cache')
        price = data['prices']
        try:
            cost = price[uuid]
        except Exception:
            cost = '-'
        return cost

    @staticmethod
    def get_skin_tier_icon(skin: str) -> str:
        """Get Skin skin tier image"""

        skindata = JSON.read('cache')
        tier_uuid = skindata['skins'][skin]['tier']
        tier = skindata['tiers'][tier_uuid]['icon']
        return tier

    @staticmethod
    def get_spray(uuid: str) -> Any:
        """Get Spray"""

        data = JSON.read('cache')
        spray = None
        with contextlib.suppress(Exception):
            spray = data['sprays'][uuid]
        return spray

    @staticmethod
    def get_title(uuid: str) -> Any:
        """Get Title"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data['titles'][uuid]
        return title

    @staticmethod
    def get_playercard(uuid: str) -> Any:
        """Get Player card"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data['playercards'][uuid]
        return title

    @staticmethod
    def get_buddie(uuid: str) -> Any:
        """Get Buddie"""

        data = JSON.read('cache')
        title = None
        with contextlib.suppress(Exception):
            title = data['buddies'][uuid]
        return title

    @staticmethod
    def get_skin_lvl_or_name(name: str, uuid: str) -> Any:
        """Get Skin uuid by name"""

        data = JSON.read('cache')
        skin = None
        with contextlib.suppress(Exception):
            skin = data['skins'][uuid]
        with contextlib.suppress(Exception):
            if skin is None:
                skin = [data['skins'][x] for x in data['skins'] if data['skins'][x]['name'] in name][0]
        return skin

    @staticmethod
    def get_tier_name(skin_uuid: str) -> str | None:
        """Get tier name by skin uuid"""

        try:
            data = JSON.read('cache')
            uuid = data['skins'][skin_uuid]['tier']
            name = data['tiers'][uuid]['name']
        except KeyError as e:
            raise ValorantBotError('Some skin data is missing, plz use `/debug cache`') from e
        return name

    @staticmethod
    def get_contract(uuid: str) -> Any:
        """Get contract by uuid"""

        data = JSON.read('cache')
        contract = None
        with contextlib.suppress(Exception):
            contract = data['contracts'][uuid]
        return contract

    @staticmethod
    def get_bundle(uuid: str) -> Any:
        """Get bundle by uuid"""

        data = JSON.read('cache')
        bundle = None
        with contextlib.suppress(Exception):
            bundle = data['bundles'][uuid]
        return bundle


# ---------- GET EMOJI ---------- #


class GetEmoji:
    @staticmethod
    def tier(skin_uuid: str) -> discord.Emoji:
        """Get tier emoji"""

        data = JSON.read('cache')
        uuid = data['skins'][skin_uuid]['tier']
        uuid = data['tiers'][uuid]['uuid']
        emoji = tiers_resources[uuid]['emoji']
        return emoji

    @classmethod
    def tier_by_bot(cls, skin_uuid: str, bot: ValorantBot) -> discord.Emoji:
        """Get tier emoji from bot"""

        emoji = discord.utils.get(bot.emojis, name=GetItems.get_tier_name(skin_uuid) + 'Tier')  # type: ignore
        if emoji is None:
            return cls.tier(skin_uuid)
        return emoji

    @staticmethod
    def point_by_bot(point: str, bot: ValorantBot) -> discord.Emoji | str | None:
        """Get point emoji from bot"""

        emoji = discord.utils.get(bot.emojis, name=point)
        if emoji is None:
            return points_emoji.get(point)
        return emoji


# ---------- UTILS FOR STORE EMBED ---------- #


class GetFormat:
    @staticmethod
    def offer_format(data: dict[str, Any]) -> dict[str, Any]:
        """Get skins list"""

        offer_list = data['SkinsPanelLayout']['SingleItemOffers']
        duration = data['SkinsPanelLayout']['SingleItemOffersRemainingDurationInSeconds']

        skin_count = 0
        skin_source = {}

        for skin_count, skin_id in enumerate(offer_list):
            skin = GetItems.get_skin(skin_id)
            name, icon = skin['names'][str(VLR_locale)], skin['icon']

            price = GetItems.get_skin_price(skin_id)
            tier_icon = GetItems.get_skin_tier_icon(skin_id)

            if skin_count == 0:
                skin1 = {'name': name, 'icon': icon, 'price': price, 'tier': tier_icon, 'uuid': skin_id}
            elif skin_count == 1:
                skin2 = {'name': name, 'icon': icon, 'price': price, 'tier': tier_icon, 'uuid': skin_id}
            elif skin_count == 2:
                skin3 = {'name': name, 'icon': icon, 'price': price, 'tier': tier_icon, 'uuid': skin_id}
            elif skin_count == 3:
                skin4 = {'name': name, 'icon': icon, 'price': price, 'tier': tier_icon, 'uuid': skin_id}

        skin_source = {'skin1': skin1, 'skin2': skin2, 'skin3': skin3, 'skin4': skin4, 'duration': duration}

        return skin_source

    # ---------- UTILS FOR MISSION EMBED ---------- #

    @staticmethod
    def mission_format(data: dict[str, Any]) -> dict[str, Any]:
        """Get mission format"""

        mission = data['Missions']

        weekly = []
        daily = []
        newplayer = []
        daily_end = ''
        try:
            weekly_end = data['MissionMetadata']['WeeklyRefillTime']
        except KeyError:
            weekly_end = ''

        def get_mission_by_id(ID: str) -> str | None:
            data = JSON.read('cache')
            mission = data['missions'][ID]
            return mission

        for m in mission:
            mission = get_mission_by_id(m['ID'])
            (*complete,) = m['Objectives'].values()
            title = mission['titles'][str(VLR_locale)]  # type: ignore
            progress = mission['progress']  # type: ignore
            xp = mission['xp']  # type: ignore

            format_m = f'\n{title} | **+ {xp:,} XP**\n- **`{complete[0]}/{progress}`**'

            if mission['type'] == 'EAresMissionType::Weekly':  # type: ignore
                weekly.append(format_m)
            if mission['type'] == 'EAresMissionType::Daily':  # type: ignore
                daily_end = m['ExpirationTime']
                daily.append(format_m)
            if mission['type'] == 'EAresMissionType::NPE':  # type: ignore
                newplayer.append(format_m)

        misson_data = {
            'daily': daily,
            'weekly': weekly,
            'daily_end': daily_end,
            'weekly_end': weekly_end,
            'newplayer': newplayer,
        }
        return misson_data

    # ---------- UTILS FOR NIGHTMARKET EMBED ---------- #

    @staticmethod
    def nightmarket_format(offer: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        """Get Nightmarket offers"""

        try:
            night_offer = offer['BonusStore']['BonusStoreOffers']
        except KeyError as e:
            raise ValorantBotError(response.get('NIGMARKET_HAS_END', 'Nightmarket has been ended')) from e
        duration = offer['BonusStore']['BonusStoreRemainingDurationInSeconds']

        night_market = {}
        for count, x in enumerate(night_offer):
            count += 1
            price = (*x['Offer']['Cost'].values(),)
            Disprice = (*x['DiscountCosts'].values(),)

            uuid = x['Offer']['OfferID']
            skin = GetItems.get_skin(uuid)
            name = skin['names'][str(VLR_locale)]
            icon = skin['icon']
            tier = GetItems.get_skin_tier_icon(uuid)

            night_market['skin' + f'{count + 1}'] = {
                'uuid': uuid,
                'name': name,
                'tier': tier,
                'icon': icon,
                'price': price[0],
                'disprice': Disprice[0],
            }
        data = {'nightmarket': night_market, 'duration': duration}
        return data

    # ---------- UTILS FOR BATTLEPASS EMBED ---------- #

    @staticmethod
    def __get_item_battlepass(type: str, uuid: str, response: dict[str, Any]) -> dict[str, Any]:
        """Get item battle pass by type and uuid"""

        if type == 'Currency':
            data = JSON.read('cache')
            name = data['currencies'][uuid]['names'][str(VLR_locale)]
            icon = data['currencies'][uuid]['icon']
            item_type = response.get('POINT', 'Point')
            return {'success': True, 'data': {'type': item_type, 'name': '10 ' + name, 'icon': icon}}

        elif type == 'PlayerCard':
            data = JSON.read('cache')
            name = data['playercards'][uuid]['names'][str(VLR_locale)]
            icon = data['playercards'][uuid]['icon']['wide']
            item_type = response.get('PLAYER_CARD', 'Player Card')
            return {'success': True, 'data': {'type': item_type, 'name': name, 'icon': icon}}

        elif type == 'Title':
            data = JSON.read('cache')
            name = data['titles'][uuid]['names'][str(VLR_locale)]
            item_type = response.get('PLAYER_TITLE', 'Title')
            return {'success': True, 'data': {'type': item_type, 'name': name, 'icon': False}}

        elif type == 'Spray':
            data = JSON.read('cache')
            name = data['sprays'][uuid]['names'][str(VLR_locale)]
            icon = data['sprays'][uuid]['icon']
            item_type = response.get('SPRAY', 'Spray')
            return {'success': True, 'data': {'type': item_type, 'name': name, 'icon': icon}}

        elif type == 'EquippableSkinLevel':
            data = JSON.read('cache')
            name = data['skins'][uuid]['names'][str(VLR_locale)]
            icon = data['skins'][uuid]['icon']
            item_type = response.get('SKIN', 'Skin')
            return {'success': True, 'data': {'type': item_type, 'name': name, 'icon': icon}}

        elif type == 'EquippableCharmLevel':
            data = JSON.read('cache')
            name = data['buddies'][uuid]['names'][str(VLR_locale)]
            icon = data['buddies'][uuid]['icon']
            item_type = response.get('BUDDY', 'Buddie')
            return {'success': True, 'data': {'type': item_type, 'name': name, 'icon': icon}}

        return {'success': False, 'error': f'Failed to get : {type}'}

    @staticmethod
    def __get_contract_tier_reward(tier: int, reward: list[dict[str, Any]]) -> dict[str, Any]:
        """Get tier reward"""

        data = {}
        count = 0

        for lvl in reward:
            for rw in lvl['levels']:
                count += 1
                data[count] = rw['reward']

        next_reward = tier + 1
        if tier == 55:
            next_reward = 55
        current_reward = data[next_reward]

        return current_reward

    @staticmethod
    def __get_contracts_by_season_id(
        contracts: dict[str, Any], data_contracts: dict[str, Any], season_id: str
    ) -> dict[str, Any]:
        """Get battle pass info"""

        contracts_uuid = [
            x
            for x in data_contracts['contracts']
            if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id
        ]
        if contracts_uuid:
            battlepass = [x for x in contracts if x['ContractDefinitionID'] == contracts_uuid[0]]  # type: ignore
            TIER = battlepass[0]['ProgressionLevelReached']  # type: ignore
            XP = battlepass[0]['ProgressionTowardsNextLevel']  # type: ignore
            REWARD = data_contracts['contracts'][contracts_uuid[0]]['reward']['chapters']
            ACT = data_contracts['contracts'][contracts_uuid[0]]['names'][str(VLR_locale)]

            return {'success': True, 'tier': TIER, 'xp': XP, 'reward': REWARD, 'act': ACT}

        return {'success': False, 'error': 'Failed to get battlepass info'}

    @classmethod
    def battlepass_format(cls, data: dict[str, Any], season: str, response: dict[str, Any]) -> dict[str, Any]:
        """Get battle pass format"""

        data = data['Contracts']
        contracts = JSON.read('cache')
        # data_contracts['contracts'].pop('version')

        season_id = season['id']  # type: ignore
        season_end = season['end']  # type: ignore

        btp = cls.__get_contracts_by_season_id(data, contracts, season_id)
        if btp['success']:
            tier, act, xp, reward = btp['tier'], btp['act'], btp['xp'], btp['reward']

            item_reward = cls.__get_contract_tier_reward(tier, reward)
            item = cls.__get_item_battlepass(item_reward['type'], item_reward['uuid'], response)

            item_name = item['data']['name']
            item_type = item['data']['type']
            item_icon = item['data']['icon']

            return {
                'data': {
                    'tier': tier,
                    'act': act,
                    'xp': xp,
                    'reward': item_name,
                    'type': item_type,
                    'icon': item_icon,
                    'end': season_end,
                    'original_type': item_reward['type'],
                }
            }

        raise ValorantBotError('Failed to get battlepass info')
