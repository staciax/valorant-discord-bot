# Standard
import base64
import discord
import json
import os
import re
from io import BytesIO
from contextlib import suppress
from datetime import datetime, timezone, timedelta

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

def get_tier_emoji(skin_uuid, bot):
    data = data_read('skins')
    uuid = data['skins'][skin_uuid]['tier']
    tier_uuid = {
        '0cebb8be-46d7-c12a-d306-e9907bfc5a25': discord.utils.get(bot.emojis, name='DeluxeTier'),
        'e046854e-406c-37f4-6607-19a9ba8426fc': discord.utils.get(bot.emojis, name='ExclusiveTier'),
        '60bca009-4182-7998-dee7-b8a2558dc369': discord.utils.get(bot.emojis, name='PremiumTier'),
        '12683d76-48d7-84a3-4e09-6985794f0445': discord.utils.get(bot.emojis, name='SelectTier'),
        '411e4a55-4e59-7757-41f0-86a53f101bb5': discord.utils.get(bot.emojis, name='UltraTier'),
    }
    return tier_uuid[uuid]

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
        
# HENRIK ENDPOINT

def get_player_mmr(region, name, tag) -> dict:
    session = requests.session()
    r = session.get('https://api.henrikdev.xyz/valorant/v1/mmr-history/{}/{}/{}'.format(region, name, tag))
    if r.status_code != 200:
        return None
    return r.json()

def get_name_tagline(region, puuid) -> str:
    session = requests.session()
    data = None
    r = session.get('https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/{}/{}'.format(region, puuid))
    if r.status_code == 200:
        riot_name = r.json()['data']['name']
        riot_tagline = r.json()['data']['tag']
        data = '{}#{}'.format(riot_name, riot_tagline)
    return data

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

# EMOJI SETUP

def url_to_image(url):
    session = requests.session()

    r = session.get(url)
    image = BytesIO(r.content)
    image_value = image.getvalue()
    if r.status_code in range(200, 299):
        return image_value

async def get_emoji_point(ctx, point):
    
    emoji = '\u200b' # if guild can't create emoji
    
    if point == 'vp':
        name = 'ValorantPoint'
        emoji = discord.utils.get(ctx.bot.emojis, name=name) or discord.utils.get(ctx.guild.emojis, name=name)
        if emoji is None:
            try:
                url = 'https://media.valorant-api.com/currencies/85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/displayicon.png'
                image = url_to_image(url)
                emoji = await ctx.guild.create_custom_emoji(image=image, name=name)
            except Exception as e:
                print(e)

    elif point == 'rad':
        name = 'RadianitePoint'
        emoji = discord.utils.get(ctx.bot.emojis, name=name) or discord.utils.get(ctx.guild.emojis, name=name)
        if emoji is None:
            try:
                url = 'https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png'
                image = url_to_image(url)
                emoji = await ctx.guild.create_custom_emoji(image=image, name=name)
            except Exception as e:
                print(e)

    return emoji

async def get_emoji_tier(ctx, skin_uuid):

    emoji = '\u200b' # if guild can't create emoji

    data = data_read('skins')
    uuid = data['skins'][skin_uuid]['tier']
    name = data['tiers'][uuid]['name']

    emoji = discord.utils.get(ctx.bot.emojis, name=name + 'Tier') or discord.utils.get(ctx.guild.emojis, name=name + 'Tier')
    if emoji is None:
        try:
            icon = data['tiers'][uuid]['icon']
            image = url_to_image(icon)
            emoji = await ctx.guild.create_custom_emoji(image=image, name=name + 'Tier')
        except Exception as e:
            print(e)
    return emoji

def get_emoji_point_bot(bot, point):
    emoji = '\u200b' # if guild can't create emoji
    if point == 'vp':
        name = 'ValorantPoint'
        emoji = discord.utils.get(bot.emojis, name=name)
    elif point == 'rad':
        name = 'RadianitePoint'
        emoji = discord.utils.get(bot.emojis, name=name)
    return emoji

def get_emoji_tier_bot(bot, skin_uuid):
    emoji = '\u200b' # if guild can't create emoji
    data = data_read('skins')
    uuid = data['skins'][skin_uuid]['tier']
    name = data['tiers'][uuid]['name']
    emoji = discord.utils.get(bot.emojis, name=name + 'Tier')
    return emoji
    
async def setup_emoji(ctx):
    data:dict = data_read('skins')
    data['tiers'].pop('version')
    
    guild = ctx.guild

    Emoji_list = ['Deluxe','Exclusive','Premium','Select','Ultra']
    Emoji_none = []
    
    for emoji in Emoji_list:
        name = emoji + 'Tier'
        emote = discord.utils.get(ctx.bot.emojis, name=name) or discord.utils.get(ctx.guild.emojis, name=name)
        if emote is None:
            Emoji_none.append(emoji)

    try:
        for x in data['tiers']:
            if data['tiers'][x]['name'] in Emoji_none:
                image = url_to_image(data['tiers'][x]['icon'])
                await guild.create_custom_emoji(image=image, name=data['tiers'][x]['name'] + 'Tier')

        radianite_emoji = discord.utils.get(ctx.bot.emojis, name='RadianitePoint') or discord.utils.get(ctx.guild.emojis, name='RadianitePoint')
        if radianite_emoji is None:
            radianite = url_to_image('https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png')
            await guild.create_custom_emoji(image=radianite, name='RadianitePoint')
        
        vlr_point_emoji = discord.utils.get(ctx.bot.emojis, name='ValorantPoint') or discord.utils.get(ctx.guild.emojis, name='ValorantPoint')
        if vlr_point_emoji is None:
            vlrpoint = url_to_image('https://media.valorant-api.com/currencies/85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/displayicon.png')
            await guild.create_custom_emoji(image=vlrpoint, name='ValorantPoint')
            
    except discord.Forbidden:
        raise RuntimeError("Bot don't have perm create emojis.")
    except discord.HTTPException:
        raise RuntimeError('An error occurred creating an emoji.')


# EMBED 

def pillow_embed(name, user, duration) -> discord.Embed:
    embed = discord.Embed(description=f"**Daily Store for {name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')}",color=0xfd4554)
    embed.set_image(url='attachment://store-offers.png')        
    embed.set_footer(text=f'Requested by {user.display_name}')
    if user.display_avatar is not None:
        embed.set_footer(text=f'Requested by {user.display_name}', icon_url=user.display_avatar)
    return embed

async def embed_design_giorgio(ctx, uuid, name, price, icon) -> discord.Embed:
    embed = discord.Embed(color=0x0F1923)
    embed.title = f"{await get_emoji_tier(ctx, uuid)} {name}"
    embed.description = f"{await get_emoji_point(ctx, 'vp')} {price}"
    embed.set_thumbnail(url=icon)
    return embed

def embed_giorgio_notify(bot, uuid, name, price, icon) -> discord.Embed:
    embed = discord.Embed(color=0x0F1923)
    embed.title = f"{get_emoji_tier_bot(bot, uuid)} {name}"
    embed.description = f"{get_emoji_point_bot(bot, 'vp')} {price}"
    embed.set_thumbnail(url=icon)
    return embed

def notify_send(emoji, name, duration, icon) -> discord.Embed:
    embed = discord.Embed(color=0xfd4554)
    embed.description = f"{emoji} **{name}** is in your daily store!\nRemaining {duration}"
    embed.set_thumbnail(url=icon)
    return embed
