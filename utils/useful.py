# Standard
import base64
import discord
import json
import re
from contextlib import suppress
from datetime import timezone 

# Third
import requests

# Local
from utils.json_loader import data_read, data_save

# USEFUL

def _decode_token(token:str) -> dict: # decode_token by ok_#4443
    data = base64.b64decode(token.split(".")[1] + "==").decode()
    return json.loads(data)

def _token_exp(token:str) -> str:
    data = _decode_token(token)
    return data['exp']

def format_dt(dt, style=None): #style 'R' or 'd'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'

def _extract_tokens(data):
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response

def extract_tokens_from_url(URL):
    try:
        accessToken = URL.split("access_token=")[1].split("&scope")[0]
        return accessToken
    except IndexError:
        raise RuntimeError('An unknown error occurred, plz /login again')

def remove_user(user_id):
    try:
        data = data_read('users')
        del data[str(user_id)]
        data_save('users', data)
    except Exception as e:
        print(e)
        print(f"I can't remove data user : {user_id}")

# GET DATA

def get_skin_name(uuid):
    '''Get Skin name'''
    data = data_read('skins')
    name = None
    with suppress(Exception):
        name = data["skins"][uuid]['name']     
    return name

def get_skin_icon(uuid) -> str:
    '''Get Skin name'''
    data = data_read('skins')
    icon = None
    with suppress(Exception):
        icon = data["skins"][uuid]['icon']     
    return icon

def get_skin_price(uuid) -> str:
    '''Get Skin price by skin uuid'''
    data = data_read('skins')
    cost = '-'
    with suppress(Exception):
        cost = data["prices"][uuid]
    return cost

# PVP ENDPOINT

def get_valorant_point(user_id):
    session = requests.session()
    data = data_read('users')

    rso = data[user_id]['rso']
    emt = data[user_id]['emt']

    headers = {
        'Authorization': f"Bearer {rso}",
        'X-Riot-Entitlements-JWT':  emt
    }
    r = session.get(
        'https://pd.{region}.a.pvp.net/store/v1/wallet/{puuid}'.format(
            region=data[user_id]['region'],puuid=data[user_id]['puuid']
        ),
        headers=headers
    )
    if r.status_code == 200:
        balances = r.json()["Balances"]
        return balances