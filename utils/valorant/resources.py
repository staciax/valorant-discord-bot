import discord
import requests
from io import BytesIO
from discord.ext import commands
from .local import LocalErrorResponse

# ---------- URL AND REGION FORMAT ---------- # https://github.com/colinhartigan/

base_endpoint = "https://pd.{shard}.a.pvp.net"
base_endpoint_glz = "https://glz-{region}-1.{shard}.a.pvp.net"
base_endpoint_shared = "https://shared.{shard}.a.pvp.net"

regions: list = ["na","eu","latam","br","ap","kr","pbe"]
region_shard_override = {
    "latam":"na",
    "br":"na",
}
shard_region_override = {
    "pbe": "na"
}

# ---------- EMOJI ---------- #

# local emoji id

emoji_icon_assests = {
    'DeluxeTier': 'https://media.valorant-api.com/contenttiers/0cebb8be-46d7-c12a-d306-e9907bfc5a25/displayicon.png',
    'ExclusiveTier': 'https://media.valorant-api.com/contenttiers/e046854e-406c-37f4-6607-19a9ba8426fc/displayicon.png',
    'PremiumTier': 'https://media.valorant-api.com/contenttiers/60bca009-4182-7998-dee7-b8a2558dc369/displayicon.png',
    'SelectTier': 'https://media.valorant-api.com/contenttiers/12683d76-48d7-84a3-4e09-6985794f0445/displayicon.png',
    'UltraTier': 'https://media.valorant-api.com/contenttiers/411e4a55-4e59-7757-41f0-86a53f101bb5/displayicon.png',
    'ValorantPointIcon': 'https://media.valorant-api.com/currencies/85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/largeicon.png',
    'RadianitePointIcon': 'https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png'
}

tiers = {
    '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {'name':'Deluxe', 'emoji':'<:Deluxe:950372823048814632>', 'color': 0x009587},
    'e046854e-406c-37f4-6607-19a9ba8426fc': {'name':'Exclusive', 'emoji':'<:Exclusive:950372911036915762>', 'color': 0xf1b82d},
    '60bca009-4182-7998-dee7-b8a2558dc369': {'name':'Premium', 'emoji':'<:Premium:950376774620049489>', 'color': 0xd1548d},
    '12683d76-48d7-84a3-4e09-6985794f0445': {'name':'Select', 'emoji':'<:Select:950376833982021662>', 'color': 0x5a9fe2},
    '411e4a55-4e59-7757-41f0-86a53f101bb5': {'name':'Ultra', 'emoji':'<:Ultra:950376896745586719>', 'color': 0xefeb65}
}

points = {
    'ValorantPoint':f'<:ValorantPoint:950365917613817856>',
    'RadianitePoint':f'<:RadianitePoint:950365909636235324>'
}

def get_item_type(uuid: str):
    """Get item type"""
    item_type = {
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': 'Agents',
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': 'Contracts',
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': 'Sprays',
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': 'Gun Buddies',
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': 'Player Cards',
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': 'Skins',
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': 'Skins chroma',
        'de7caa6b-adf7-4588-bbd1-143831e786c6': 'Player titles'
    }
    return item_type.get(uuid, None)

def __url_to_image(url):
    session = requests.session()

    r = session.get(url)
    image = BytesIO(r.content)
    image_value = image.getvalue()
    if r.status_code in range(200, 299):
        return image_value

async def setup_emoji(bot: commands.Bot, guild: discord.Guild, local_code: str, force=False):

    response = LocalErrorResponse('SETUP_EMOJI', local_code)

    """Setup emoji"""
    for find_emoji in emoji_icon_assests.items():
        name = find_emoji[0]
        emoji_url = find_emoji[1]
        emoji = discord.utils.get(bot.emojis, name=name)
        if not emoji:
            try:
                emoji = await guild.create_custom_emoji(name=name, image=__url_to_image(emoji_url))
            except discord.Forbidden:
                if force:
                    raise RuntimeError(response.get('MISSING_PERM'))
                continue
            except discord.HTTPException:
                print(response.get('FAILED_CREATE_EMOJI'))
                pass
                # raise RuntimeError(f'Failed to create emoji !')