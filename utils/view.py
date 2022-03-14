# Standard
import discord
from discord.ui import Modal, InputText
from utils.json_loader import data_read, data_save
from utils.useful import *
from utils.auth import Auth
from utils.emoji import points as Point_emoji, get_emoji_tier

class Notify(discord.ui.View):
    def __init__(self, user_id, uuid, name):
        self.user_id = user_id
        self.uuid = uuid
        self.name = name
        super().__init__()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == int(self.user_id):
            return True
        return False

    async def on_timeout(self):
        if self.message:
            self.remve_notify.disabled = True
            await self.message.edit(view=self)

    @discord.ui.button(label='Remove Notify', emoji='✖️', style=discord.ButtonStyle.red)
    async def remve_notify(self, button:discord.Button, interaction:discord.Interaction):
        data:list = data_read('notifys')
        
        for i in range(len(data)):
            if data[i]['uuid'] == self.uuid and data[i]['id'] == str(self.user_id):
                data.pop(i)
                break
        
        data_save('notifys', data)

        self.remve_notify.disabled = True
        await self.message.edit(view=self)
        await interaction.response.send_message(f'**{self.name}** been removed from notify', ephemeral=True)

class NumberButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(
            label=label,
            style=discord.enums.ButtonStyle.red,
            custom_id=str(custom_id)
        )

    async def callback(self, interaction: discord.Interaction):        
        
        data:list = data_read('notifys')
        for i in range(len(data)):
            if data[i]['uuid'] == self.custom_id and data[i]['id'] == str(self.view.ctx.author.id):
                data.pop(i)
                break
        
        data_save('notifys', data)
        
        del self.view.skin_source[self.custom_id]
        self.view.update_button()

        embed = self.view.main_embed()
        await self.view.message.edit(embed=embed, view=self.view)

class Notify_list(discord.ui.View):
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        super().__init__()
    
    async def on_timeout(self) -> None:
        if self.message:
            embed = discord.Embed(color=0x2F3136, description='🕙 Timeout')
            await self.message.edit(embed=embed, view=None) 
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:        
        if interaction.user == self.ctx.author:
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!', ephemeral=True)
        return False

    def update_button(self):
        self.clear_items()
        self.create_button()

    def create_button(self):
        data = self.skin_source
        for index, skin in enumerate(data, start=1):
            self.add_item(NumberButton(label=index, custom_id=skin))

    def get_data(self):
        database = data_read('notifys')
        notify_skin = [x['uuid'] for x in database if x['id'] == str(self.ctx.author.id)]
        skin_source:dict = {}

        for skin in notify_skin:
            skin_source[skin] = {
                'name': get_skin_name(skin),
                'icon':  get_skin_icon(skin),
                'price': get_skin_price(skin),
                'emoji': get_emoji_tier(skin)
            }
        self.skin_source = skin_source

    def main_embed(self) -> discord.Embed:        
        embed = discord.Embed(description='', title='Your Notify:',color=0xfd4554)
        embed.set_footer(text='Click for remove')
        skin_list = self.skin_source
        vlr_point = Point_emoji['vp']

        if len(skin_list) == 0:
            embed.description = f"You don't have skin notify"
        
        elif len(skin_list) == 1:
            for skin in skin_list:
                if skin_list[skin]['icon'] is not None:
                    embed.set_thumbnail(url=skin_list[skin]['icon'])
                    embed.description = f"**1.** {skin_list[skin]['emoji']} **{skin_list[skin]['name']}**\n{vlr_point} {skin_list[skin]['price']}"
                break
        else:
            count = 0
            for skin in skin_list:
                count += 1
                embed.description += f"\n**{count}.** {skin_list[skin]['emoji']} **{skin_list[skin]['name']}**\n{vlr_point} {skin_list[skin]['price']}"

        return embed
    
    async def start(self):
        self.get_data()
        self.create_button()
        embed = self.main_embed()
        self.message = await self.ctx.respond(embed=embed, view=self)   

class TwoFA_UI(Modal):
    def __init__(self, ctx, error) -> None:
        self.ctx = ctx
        super().__init__(title='Two-factor authentication')
        self.add_item(InputText(label="Input 2FA", placeholder=error, max_length=6, min_length=6))

    async def callback(self, interaction: discord.Interaction):
        
        text_callback = self.children
        
        if text_callback:
            code = text_callback[0].value
            user_id = self.ctx.author.id
            
            data = Auth(user_id=str(user_id)).give2facode(str(code))
            
            if data['auth'] == 'response':
            
                embed = discord.Embed(color=0xfd4554)
                embed.description = f"Successfully logged in as **{data['player']}!**"

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            elif data['auth'] == 'failed':
                await interaction.response.send_message(data['error'], ephemeral=True)
                return
        
        await interaction.response.send_message("Failed to Input 2FA.", ephemeral=True)