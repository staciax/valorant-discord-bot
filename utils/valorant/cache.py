from __future__ import annotations

import json
import os
from typing import Dict, Optional

# Standard
import requests

# Local
from .useful import JSON, on_replit


def create_json(filename: str, formats: Dict) -> None:
    """Create a json file"""

    if on_replit:
        from replit import db

        db[filename] = formats
    else:
        file_path = f"data/" + filename + ".json"
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(formats, fp, indent=2)


def get_valorant_version() -> Optional[str]:
    """Get the valorant version from valorant-api.com"""

    print('Fetching Valorant version !')

    resp = requests.get('https://valorant-api.com/v1/version')

    return resp.json()['data']['manifestId']


def fetch_skin() -> None:
    """Fetch the skin from valorant-api.com"""

    data = JSON.read('cache')

    print('Fetching weapons skin !')
    resp = requests.get(f'https://valorant-api.com/v1/weapons/skins?language=all')
    if resp.status_code == 200:
        json = {}
        for skin in resp.json()['data']:
            skinone = skin['levels'][0]
            json[skinone['uuid']] = {
                'uuid': skinone['uuid'],
                'names': skin['displayName'],
                'icon': skinone['displayIcon'],
                'tier': skin['contentTierUuid'],
            }
        data['skins'] = json
        JSON.save('cache', data)


def fetch_tier() -> None:
    """Fetch the skin tier from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching tier skin !')

    resp = requests.get('https://valorant-api.com/v1/contenttiers/')
    if resp.status_code == 200:
        json = {}
        for tier in resp.json()['data']:
            json[tier['uuid']] = {
                'uuid': tier['uuid'],
                'name': tier['devName'],
                'icon': tier['displayIcon'],
            }
        data['tiers'] = json
        JSON.save('cache', data)


def pre_fetch_price() -> None:
    """Pre-fetch the price of all skins"""
    try:
        data = JSON.read('cache')
        pre_json = {'is_price': False}
        data['prices'] = pre_json
        JSON.save('cache', data)
    except Exception as e:
        print(e)
        print("Can't fetch price")


def fetch_mission() -> None:
    """Fetch the mission from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching mission !')

    resp = requests.get(f'https://valorant-api.com/v1/missions?language=all')
    if resp.status_code == 200:
        json = {}
        # json['version'] = get_valorant_version()
        for uuid in resp.json()['data']:
            json[uuid['uuid']] = {
                'uuid': uuid['uuid'],
                'titles': uuid['title'],
                'type': uuid['type'],
                'progress': uuid['progressToComplete'],
                'xp': uuid['xpGrant'],
            }
        data['missions'] = json
        JSON.save('cache', data)


def fetch_playercard() -> None:
    """Fetch the player card from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching Player cards !')
    resp = requests.get(f'https://valorant-api.com/v1/playercards?language=all')
    if resp.status_code == 200:
        payload = {}
        # json['version'] = get_valorant_version()
        for card in resp.json()['data']:
            payload[card['uuid']] = {
                'uuid': card['uuid'],
                'names': card['displayName'],
                'icon': {
                    'small': card['smallArt'],
                    'wide': card['wideArt'],
                    'large': card['largeArt'],
                },
            }
        data['playercards'] = payload
        JSON.save('cache', data)


def fetch_titles() -> None:
    """Fetch the player titles from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching Player titles !')

    resp = requests.get(f'https://valorant-api.com/v1/playertitles?language=all')
    if resp.status_code == 200:
        payload = {}
        for title in resp.json()['data']:
            payload[title['uuid']] = {'uuid': title['uuid'], 'names': title['displayName'], 'text': title['titleText']}
        data['titles'] = payload
        JSON.save('cache', data)


def fetch_spray() -> None:
    """Fetch the spray from valorant-api.com"""

    data = JSON.read('cache')
    session = requests.session()
    print('Fetching Sprays !')
    resp = requests.get(f'https://valorant-api.com/v1/sprays?language=all')
    if resp.status_code == 200:
        payload = {}
        for spray in resp.json()['data']:
            payload[spray['uuid']] = {
                'uuid': spray['uuid'],
                'names': spray['displayName'],
                'icon': spray['fullTransparentIcon'] or spray['displayIcon'],
            }
        data['sprays'] = payload
        JSON.save('cache', data)


def fetch_bundles() -> None:
    """Fetch all bundles from valorant-api.com and https://docs.valtracker.gg/bundles"""

    data = JSON.read('cache')
    print('Fetching bundles !')
    resp = requests.get(f'https://valorant-api.com/v1/bundles?language=all')
    if resp.status_code == 200:
        bundles = {}
        for bundle in resp.json()['data']:
            bundles[bundle['uuid']] = {
                'uuid': bundle['uuid'],
                'names': bundle['displayName'],
                'subnames': bundle['displayNameSubText'],
                'descriptions': bundle['extraDescription'],
                'icon': bundle['displayIcon2'],
                'items': None,
                'price': None,
                'basePrice': None,
                'expires': None,
            }

        resp2 = requests.get(f'https://api.valtracker.gg/bundles')

        for bundle2 in resp2.json()['data']:
            if bundle2['uuid'] in bundles:
                bundle = bundles[bundle2.get('uuid')]
                items = []
                default = {'amount': 1, 'discount': 0}
                for weapon in bundle2['weapons']:
                    items.append(
                        {
                            'uuid': weapon['levels'][0]['uuid'],
                            'type': 'e7c63390-eda7-46e0-bb7a-a6abdacd2433',
                            'price': weapon.get('price'),
                            **default,
                        }
                    )
                for buddy in bundle2['buddies']:  #
                    items.append(
                        {
                            'uuid': buddy['levels'][0]['uuid'],
                            'type': 'dd3bf334-87f3-40bd-b043-682a57a8dc3a',
                            'price': buddy.get('price'),
                            **default,
                        }
                    )
                for card in bundle2['cards']:  #
                    items.append(
                        {
                            'uuid': card['uuid'],
                            'type': '3f296c07-64c3-494c-923b-fe692a4fa1bd',
                            'price': card.get('price'),
                            **default,
                        }
                    )
                for spray in bundle2['sprays']:
                    items.append(
                        {
                            'uuid': spray['uuid'],
                            'type': 'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475',
                            'price': spray.get('price'),
                            **default,
                        }
                    )

                bundle['items'] = items
                bundle['price'] = bundle2['price']

        data['bundles'] = bundles
        JSON.save('cache', data)


def fetch_contracts() -> None:
    """Fetch contracts from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching Contracts !')
    resp = requests.get(f'https://valorant-api.com/v1/contracts?language=all')

    # IGNOR OLD BATTLE_PASS
    ignor_contract = [
        '7b06d4ce-e09a-48d5-8215-df9901376fa7',  # BP EP 1 ACT 1
        'ed0b331b-45f2-115c-c958-3c9683ff5b5e',  # BP EP 1 ACT 2
        'e5c5ee7c-ac93-4f3b-8b76-cc7a2c66bf24',  # BP EP 1 ACT 3
        '4cff28f8-47e9-62e5-2625-49a517f981d2',  # BP EP 2 ACT 1
        'd1dfd006-4efa-7ef2-a46f-3eb497fc26df',  # BP EP 2 ACT 2
        '5bef6de8-44d4-ac64-3df2-078e618fc0e3',  # BP EP 2 ACT 3
        'de37c775-4017-177a-8c64-a8bb414dae1f',  # BP EP 3 ACT 1
        'b0bd7062-4d62-1ff1-7920-b39622ee926b',  # BP EP 3 ACT 2
        'be540721-4d60-0675-a586-ecb14adcb5f7',  # BP EP 3 ACT 3
        '60f2e13a-4834-0a18-5f7b-02b1a97b7adb' '60f2e13a-4834-0a18-5f7b-02b1a97b7adb'  # BP EP 4 ACT 1  # BP EP 4 ACT 1
        # 'c1cd8895-4bd2-466d-e7ff-b489e3bc3775', # BP EP 4 ACT 2
    ]

    if resp.status_code == 200:
        json = {}
        for contract in resp.json()['data']:
            if not contract['uuid'] in ignor_contract:
                json[contract['uuid']] = {
                    'uuid': contract['uuid'],
                    'free': contract['shipIt'],
                    'names': contract['displayName'],
                    'icon': contract['displayIcon'],
                    'reward': contract['content'],
                }
        data['contracts'] = json
        JSON.save('cache', data)


# def fetch_ranktiers(lang: str):
#     """ Fetch rank tiers from from valorant-api.com """

#     data = JSON.read('cache')
#     session = requests.session()
#     print('Fetching ranktiers !')
#     resp = session.get(f'https://valorant-api.com/v1/competitivetiers?language={lang}')
#     if resp.status_code == 200:
#         json = {}
#         for rank in resp.json()['data']:
#             for i in rank['tiers']:
#                 json[i['tier']] = {
#                     'tier':i['tier'],
#                     'name':i['tierName'],
#                     'subname':i['divisionName'],
#                     'icon':i['largeIcon'],
#                     'rankup':i['rankTriangleUpIcon'],
#                     'rankdown':i['rankTriangleDownIcon'],
#                 }
#         data['ranktiers'] = json
#         JSON.save('cache', data)
#     session.close()


def fetch_currencies() -> None:
    """Fetch currencies from valorant-api.com"""

    data = JSON.read('cache')
    print('Fetching currencies !')
    resp = requests.get(f'https://valorant-api.com/v1/currencies?language=all')
    if resp.status_code == 200:
        payload = {}
        for currencie in resp.json()['data']:
            payload[currencie['uuid']] = {
                'uuid': currencie['uuid'],
                'names': currencie['displayName'],
                'icon': currencie['displayIcon'],
            }
        data['currencies'] = payload
        JSON.save('cache', data)


def fetch_buddies() -> None:
    """Fetch all buddies from valorant-api.com"""

    data = JSON.read('cache')

    print('Fetching buddies !')

    resp = requests.get(f'https://valorant-api.com/v1/buddies?language=all')
    if resp.status_code == 200:
        payload = {}
        for buddy in resp.json()['data']:
            buddy_one = buddy['levels'][0]
            payload[buddy_one['uuid']] = {
                'uuid': buddy_one['uuid'],
                'names': buddy['displayName'],
                'icon': buddy_one['displayIcon'],
            }
        data['buddies'] = payload
        JSON.save('cache', data)


def fetch_price(data_price: Dict) -> None:
    """Fetch the price of a skin"""

    data = JSON.read('cache')
    payload = {}
    for skin in data_price['Offers']:
        if skin["OfferID"] in data['skins']:
            (*cost,) = skin["Cost"].values()
            payload[skin['OfferID']] = cost[0]
    # prices['is_price'] = True
    data['prices'] = payload
    JSON.save('cache', data)


# def fetch_skinchromas() -> None:
#     """ Fetch skin chromas from valorant-api.com """

#     create_json('skinchromas', {})

#     data = JSON.read('skinchromas')
#     session = requests.session()

#     print('Fetching season !')

#     resp = session.get('https://valorant-api.com/v1/weapons/skinchromas?language=all')
#     if resp.status_code == 200:
#         json = {}
#         # json['version'] = get_valorant_version()
#         for chroma in resp.json()['data']:
#             json[chroma['uuid']] = {
#                 'uuid': chroma['uuid'],
#                 'names': chroma['displayName'],
#                 'icon': chroma['displayIcon'],
#                 'full_render': chroma['fullRender'],
#                 'swatch': chroma['swatch'],
#                 'video': chroma['streamedVideo'],
#             }

#         data['chromas'] = json
#         JSON.save('skinchromas', data)

#     session.close()


def get_cache() -> None:
    """Get all cache from valorant-api.com"""

    create_json('cache', {"valorant_version": get_valorant_version()})

    fetch_skin()
    fetch_tier()
    pre_fetch_price()
    fetch_bundles()
    fetch_playercard()
    fetch_currencies()
    fetch_titles()
    fetch_spray()
    fetch_buddies()
    fetch_mission()
    fetch_contracts()
    # fetch_skinchromas() # next update

    print('Loaded Cache')
