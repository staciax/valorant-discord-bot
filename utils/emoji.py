import discord
import requests
from io import BytesIO
from utils.json_loader import data_read

def get_emoji_tier(skin_uuid) -> discord.Emoji:
    data = data_read('skins')
    uuid = data['skins'][skin_uuid]['tier']
    uuid = data['tiers'][uuid]['uuid']
    emoji = tiers[uuid]['emoji']
    return emoji

tiers = {
    '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {'name':'Deluxe', 'emoji':'<:Deluxe:950372823048814632>', 'color': 0x009587},
    'e046854e-406c-37f4-6607-19a9ba8426fc': {'name':'Exclusive', 'emoji':'<:Exclusive:950372911036915762>', 'color': 0xf1b82d},
    '60bca009-4182-7998-dee7-b8a2558dc369': {'name':'Premium', 'emoji':'<:Premium:950376774620049489>', 'color': 0xd1548d},
    '12683d76-48d7-84a3-4e09-6985794f0445': {'name':'Select', 'emoji':'<:Select:950376833982021662>', 'color': 0x5a9fe2},
    '411e4a55-4e59-7757-41f0-86a53f101bb5': {'name':'Ultra', 'emoji':'<:Ultra:950376896745586719>', 'color': 0xefeb65}
}

points = {
    'vp':'<:ValorantPoint:950365917613817856>',
    'rad':'<:RadianitePoint:950365909636235324>'
}

# SETUP EMOJI FOR NOTIFY

def get_notify_emoji(skin_uuid, bot):
    data = data_read('skins')
    uuid = data['skins'][skin_uuid]['tier']
    tier_uuid = {
        '0cebb8be-46d7-c12a-d306-e9907bfc5a25': discord.utils.get(bot.emojis, name='Deluxe_'),
        'e046854e-406c-37f4-6607-19a9ba8426fc': discord.utils.get(bot.emojis, name='Exclusive_'),
        '60bca009-4182-7998-dee7-b8a2558dc369': discord.utils.get(bot.emojis, name='Premium_'),
        '12683d76-48d7-84a3-4e09-6985794f0445': discord.utils.get(bot.emojis, name='Select_'),
        '411e4a55-4e59-7757-41f0-86a53f101bb5': discord.utils.get(bot.emojis, name='Ultra_'),
    }
    return tier_uuid[uuid]

def url_to_image(url):
    session = requests.session()

    r = session.get(url)
    image = BytesIO(r.content)
    image_value = image.getvalue()
    if r.status_code in range(200, 299):
        return image_value

async def setup_emoji(ctx):
    data:dict = data_read('skins')
    data['tiers'].pop('version')
    
    guild = ctx.guild

    Emoji_list = ['Deluxe','Exclusive','Premium','Select','Ultra']
    Emoji_none = []
    
    for emoji in Emoji_list:
        name = emoji
        emote = discord.utils.get(ctx.bot.emojis, name=name + '_') or discord.utils.get(ctx.guild.emojis, name=name + '_')
        if emote is None:
            Emoji_none.append(emoji)

    try:
        for x in data['tiers']:
            if data['tiers'][x]['name'] in Emoji_none:
                image = url_to_image(data['tiers'][x]['icon'])
                await guild.create_custom_emoji(image=image, name=data['tiers'][x]['name'] + '_')

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
        raise RuntimeError("Can't create emoji. or Your server emoji slot is full")