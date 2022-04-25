# Standard
import discord
import contextlib
from discord.ext import commands
from discord import Interaction, TextStyle, Embed, ui
from typing import Awaitable, List, Dict

# Local
from .useful import (
    get_skin_price,
    get_emoji_tier_by_bot,
    get_skin,
    json_read,
    json_save,
    get_item_by_type,
    get_bundle
)
from .resources import points as points_emoji, get_item_type
from .db import DATABASE

class NotifyView(discord.ui.View):
    def __init__(self, user_id, uuid, name):
        self.user_id = user_id
        self.uuid = uuid
        self.name = name
        super().__init__(timeout=600)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == int(self.user_id):
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!', ephemeral=True)
        return False

    async def on_timeout(self):
        with contextlib.suppress(Exception):
            self.remve_notify.disabled = True
            await self.message.edit_original_message(view=self)

    @discord.ui.button(label='Remove Notify', emoji='✖️', style=discord.ButtonStyle.red)
    async def remve_notify(self, interaction:discord.Interaction, button:discord.Button):
        data = json_read('notifys')
        
        for i in range(len(data)):
            if data[i]['uuid'] == self.uuid and data[i]['id'] == str(self.user_id):
                data.pop(i)
                break
        
        json_save('notifys', data)

        self.remve_notify.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f'**{self.name}** been removed from notify', ephemeral=True)

class NotifyListButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(
            label=label,
            style=discord.enums.ButtonStyle.red,
            custom_id=str(custom_id)
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer()    
        
        data:list = json_read('notifys')
        for i in range(len(data)):
            if data[i]['uuid'] == self.custom_id and data[i]['id'] == str(self.view.interaction.user.id):
                data.pop(i)
                break
        
        json_save('notifys', data)
        
        del self.view.skin_source[self.custom_id]
        self.view.update_button()
        embed = self.view.main_embed()
        await self.view.interaction.edit_original_message(embed=embed, view=self.view)

class NotifyViewList(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.bot: commands.Bot = getattr(interaction, "client", interaction._state._get_client())
        self.default_language = 'en-US'
        super().__init__()
    
    async def on_timeout(self) -> None:
        embed = discord.Embed(color=0x2F3136, description='🕙 Timeout')
        await self.interaction.edit_original_message(embed=embed, view=None) 
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:        
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!', ephemeral=True)
        return False

    def update_button(self):
        self.clear_items()
        self.create_button()

    def create_button(self):
        data = self.skin_source
        for index, skin in enumerate(data, start=1):
            self.add_item(NotifyListButton(label=index, custom_id=skin))

    def get_data(self):
        database = json_read('notifys')
        notify_skin = [x['uuid'] for x in database if x['id'] == str(self.interaction.user.id)]
        skin_source:dict = {}

        for uuid in notify_skin:
            skin = get_skin(uuid)
            name = skin['names'][self.default_language]
            icon = skin['icon']

            skin_source[uuid] = {
                'name': name,
                'icon':  icon,
                'price': get_skin_price(uuid),
                'emoji': get_emoji_tier_by_bot(uuid, self.bot)
            }
        self.skin_source = skin_source

    def main_embed(self) -> discord.Embed:        
        skin_list: dict = self.skin_source
        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')

        embed = discord.Embed(description='\u200b', title='Your Notify:', color=0xfd4554)
        embed.set_footer(text='Click button for remove')

        if len(skin_list) == 0:
            embed.description = f"You don't have skin notify"
        else:
            count = 0
            text_format = []
            for skin in skin_list:
                name = skin_list[skin]['name']
                icon = skin_list[skin]['icon']
                price = skin_list[skin]['price']
                emoji = skin_list[skin]['emoji']
                count += 1
                text_format.append(f"**{count}.** {emoji} **{name}**\n{vp_emoji} {price}")
            else:
                embed.description = '\n'.join(text_format)
                if len(skin_list) == 1:
                    embed.set_thumbnail(url=icon)
        
        return embed
    
    async def start(self):
        self.get_data()
        self.create_button()
        embed = self.main_embed()
        await self.interaction.response.send_message(embed=embed, view=self)

class TwoFA_UI(ui.Modal, title='Two-factor authentication'):
    '''Modal for riot login with 2 factor authentication'''
    
    def __init__(self, interaction: Interaction, db: DATABASE, cookie: dict, message: str) -> None:
        super().__init__(timeout=600)
        self.interaction = interaction
        self.db = db
        self.cookie = cookie
        self.two2fa.placeholder = message
    
    two2fa = ui.TextInput(
        label='Input 2FA Code',
        max_length=6,
        style=TextStyle.short
    )

    async def on_submit(self, interaction: Interaction) -> None:

        code = self.two2fa.value
        if code:
            cookie = self.cookie
            user_id = self.interaction.user.id
            auth = self.db.auth

            async def send_embed(content: str) -> Awaitable[None]:
                embed = Embed(description = content, color=0xfd4554)
                if interaction.response.is_done():
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            if not code.isdigit():
                return await send_embed(f"`{code}` is not a number")

            response = await auth.give2facode(code, cookie)

            if response['auth'] == 'response':
                
                login = await self.db.login(user_id, response)
                if login['auth']:
                    return await send_embed(f"Successfully logged in as **{login['player']}!**")
                
                return await send_embed(login['error'])
                
            elif response['auth'] == 'failed':
                return await send_embed(login['error'])
    
    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        embed = Embed(description = 'Oops! Something went wrong.', color=0xfd4554)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# inspired by https://github.com/giorgi-o
class BaseBundle(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, entries: Dict):
        self.interaction = interaction
        self.entries = entries
        self.bot: commands.Bot = getattr(interaction, "client", interaction._state._get_client())
        self.current_page: int = 0
        self.embeds: List[List[discord.Embed]] = []
        self.page_format = {}
        super().__init__()
        self.clear_items()
        
    def fill_items(self, force=False):
        self.clear_items()
        if len(self.embeds) > 1 or force:
            self.add_item(self.back_button)
            self.add_item(self.next_button)

    def base_embed(self, title:str, description:str, icon:str, color: int=0x0F1923) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_thumbnail(url=icon)
        return embed

    def build_embeds(self, selected_bundle: int = 1):

        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')
    
        embeds_list = []
        embeds = []
        for index, bundle in enumerate(sorted(self.entries, key=lambda c: c['names']['en-US']), start=1):
            if index == selected_bundle:
                embeds.append(discord.Embed(title=bundle['names']['en-US'] + " Collection", description=f"{vp_emoji} {bundle['price']}",color=0xfd4554).set_image(url=bundle['icon']))
                
                for items in bundle['items']:
                    item = get_item_by_type(items['type'], items['uuid'])
                    item_type = get_item_type(items['type'])

                    emoji = get_emoji_tier_by_bot(items['uuid'], self.bot) if items['type'] == 'Skin' else ''
                    icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large']
                    color = 0xfd4554 if item_type == 'Skins' else 0x0F1923
                
                    embed = self.base_embed(f"{emoji} {item['names']['en-US']}", f"{vp_emoji} {items['price']}", icon, color)
                    embeds.append(embed)

                    if len(embeds) == 10:
                        embeds_list.append(embeds)
                        embeds = []

                if len(embeds) != 0:
                    embeds_list.append(embeds)

        self.embeds = embeds_list

    def build_Featured_Bundle(self, bundle: List[Dict]) -> List[discord.Embed]:
        vp_emoji = discord.utils.get(self.bot.emojis, name='ValorantPointIcon')

        name = bundle['names']['en-US']

        embed = discord.Embed(title=f"Featured Bundle: {name} Collection", description=f"{vp_emoji} {bundle['price']}",color=0xfd4554).set_image(url=bundle['icon'])

        embed_list = []

        embeds = [embed]

        for items in sorted(bundle['items'], reverse=True, key=lambda c: c['price']):

            item = get_item_by_type(items['type'], items['uuid'])
            item_type = get_item_type(items['type'])
            emoji = get_emoji_tier_by_bot(items['uuid'], self.bot) if items['type'] == 'Skin' else ''
            icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large']
            color = 0xfd4554 if item_type == 'Skins' else 0x0F1923
            embed = self.base_embed(f"{emoji} {item['names']['en-US']}", f"{vp_emoji} {items['price']}", icon, color)
            embeds.append(embed)

            if len(embeds) == 10:
                embed_list.append(embeds)
                embeds = []
        
        if len(embeds) != 0:
            embed_list.append(embeds)

        return embed_list

    def build_select(self):
        for index, bundle in enumerate(sorted(self.entries, key=lambda c: c['names']['en-US']), start=1):
            self.select_bundle.add_option(label=bundle['names']['en-US'], value=index)

    @ui.select(placeholder='Select a bundle:')
    async def select_bundle(self, interaction: Interaction, select: ui.Select):
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

    def update_button(self):
        self.next_button.disabled = self.current_page == len(self.embeds) - 1
        self.back_button.disabled = self.current_page == 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This menus cannot be controlled by you, sorry!', ephemeral=True)
        return False
        
    async def start(self):
        if len(self.entries) == 1:
            self.build_embeds()
            self.fill_items()
            self.update_button()
            embeds = self.embeds[0]
            return await self.interaction.followup.send(embeds=embeds, view=self)
        self.add_item(self.select_bundle)
        self.build_select()
        await self.interaction.followup.send('\u200b', view=self)

    async def start_furture(self):
        FBundle = self.entries['FeaturedBundle']['Bundle']

        bundle_payload = {
            "uuid": FBundle["DataAssetID"],
            "icon": get_bundle(FBundle["DataAssetID"])['icon'],
            "names": get_bundle(FBundle["DataAssetID"])['names'],
            "duration": FBundle["DurationRemainingInSeconds"],
            "items": []
        }

        price = 0
        baseprice = 0

        for items in FBundle['Items']:
            item_payload = {
                "uuid": items["Item"]["ItemID"],
                "type": items["Item"]["ItemTypeID"],
                "item" : get_item_by_type(items["Item"]["ItemTypeID"], items["Item"]["ItemID"]),
                "amount": items["Item"]["Amount"],
                "price": items["DiscountedPrice"],
                "base_price": items["BasePrice"],
                "discount": items["DiscountPercent"]
            }
            price += int(items["DiscountedPrice"])
            baseprice += int(items["BasePrice"])
            bundle_payload['items'].append(item_payload)

        bundle_payload['price'] = price
        bundle_payload['base_price'] = baseprice

        self.embeds = self.build_Featured_Bundle(bundle_payload)
        self.fill_items()
        self.update_button()
        await self.interaction.followup.send(embeds=self.embeds[0], view=self)