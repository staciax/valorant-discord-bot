import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Union, Any, List, Dict
import contextlib
from .useful import (
    iso_to_time,
    format_relative,
    get_skin_list,
    get_emoji_tier,
    get_mission_format,
    get_nightmarket,
    get_battlepass,
    calculate_level_xp,
    get_emoji_tier_by_bot,
    get_emoji_point_by_bot

)
from .resources import points
from .useful import json_read

class Embed(discord.Embed): # Custom Embed
    def __init__(self, description:str = None, color: Union[discord.Color, int] = 0xfd4554, **kwargs: Any) -> None:
        super().__init__(description=description, color=color, **kwargs)






# ---------- STORE EMBED ---------- #

def embed_design_giorgio(skin: Dict, bot: commands.Bot) -> discord.Embed:
    """EMBED DESIGN Giorgio"""

    uuid, name, price, icon = skin['uuid'], skin['name'], skin['price'], skin['icon']
    emoji = get_emoji_tier_by_bot(uuid, bot)

    vp_emoji = get_emoji_point_by_bot('ValorantPointIcon', bot)

    embed = Embed(f"{emoji} **{name}**\n{vp_emoji} {price}", color=0x0F1923)
    embed.set_thumbnail(url=icon)
    return embed

def embed_store(player: str, offer: Dict, language: str, response: Dict, bot: commands.Bot) -> List[discord.Embed]:
    """Embed Store"""

    msg_response = response.get('RESPONSE', 'Daily store for **{username}** | Remaining {duration}')

    data = get_skin_list(offer, language)

    duration = data['duration']

    description = msg_response.format(username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration)))
    
    embed = Embed(description)
    embeds = [embed]
    [embeds.append(embed_design_giorgio(data[skin], bot)) for skin in data if not skin == 'duration']

    return embeds

# ---------- MISSION EMBED ---------- #

def embed_mission(player:str, mission: Dict, language: str, response: Dict) -> discord.Embed:
    """Embed Mission"""

    # language
    mission_lang = response.get('TITLE', 'Mission')
    daily_lang = response.get('DAILY', 'Daily')
    weekly_lang = response.get('WEEKLY', 'Weekly')
    newplayer_lang = response.get('NEWPLAYER', 'New Player')
    no_mission_lang = response.get('NO_MISSION', 'No missions available')

    # mission format
    data = get_mission_format(mission, language)

    daily_format = data['daily']
    daily_end = data['daily_end']
    weekly_format = data['weekly']
    weekly_end = data['weekly_end']
    newplayer_format = data['newplayer']

    daily = ''.join(daily_format)
    weekly = ''.join(weekly_format)
    newplayer = ''.join(newplayer_format)

    weekly_end_time = ''
    with contextlib.suppress(Exception):
        weekly_end_time = f"Refills {format_relative(iso_to_time(weekly_end))}"

    embed = Embed(title=f"**{mission_lang}**")
    embed.set_footer(text=player)
    if len(daily) != 0:
        embed.add_field(
            name=f"**{daily_lang}**",
            value=f"{daily}\nEnd(s) at {format_relative(iso_to_time(daily_end))}",
            inline=False
        )
    if len(weekly) != 0:
        embed.add_field(
            name=f"**{weekly_lang}**",
            value=f"{weekly}\n\n{weekly_end_time}",
            inline=False
        )
    if len(newplayer) != 0:
        embed.add_field(
            name=f"**{newplayer_lang}**",
            value=f"{newplayer}",
            inline=False
        )
    if len(embed.fields) == 0:
        embed.description = no_mission_lang
    
    return embed

# ---------- POINT EMBED ---------- #

def embed_point(player:str, wallet: Dict, language: str, response: Dict, bot: commands.Bot) -> discord.Embed:
    """Embed Point"""

    # language
    title_point = response.get('POINT', 'Points')

    cache = json_read('cache')
    point = cache['currencies']

    vp_uuid = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
    rad_uuid = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'

    valorant_point = wallet['Balances'][vp_uuid]
    radiant_point = wallet['Balances'][rad_uuid]

    rad = point[rad_uuid]['names'][language]
    vp = point[vp_uuid]['names'][language]
    if vp == 'VP': vp = 'Valorant Points'

    embed = Embed(title=f"{title_point}:")

    vp_emoji = get_emoji_point_by_bot('ValorantPointIcon', bot)
    rad_emoji = get_emoji_point_by_bot('RadianitePointIcon', bot)

    embed.add_field(name=vp, value=f"{vp_emoji} {valorant_point}")
    embed.add_field(name=rad, value=f"{rad_emoji} {radiant_point}")
    embed.set_footer(text=player)

    return embed

# ---------- NIGHTMARKET EMBED ---------- #

def gen_embed_nmk(skins: Dict, bot: commands.Bot) -> discord.Embed:
    """Generate Embed Nightmarket"""
    
    uuid, name, icon, price, dpice = skins['uuid'], skins['name'], skins['icon'], skins['price'], skins['disprice']

    embed = Embed(f"{get_emoji_tier(uuid)} **{name}**\n{points['vp']} {dpice} ~~{price}~~", color=0x0F1923)
    embed.set_thumbnail(url=icon)
    return embed

def embed_nightmarket(player:str, offer: Dict, language: str, response: Dict) -> discord.Embed:
    """Embed Nightmarket"""

    # language
    msg_response = response.get('RESPONSE', 'NightMarket for **{username}** | Remaining {duration}')
    
    night_mk = get_nightmarket(offer, language, response)    
    skins = night_mk['nightmarket']
    duration = night_mk['duration']

    description = msg_response.format(username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration)))

    embed = Embed(description)

    embeds = [embed]
    [embeds.append(gen_embed_nmk(skins[skin])) for skin in skins]

    return embeds

# ---------- BATTLEPASS EMBED ---------- #

def embed_battlepass(player:str, data: Dict, season: Dict, language: str, response: Dict) -> discord.Embed:
    """Embed Battlepass"""

    # language
    MSG_RESPONSE = response.get('RESPONSE', '**Next Reward:** {next}\n**Type:** {type}\n**XP:** {xp}\n**ACT END:** {end}')
    MSG_TIER = response.get('TIER', 'TIER')

    BTP = get_battlepass(data, season, language, response)
    
    item = BTP['data']
    reward = item['reward']
    xp = item['xp']
    act = item['act']
    tier = item['tier']
    icon = item['icon']
    season_end = item['end']
    item_type = item['type']
    original_type = item['original_type']

    description = MSG_RESPONSE.format(next=f'`{reward}`', type=f'`{item_type}`', xp=f'`{xp:,}/{calculate_level_xp(tier + 1):,}`', end=format_relative(season_end))

    embed =  Embed(description, title=f"BATTLEPASS")
    
    if icon:
        if original_type in ['PlayerCard', 'EquippableSkinLevel']:
            embed.set_image(url=icon)
        else:
            embed.set_thumbnail(url=icon)
    
    if tier >= 50:
        embed.color = 0xf1b82d

    if tier == 55:
        embed.description = f'{reward}'

    embed.set_footer(text=f"{MSG_TIER} {tier} | {act}\n{player}")

    return embed

# ---------- NOTIFY EMBED ---------- #

def notify_specified_send(uuid: str) -> discord.Embed:
    ...

def notify_all_send(player:str, offer: Dict, language:str, response: Dict, bot: commands.Bot) -> discord.Embed:
    description_format = response.get('RESPONSE_ALL', 'Daily store for **{username}** | Remaining {duration}')

    data = get_skin_list(offer, language)

    duration = data['duration']

    description = description_format.format(username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration)))
    embed = Embed(description)
    embeds = [embed]
    [embeds.append(embed_design_giorgio(data[skin], bot)) for skin in data if not skin == 'duration']
    
    return embeds