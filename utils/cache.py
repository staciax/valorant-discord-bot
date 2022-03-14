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
    # json['version'] = get_valorant_version()

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
