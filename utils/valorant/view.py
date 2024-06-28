from __future__ import annotations

import contextlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

# Standard
import discord
from discord import ButtonStyle, Interaction, TextStyle, ui

from ..errors import ValorantBotError
from ..locale_v2 import ValorantTranslator
from .resources import get_item_type

# Local
from .useful import JSON, GetEmoji, GetItems, format_relative

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot

    from .db import DATABASE


class share_button(ui.View):
    def __init__(self, interaction: Interaction, embeds: list[discord.Embed]) -> None:
        self.interaction: Interaction = interaction
        self.embeds = embeds
        super().__init__(timeout=300)

    async def on_timeout(self) -> None:
        """Called when the view times out"""
        await self.interaction.edit_original_response(view=None)

    @ui.button(label='Share to friends', style=ButtonStyle.primary)
    async def button_callback(self, interaction: Interaction, button: ui.Button):
        await interaction.channel.send(embeds=self.embeds)  # type: ignore
        await self.interaction.edit_original_response(content='\u200b', embed=None, view=None)


class NotifyView(discord.ui.View):
    def __init__(self, user_id: int, uuid: str, name: str, response: dict) -> None:
        self.user_id = user_id
        self.uuid = uuid
        self.name = name
        self.response = response
        super().__init__(timeout=600)
        self.remove_notify.label = response.get('REMOVE_NOTIFY')

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == int(self.user_id):
            return True
        await interaction.response.send_message(
            'This pagination menu cannot be controlled by you, sorry!', ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        """Called when the view times out"""

        with contextlib.suppress(Exception):
            self.remve_notify.disabled = True  # type: ignore
            await self.message.edit_original_response(view=self)  # type: ignore

    @discord.ui.button(label='Remove Notify', emoji='✖️', style=ButtonStyle.red)
    async def remove_notify(self, interaction: Interaction, button: ui.Button):
        data = JSON.read('notifys')

        for i in range(len(data)):
            if data[i]['uuid'] == self.uuid and data[i]['id'] == str(self.user_id):  # type: ignore
                data.pop(i)  # type: ignore
                break

        JSON.save('notifys', data)

        self.remove_notify.disabled = True
        await interaction.response.edit_message(view=self)

        removed_notify = self.response.get('REMOVED_NOTIFY')
        await interaction.followup.send(removed_notify.format(skin=self.name), ephemeral=True)  # type: ignore


class _NotifyListButton(ui.Button):
    def __init__(self, label: str, custom_id: str) -> None:
        super().__init__(label=label, style=ButtonStyle.red, custom_id=str(custom_id))

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        data: dict[str, Any] = JSON.read('notifys')
        for i in range(len(data)):
            if data[i]['uuid'] == self.custom_id and data[i]['id'] == str(self.view.interaction.user.id):  # type: ignore
                data.pop(i)  # type: ignore
                break

        JSON.save('notifys', data)

        del self.view.skin_source[self.custom_id]  # type: ignore
        self.view.update_button()  # type: ignore
        embed = self.view.main_embed()  # type: ignore
        await self.view.interaction.edit_original_response(embed=embed, view=self.view)  # type: ignore


class NotifyViewList(ui.View):
    skin_source: dict

    def __init__(self, interaction: Interaction[ValorantBot], response: dict[str, Any]) -> None:
        self.interaction: Interaction = interaction
        self.response = response
        self.bot: ValorantBot = interaction.client
        self.default_language = 'en-US'
        super().__init__(timeout=600)

    async def on_timeout(self) -> None:
        """Called when the view times out."""
        embed = discord.Embed(color=0x2F3136, description='🕙 Timeout')
        await self.interaction.edit_original_response(embed=embed, view=None)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message(
            'This pagination menu cannot be controlled by you, sorry!', ephemeral=True
        )
        return False

    def update_button(self) -> None:
        self.clear_items()
        self.create_button()

    def create_button(self) -> None:
        data = self.skin_source
        for index, skin in enumerate(data, start=1):
            self.add_item(_NotifyListButton(label=str(index), custom_id=skin))

    def get_data(self) -> None:
        """Gets the data from the cache."""

        database = JSON.read('notifys')
        notify_skin = [x['uuid'] for x in database if x['id'] == str(self.interaction.user.id)]  # type: ignore
        skin_source = {}

        for uuid in notify_skin:
            skin = GetItems.get_skin(uuid)
            name = skin['names'][str(VLR_locale)]
            icon = skin['icon']

            skin_source[uuid] = {
                'name': name,
                'icon': icon,
                'price': GetItems.get_skin_price(uuid),
                'emoji': GetEmoji.tier_by_bot(uuid, self.bot),
            }
        self.skin_source = skin_source

    def main_embed(self) -> discord.Embed:
        """Main embed for the view"""

        skin_list = self.skin_source
        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')

        title = self.response.get('TITLE')
        embed = discord.Embed(description='\u200b', title=title, color=0xFD4554)

        click_for_remove = self.response.get('REMOVE_NOTIFY')

        if len(skin_list) == 0:
            description = self.response.get('DONT_HAVE_NOTIFY')
            embed.description = description
        else:
            embed.set_footer(text=click_for_remove)
            count = 0
            text_format = []
            for count, skin in enumerate(skin_list):
                name = skin_list[skin]['name']
                icon = skin_list[skin]['icon']
                price = skin_list[skin]['price']
                emoji = skin_list[skin]['emoji']
                text_format.append(f'**{count + 1}.** {emoji} **{name}**\n{vp_emoji} {price}')
            else:
                embed.description = '\n'.join(text_format)
                if len(skin_list) == 1:
                    embed.set_thumbnail(url=icon)

        return embed

    async def start(self) -> None:
        """Starts the view."""
        self.get_data()
        self.create_button()
        embed = self.main_embed()
        await self.interaction.followup.send(embed=embed, view=self)


class TwoFA_UI(ui.Modal, title='Two-factor authentication'):
    """Modal for riot login with multifactorial authentication"""

    def __init__(
        self,
        interaction: Interaction,
        db: DATABASE,
        cookie: dict[str, Any],
        message: str,
        label: str,
        response: dict[str, Any],
    ) -> None:
        super().__init__(timeout=600)
        self.interaction: Interaction = interaction
        self.db = db
        self.cookie = cookie
        self.response = response
        self.two2fa.placeholder = message
        self.two2fa.label = label

    two2fa = ui.TextInput(label='Input 2FA Code', max_length=6, style=TextStyle.short)

    async def on_submit(self, interaction: Interaction) -> None:
        """Called when the user submits the modal."""

        code = self.two2fa.value
        if code:
            cookie = self.cookie
            user_id = self.interaction.user.id
            auth = self.db.auth
            auth.locale_code = self.interaction.locale  # type: ignore

            async def send_embed(content: str) -> None:
                embed = discord.Embed(description=content, color=0xFD4554)
                if interaction.response.is_done():
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            if not code.isdigit():
                return await send_embed(f'`{code}` is not a number')

            auth = await auth.give2facode(code, cookie)

            if auth['auth'] == 'response':
                login = await self.db.login(user_id, auth, self.interaction.locale)  # type: ignore
                if login['auth']:  # type: ignore
                    return await send_embed(f"{self.response.get('SUCCESS')} **{login['player']}!**")  # type: ignore

                return await send_embed(login['error'])  # type: ignore

            elif auth['auth'] == 'failed':
                return await send_embed(auth['error'])

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        """Called when the user submits the modal with an error."""
        print('TwoFA_UI:', error)
        embed = discord.Embed(description='Oops! Something went wrong.', color=0xFD4554)
        await interaction.response.send_message(embed=embed, ephemeral=True)


# inspired by https://github.com/giorgi-o
class BaseBundle(ui.View):
    def __init__(
        self, interaction: Interaction[ValorantBot], entries: dict[str, Any], response: dict[str, Any]
    ) -> None:
        self.interaction: Interaction = interaction
        self.entries = entries
        self.response = response
        self.language = str(VLR_locale)
        self.bot: ValorantBot = interaction.client
        self.current_page: int = 0
        self.embeds: list[list[discord.Embed]] = []
        self.page_format = {}
        super().__init__()
        self.clear_items()

    def fill_items(self, force: bool = False) -> None:
        self.clear_items()
        if len(self.embeds) > 1 or force:
            self.add_item(self.back_button)
            self.add_item(self.next_button)

    def base_embed(self, title: str, description: str, icon: str|None, color: int = 0x0F1923) -> discord.Embed:
        """Base embed for the view"""

        embed = discord.Embed(title=title, description=description, color=color)
        if icon:
            embed.set_thumbnail(url=icon)
        return embed

    def build_embeds(self, selected_bundle: int = 1) -> None:
        """Builds the bundle embeds"""

        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')

        embeds_list = []
        embeds = []

        collection_title = self.response.get('TITLE')

        for index, bundle in enumerate(sorted(self.entries, key=lambda c: c['names'][self.language]), start=1):  # type: ignore
            if index == selected_bundle:
                embeds.append(
                    discord.Embed(
                        title=bundle['names'][self.language] + f' {collection_title}',  # type: ignore
                        description=f"{vp_emoji} {bundle['price']}",  # type: ignore
                        color=0xFD4554,
                    ).set_image(url=bundle['icon'])  # type: ignore
                )

                for items in sorted(bundle['items'], key=lambda x: x['price'], reverse=True):  # type: ignore
                    item = GetItems.get_item_by_type(items['type'], items['uuid'])  # type: ignore
                    item_type = get_item_type(items['type'])  # type: ignore

                    emoji = GetEmoji.tier_by_bot(items['uuid'], self.bot) if item_type == 'Skins' else ''  # type: ignore
                    icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large']
                    color = 0xFD4554 if item_type == 'Skins' else 0x0F1923

                    embed = self.base_embed(
                        f"{emoji} {item['names'][self.language]}",
                        f"{vp_emoji} {items['price']}",  # type: ignore
                        icon,
                        color,  # type: ignore
                    )
                    embeds.append(embed)

                    if len(embeds) == 10:
                        embeds_list.append(embeds)
                        embeds = []

                if len(embeds) != 0:
                    embeds_list.append(embeds)

        self.embeds = embeds_list

    def build_featured_bundle(self, bundle: list[dict]) -> list[discord.Embed]:
        """Builds the featured bundle embeds"""

        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')

        name = bundle['names'][self.language]  # type: ignore

        featured_bundle_title = self.response.get('TITLE')

        duration = bundle['duration']  # type: ignore
        duration_text = self.response.get('DURATION').format(  # type: ignore
            duration=format_relative(datetime.utcnow() + timedelta(seconds=duration))
        )

        bundle_price = bundle['price']  # type: ignore
        bundle_base_price = bundle['base_price']  # type: ignore
        bundle_price_text = (
            f"**{bundle_price}** {(f'~~{bundle_base_price}~~' if bundle_base_price != bundle_price else '')}"
        )

        embed = discord.Embed(
            title=featured_bundle_title.format(bundle=name),  # type: ignore
            description=f'{vp_emoji} {bundle_price_text}' f' ({duration_text})',
            color=0xFD4554,
        )
        embed.set_image(url=bundle['icon'])  # type: ignore

        embed_list = []

        embeds = [embed]

        for items in sorted(bundle['items'], reverse=True, key=lambda c: c['base_price']):  # type: ignore
            item = GetItems.get_item_by_type(items['type'], items['uuid'])
            item_type = get_item_type(items['type'])
            emoji = GetEmoji.tier_by_bot(items['uuid'], self.bot) if item_type == 'Skins' else ''
            if item_type == 'Player titles':
                icon = None
            else:
                icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large'] if item['icon']['large'] else item['icon']['small']
            color = 0xFD4554 if item_type == 'Skins' else 0x0F1923

            item_price = items['price']
            item_base_price = items['base_price']
            item_price_text = f"**{item_price}** {(f'~~{item_base_price}~~' if item_base_price != item_price else '')}"

            embed = self.base_embed(
                f"{emoji} {item['names'][self.language]}", f'**{vp_emoji}** {item_price_text}', icon, color
            )

            embeds.append(embed)

            if len(embeds) == 10:
                embed_list.append(embeds)
                embeds = []

        if len(embeds) != 0:
            embed_list.append(embeds)

        return embed_list

    def build_select(self) -> None:
        """Builds the select bundle"""
        for index, bundle in enumerate(sorted(self.entries, key=lambda c: c['names']['en-US']), start=1):  # type: ignore
            self.select_bundle.add_option(label=bundle['names'][self.language], value=index)  # type: ignore

    @ui.select(placeholder='Select a bundle:')
    async def select_bundle(self, interaction: Interaction, select: ui.Select):
        # TODO: fix freeze
        self.build_embeds(int(select.values[0]))
        self.fill_items()
        self.update_button()
        embeds = self.embeds[0]
        await interaction.response.edit_message(embeds=embeds, view=self)

    @ui.button(label='Back')
    async def back_button(self, interaction: Interaction, button: ui.Button):
        self.current_page = 0
        embeds = self.embeds[self.current_page]
        self.update_button()
        await interaction.response.edit_message(embeds=embeds, view=self)

    @ui.button(label='Next')
    async def next_button(self, interaction: Interaction, button: ui.Button):
        self.current_page = 1
        embeds = self.embeds[self.current_page]
        self.update_button()
        await interaction.response.edit_message(embeds=embeds, view=self)

    def update_button(self) -> None:
        """Updates the button"""
        self.next_button.disabled = self.current_page == len(self.embeds) - 1
        self.back_button.disabled = self.current_page == 0

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This menus cannot be controlled by you, sorry!', ephemeral=True)
        return False

    async def start(self) -> None:
        """Starts the bundle view"""

        if len(self.entries) == 1:
            self.build_embeds()
            self.fill_items()
            self.update_button()
            embeds = self.embeds[0]
            await self.interaction.followup.send(embeds=embeds, view=self)
            return
        elif len(self.entries) != 0:
            self.add_item(self.select_bundle)
            placeholder = self.response.get('DROPDOWN_CHOICE_TITLE')
            self.select_bundle.placeholder = placeholder
            self.build_select()
            await self.interaction.followup.send('\u200b', view=self)
            return

        not_found_bundle = self.response.get('NOT_FOUND_BUNDLE')
        raise ValorantBotError(not_found_bundle)

    async def start_furture(self) -> None:
        """Starts the featured bundle view"""

        BUNDLES = []
        FBundle = self.entries['FeaturedBundle']['Bundles']

        for fbd in FBundle:
            get_bundle = GetItems.get_bundle(fbd['DataAssetID'])

            bundle_payload = {
                'uuid': fbd['DataAssetID'],
                'icon': get_bundle['icon'],
                'names': get_bundle['names'],
                'duration': fbd['DurationRemainingInSeconds'],
                'items': [],
            }

            price = 0
            baseprice = 0

            for items in fbd['Items']:
                item_payload = {
                    'uuid': items['Item']['ItemID'],
                    'type': items['Item']['ItemTypeID'],
                    'item': GetItems.get_item_by_type(items['Item']['ItemTypeID'], items['Item']['ItemID']),
                    'amount': items['Item']['Amount'],
                    'price': items['DiscountedPrice'],
                    'base_price': items['BasePrice'],
                    'discount': items['DiscountPercent'],
                }
                price += int(items['DiscountedPrice'])
                baseprice += int(items['BasePrice'])
                bundle_payload['items'].append(item_payload)

            bundle_payload['price'] = price
            bundle_payload['base_price'] = baseprice

            BUNDLES.append(bundle_payload)

        if len(BUNDLES) > 1:
            return await self.interaction.followup.send('\u200b', view=SelectionFeaturedBundleView(BUNDLES, self))

        self.embeds = self.build_featured_bundle(BUNDLES[0])  # type: ignore
        self.fill_items()
        self.update_button()
        await self.interaction.followup.send(embeds=self.embeds[0], view=self)  # type: ignore


class SelectionFeaturedBundleView(ui.View):
    def __init__(self, bundles: list[dict[str, Any]], other_view: ui.View | BaseBundle | None = None):  # type: ignore
        self.bundles = bundles
        self.other_view = other_view
        super().__init__(timeout=120)
        self.__build_select()
        self.select_bundle.placeholder = self.other_view.response.get('DROPDOWN_CHOICE_TITLE')  # type: ignore

    def __build_select(self) -> None:
        """Builds the select bundle"""
        for index, bundle in enumerate(self.bundles):
            self.select_bundle.add_option(label=bundle['names'][str(VLR_locale)], value=str(index))

    @ui.select(placeholder='Select a bundle:')
    async def select_bundle(self, interaction: Interaction, select: ui.Select):
        value = select.values[0]
        bundle = self.bundles[int(value)]
        embeds = self.other_view.build_featured_bundle(bundle)  # type: ignore
        self.other_view.fill_items()  # type: ignore
        self.other_view.update_button()  # type: ignore
        await interaction.response.edit_message(content=None, embeds=embeds[0], view=self.other_view)  # type: ignore
