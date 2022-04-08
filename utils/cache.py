import os
import json
import requests
from utils.json_loader import data_read, data_save
from datetime import datetime, timezone, timedelta

# VALORANT-API.COM

def get_valorant_version():
    session = requests.session()
    
    print('Fetching Valorant version !')
    
    r = session.get('https://valorant-api.com/v1/version')
    session.close() 
    return r.json()['data']['manifestId']

def fetch_contracts():

    data = data_read('contracts')
    session = requests.session()
    print('Fetching Contracts !')
    r = session.get(f'https://valorant-api.com/v1/contracts')

    # IGNOR OLD BATTLE_PASS
    ignor_contract = [
        '7b06d4ce-e09a-48d5-8215-df9901376fa7', # BP EP 1 ACT 1
        'ed0b331b-45f2-115c-c958-3c9683ff5b5e', # BP EP 1 ACT 2
        'e5c5ee7c-ac93-4f3b-8b76-cc7a2c66bf24', # BP EP 1 ACT 3
        '4cff28f8-47e9-62e5-2625-49a517f981d2', # BP EP 2 ACT 1
        'd1dfd006-4efa-7ef2-a46f-3eb497fc26df', # BP EP 2 ACT 2
        '5bef6de8-44d4-ac64-3df2-078e618fc0e3', # BP EP 2 ACT 3
        'de37c775-4017-177a-8c64-a8bb414dae1f', # BP EP 3 ACT 1
        'b0bd7062-4d62-1ff1-7920-b39622ee926b', # BP EP 3 ACT 2
        'be540721-4d60-0675-a586-ecb14adcb5f7', # BP EP 3 ACT 3
        '60f2e13a-4834-0a18-5f7b-02b1a97b7adb', # BP EP 4 ACT 1
    ]

    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            if not x['uuid'] in ignor_contract:
                json[x['uuid']] = {
                    'uuid': x['uuid'],
                    'free': x['shipIt'],
                    'name': x['displayName'],
                    'icon': x['displayIcon'],
                    'reward': x['content']
                }
        data['contracts'] = json
        data_save('contracts', data)
    session.close()

def fetch_currencies():

    data = data_read('currencies')
    session = requests.session()
    print('Fetching currencies !')
    r = session.get(f'https://valorant-api.com/v1/currencies')
    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            json[x['uuid']] = {
                'uuid': x['uuid'],
                'name': x['displayName'],
                'icon': x['displayIcon']
            }
        data['currencies'] = json
        data_save('currencies', data)
    session.close()

def fetch_playercard():
    data = data_read('playercards')
    session = requests.session()
    print('Fetching Playercards !')
    r = session.get(f'https://valorant-api.com/v1/playercards')
    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            json[x['uuid']] = {
                'uuid': x['uuid'],
                'name': x['displayName'],
                'icon' : {
                    'small': x['smallArt'],
                    'wide': x['wideArt'],
                    'large': x['largeArt'],
                }
            }
        data['playercards'] = json
        data_save('playercards', data)
    session.close()

def fetch_playertitles():
    data = data_read('playertitles')
    session = requests.session()
    print('Fetching Player titles !')

    r = session.get(f'https://valorant-api.com/v1/playertitles')
    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            json[x['uuid']] = {
                'uuid': x['uuid'],
                'name': x['displayName'],
                'text': x['titleText']
            }
        data['titles'] = json
        data_save('playertitles', data)
    session.close()

def fetch_spray():
    data = data_read('sprays')
    session = requests.session()
    print('Fetching Sprays !')
    r = session.get(f'https://valorant-api.com/v1/sprays')
    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            json[x['uuid']] = {
                'uuid': x['uuid'],
                'name': x['displayName'],
                'icon': x['fullTransparentIcon'] or x['displayIcon']
            }
        data['sprays'] = json
        data_save('sprays', data)
    session.close()

def fetch_buddies():

    data = data_read('buddies')
    session = requests.session()

    print('Fetching buddies !')

    r = session.get(f'https://valorant-api.com/v1/buddies')
    if r.status_code == 200:
        json = {}
        json['version'] = data['gameversion']
        for x in r.json()['data']:
            buddy = x['levels'][0]
            json[buddy['uuid']] = {
                'uuid': buddy['uuid'],
                'name': x['displayName'],
                'icon': buddy['displayIcon']
            }
        data['buddies'] = json
        data_save('buddies', data)
    session.close()

def fetch_skin():
    data = data_read('skins')
    session = requests.session()

    print('Fetching weapons skin !')

    r = session.get('https://valorant-api.com/v1/weapons/skins')
    if r.status_code == 200:
        skins = {}
        skins['version'] = data['gameversion']
        for x in r.json()['data']:
            skinone = x['levels'][0]
            skins[skinone['uuid']] = {
                'uuid': skinone['uuid'],
                'name': x['displayName'],
                'icon': skinone['displayIcon'],
                'tier': x['contentTierUuid'],
            }
        data['skins'] = skins
        data_save('skins', data)
    session.close()

def fetch_tier():
    data = data_read('skins')
    session = requests.session()

    print('Fetching tier skin !')

    r = session.get('https://valorant-api.com/v1/contenttiers/')
    if r.status_code == 200:
        tiers = {}
        tiers['version'] = data['gameversion']
        for tier in r.json()['data']:
            tiers[tier['uuid']] = {
                'uuid': tier['uuid'],
                'name': tier['devName'],
                'icon': tier['displayIcon'],
            }
        data['tiers'] = tiers 
        data_save('skins', data)
    session.close()

def fetch_mission():
    data = data_read('missions')
    session = requests.session()
    print('Fetching mission !')
    r = session.get(f'https://valorant-api.com/v1/missions')
    json = {}
    json['version'] = get_valorant_version()
    if r.status_code == 200:
        for x in r.json()['data']:
            json[x['uuid']] = {
                'uuid': x['uuid'],
                'title': x['title'],
                'type': x['type'],
                'progress': x['progressToComplete'],
                'xp': x['xpGrant'],
            }
        data['missions'] = json
        data_save('missions', data)
    session.close()

# DATA SETUP

def pre_fetch_price():
    try:
        data = data_read('skins')
        pre_json = {'timestamp': None}
        data['prices'] = pre_json
        data_save('skins', data)
    except Exception as e:
        print(e)
        print("Can't fetch price")

def fetch_price(user_id=None, region=None, headers=None):
    data = data_read('skins')
    session = requests.session()

    print('Fetching price skin!')

    if region is not None and headers is not None:
        region = region
        headers = headers
    elif user_id is not None:
        database = data_read('users')
        headers = {
            'Authorization': "Bearer " + database[str(user_id)]['rso'],
            'X-Riot-Entitlements-JWT': database[str(user_id)]['emt']
            }
        region = database[str(user_id)]['region']

    r = session.get('https://pd.{region}.a.pvp.net/store/v1/offers/'.format(region=region), headers=headers, verify=False)
    if r.status_code == 200:
        fetch = r.json()
        prices = {}
        prices['version'] = data['gameversion']
        for x in fetch['Offers']:
            if x["OfferID"] in data['skins']:
                *cost, = x["Cost"].values()
                prices[x['OfferID']] = cost[0]
        prices['timestamp'] = int(datetime.timestamp(datetime.now()))
        data['prices'] = prices
        data_save('skins', data)
    session.close()
    
def data_folder():
    # create data folder
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'data')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    
def create_json(filename, formats):
    file_path = f"data/"+ filename +".json"
    file_dir = os.path.dirname(file_path)
    os.makedirs(file_dir, exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "w") as fp:
            json.dump(formats, fp, indent=2)

def create_all_file(bot):
    
    # create data folder
    data_folder()
    create_json('skins', {'formats': bot.format_version})
    create_json('missions', {'formats': bot.format_version})
    create_json('contracts', {'formats': bot.format_version})
    create_json('currencies', {'formats': bot.format_version})
    create_json('playercards', {'formats': bot.format_version})
    create_json('playertitles', {'formats': bot.format_version})
    create_json('sprays', {'formats': bot.format_version})
    create_json('buddies', {'formats': bot.format_version})

def update_cache(bot):
    # cache_update
    data = data_read('skins')
    data['formats'] = bot.format_version
    data['gameversion'] = bot.game_version
    data_save('skins', data)

    miss = data_read('missions')
    miss['formats'] = bot.format_version
    miss['gameversion'] = bot.game_version
    data_save('missions', miss)

    con = data_read('contracts')
    con['formats'] = bot.format_version
    con['gameversion'] = bot.game_version
    data_save('contracts', con)

    cur = data_read('currencies')
    cur['formats'] = bot.format_version
    cur['gameversion'] = bot.game_version
    data_save('currencies', cur)

    card = data_read('playercards')
    card['formats'] = bot.format_version
    card['gameversion'] = bot.game_version
    data_save('playercards', card)

    title = data_read('playertitles')
    title['formats'] = bot.format_version
    title['gameversion'] = bot.game_version
    data_save('playertitles', title)

    spray = data_read('sprays')
    spray['formats'] = bot.format_version
    spray['gameversion'] = bot.game_version
    data_save('sprays', spray)

    buddie = data_read('buddies')
    buddie['formats'] = bot.format_version
    buddie['gameversion'] = bot.game_version
    data_save('buddies', buddie)
    
    try:
        if data["skins"]["version"] != bot.game_version: fetch_skin()
        fetch_tier()
        if miss["missions"]["version"] != bot.game_version: fetch_mission()
        if con["contracts"]["version"] != bot.game_version: fetch_contracts()
    except KeyError:
        print('\n')
        fetch_contracts()
        fetch_currencies()
        fetch_playercard()
        fetch_playertitles()
        fetch_spray()
        fetch_buddies()
        fetch_skin()
        pre_fetch_price()
        fetch_tier()
        fetch_mission()
    finally:
        print("\nBOT is Ready !")