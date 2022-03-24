import discord
from utils.useful import format_dt
from utils.emoji import get_emoji_tier, points as points_emoji, get_notify_emoji
from utils.useful import get_skin_icon
from datetime import datetime, timezone, timedelta

# EMBED 

def pillow_embed(name, user, duration) -> discord.Embed:
    embed = discord.Embed(description=f"**Daily Store for {name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=duration)), 'R')}",color=0xfd4554)
    embed.set_image(url='attachment://store-offers.png')        
    embed.set_footer(text=f'Requested by {user.display_name}')
    if user.display_avatar is not None:
        embed.set_footer(text=f'Requested by {user.display_name}', icon_url=user.display_avatar)
    return embed

def embed_design_giorgio(skin) -> discord.Embed:

    uuid= skin['uuid']
    name= skin['name']
    price= skin['price']
    icon= skin['icon']

    embed = discord.Embed(color=0x0F1923)
    embed.title = f"{get_emoji_tier(uuid)} {name}"
    embed.description = f"{points_emoji['vp']} {price}"
    embed.set_thumbnail(url=icon)
    return embed

def embed_giorgio_notify(uuid, name, price, icon, bot) -> discord.Embed:
    embed = discord.Embed(color=0x0F1923)
    embed.title = f"{get_notify_emoji(uuid, bot)} {name}"
    embed.description = f"{points_emoji['vp']} {price}"
    embed.set_thumbnail(url=icon)
    return embed

def notify_send(emoji, name, duration, icon) -> discord.Embed:
    embed = discord.Embed(color=0xfd4554)
    embed.description = f"{emoji} **{name}** is in your daily store!\nRemaining {duration}"
    embed.set_thumbnail(url=icon)
    return embed

def night_embed(uuid, name, price, dpice):
    embed = discord.Embed(color=0x0F1923)
    embed.description = f"{get_emoji_tier(uuid)} **{name}**\n{points_emoji['vp']} {dpice} ~~{price}~~"
    embed.set_thumbnail(url=get_skin_icon(uuid))
    return embed