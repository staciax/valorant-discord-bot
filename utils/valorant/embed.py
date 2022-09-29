from __future__ import annotations

import contextlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Union

import discord

from ..locale_v2 import ValorantTranslator
from .useful import JSON, GetEmoji, GetFormat, calculate_level_xp, format_relative, iso_to_time

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot


class Embed(discord.Embed):  # Custom Embed
    def __init__(self, description: str = None, color: Union[discord.Color, int] = 0xFD4554, **kwargs: Any) -> None:
        super().__init__(description=description, color=color, **kwargs)


class GetEmbed:
    def __giorgio_embed(skin: Dict, bot: ValorantBot) -> discord.Embed:
        """EMBED DESIGN Giorgio"""

        uuid, name, price, icon = skin['uuid'], skin['name'], skin['price'], skin['icon']
        emoji = GetEmoji.tier_by_bot(uuid, bot)

        vp_emoji = GetEmoji.point_by_bot('ValorantPointIcon', bot)

        embed = Embed(f"{emoji} **{name}**\n{vp_emoji} {price}", color=0x0F1923)
        embed.set_thumbnail(url=icon)
        return embed

    @classmethod
    def store(cls, player: str, offer: Dict, response: Dict, bot: ValorantBot) -> List[discord.Embed]:
        """Embed Store"""

        store_esponse = response.get('RESPONSE')

        data = GetFormat.offer_format(offer)

        duration = data.pop('duration')

        description = store_esponse.format(
            username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration))
        )

        embed = Embed(description)
        embeds = [embed]
        [embeds.append(cls.__giorgio_embed(data[skin], bot)) for skin in data]

        return embeds

    # ---------- MISSION EMBED ---------- #

    def mission(player: str, mission: Dict, response: Dict) -> discord.Embed:
        """Embed Mission"""

        # language
        title_mission = response.get('TITLE')
        title_daily = response.get('DAILY')
        title_weekly = response.get('WEEKLY')
        title_new_player = response.get('NEWPLAYER')
        clear_all_mission = response.get('NO_MISSION')
        reset_in = response.get('DAILY_RESET')
        refill_in = response.get('REFILLS')

        # mission format
        data = GetFormat.mission_format(mission)

        daily_format = data['daily']
        daily_end = data['daily_end']
        weekly_format = data['weekly']
        weekly_end = data['weekly_end']
        new_player_format = data['newplayer']

        daily = ''.join(daily_format)
        weekly = ''.join(weekly_format)
        new_player = ''.join(new_player_format)

        weekly_end_time = ''
        with contextlib.suppress(Exception):
            weekly_end_time = f"{refill_in.format(duration=format_relative(iso_to_time(weekly_end)))}"

        embed = Embed(title=f"**{title_mission}**")
        embed.set_footer(text=player)
        if len(daily) != 0:
            embed.add_field(
                name=f"**{title_daily}**",
                value=f"{daily}\n{reset_in.format(duration=format_relative(iso_to_time(daily_end)))}",
                inline=False,
            )
        if len(weekly) != 0:
            embed.add_field(name=f"**{title_weekly}**", value=f"{weekly}\n\n{weekly_end_time}", inline=False)
        if len(new_player) != 0:
            embed.add_field(name=f"**{title_new_player}**", value=f"{new_player}", inline=False)
        if len(embed.fields) == 0:
            embed.color = 0x77DD77
            embed.description = clear_all_mission

        return embed

    # ---------- POINT EMBED ---------- #

    def point(player: str, wallet: Dict, response: Dict, bot: ValorantBot) -> discord.Embed:
        """Embed Point"""

        # language
        title_point = response.get('POINT')

        cache = JSON.read('cache')
        point = cache['currencies']

        vp_uuid = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
        rad_uuid = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'

        valorant_point = wallet['Balances'][vp_uuid]
        radiant_point = wallet['Balances'][rad_uuid]

        rad = point[rad_uuid]['names'][str(VLR_locale)]
        vp = point[vp_uuid]['names'][str(VLR_locale)]
        if vp == 'VP':
            vp = 'Valorant Points'

        embed = Embed(title=f"{title_point}:")

        vp_emoji = GetEmoji.point_by_bot('ValorantPointIcon', bot)
        rad_emoji = GetEmoji.point_by_bot('RadianitePointIcon', bot)

        embed.add_field(name=vp, value=f"{vp_emoji} {valorant_point}")
        embed.add_field(name=rad, value=f"{rad_emoji} {radiant_point}")
        embed.set_footer(text=player)

        return embed

    # ---------- NIGHT MARKET EMBED ---------- #

    def __nightmarket_embed(skins: Dict, bot: ValorantBot) -> discord.Embed:
        """Generate Embed Night Market"""

        uuid, name, icon, price, dpice = skins['uuid'], skins['name'], skins['icon'], skins['price'], skins['disprice']

        emoji = GetEmoji.tier_by_bot(uuid, bot)
        vp_emoji = GetEmoji.point_by_bot('ValorantPointIcon', bot)

        embed = Embed(f"{emoji} **{name}**\n{vp_emoji} {dpice} ~~{price}~~", color=0x0F1923)
        embed.set_thumbnail(url=icon)
        return embed

    @classmethod
    def nightmarket(cls, player: str, offer: Dict, bot: ValorantBot, response: Dict) -> discord.Embed:
        """Embed Night Market"""

        # language
        msg_response = response.get('RESPONSE')

        night_mk = GetFormat.nightmarket_format(offer, response)
        skins = night_mk['nightmarket']
        duration = night_mk['duration']

        description = msg_response.format(
            username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration))
        )

        embed = Embed(description)

        embeds = [embed]
        [embeds.append(cls.__nightmarket_embed(skins[skin], bot)) for skin in skins]

        return embeds

    # ---------- BATTLEPASS EMBED ---------- #

    def battlepass(player: str, data: Dict, season: Dict, response: Dict) -> discord.Embed:
        """Embed Battle-pass"""

        # language
        MSG_RESPONSE = response.get('RESPONSE')
        MSG_TIER = response.get('TIER')

        BTP = GetFormat.battlepass_format(data, season, response)

        item = BTP['data']
        reward = item['reward']
        xp = item['xp']
        act = item['act']
        tier = item['tier']
        icon = item['icon']
        season_end = item['end']
        item_type = item['type']
        original_type = item['original_type']

        description = MSG_RESPONSE.format(
            next=f'`{reward}`',
            type=f'`{item_type}`',
            xp=f'`{xp:,}/{calculate_level_xp(tier + 1):,}`',
            end=format_relative(season_end),
        )

        embed = Embed(description, title=f"BATTLEPASS")

        if icon:
            if original_type in ['PlayerCard', 'EquippableSkinLevel']:
                embed.set_image(url=icon)
            else:
                embed.set_thumbnail(url=icon)

        if tier >= 50:
            embed.color = 0xF1B82D

        if tier == 55:
            embed.description = str(reward)

        embed.set_footer(text=f"{MSG_TIER} {tier} | {act}\n{player}")

        return embed

    # ---------- NOTIFY EMBED ---------- #

    def notify_specified_send(uuid: str) -> discord.Embed:
        ...

    @classmethod
    def notify_all_send(cls, player: str, offer: Dict, response: Dict, bot: ValorantBot) -> discord.Embed:

        description_format = response.get('RESPONSE_ALL')

        data = GetFormat.offer_format(offer)

        duration = data.pop('duration')

        description = description_format.format(
            username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration))
        )
        embed = Embed(description)
        embeds = [embed]
        [embeds.append(cls.__giorgio_embed(data[skin], bot)) for skin in data]

        return embeds
