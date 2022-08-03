from discord.ext import tasks
from discord import app_commands, Interaction
from discord.app_commands.checks import dynamic_cooldown
from typing import Literal, List

from datetime import datetime, time, timedelta
from utils.checks import cooldown_5s

from ._abc import MixinMeta


class Notify(MixinMeta):
    """ Notify cog """

    async def send_notify(self):
        ...  # todo webhook send

    @tasks.loop(time=time(hour=0, minute=0, second=10))  # utc 00:00:15
    async def notify_alert(self) -> None:
        await self.send_notify()

    @notify_alert.before_loop
    async def before_daily_send(self) -> None:
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')

    notify = app_commands.Group(name='notify', description='แจ้งเตือนสกิน | Notify commands')

    @notify.command(name='add', description='Set a notification when a specific skin is available on your store')
    @dynamic_cooldown(cooldown_5s)
    @app_commands.describe(skin='The name of the skin you want to notify')
    async def notify_add(self, interaction: Interaction, skin: str) -> None:
        """เพิ่มแจ้งเตือนสกิน | Set a notification when a specific skin is available on your store"""
        ...

    @notify_add.autocomplete('skin')
    async def notify_add_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        ...

    @notify.command(name='list', description='View skins you have set a for notification.')
    @dynamic_cooldown(cooldown_5s)
    async def notify_list(self, interaction: Interaction) -> None:
        """ดูรายการแจ้งเตือน | View skins you have set a notification for"""
        ...

    @notify.command(name='mode', description='Change notification mode')
    @app_commands.describe(mode='Choose notification')
    @dynamic_cooldown(cooldown_5s)
    async def notify_mode(self, interaction: Interaction, mode: Literal['Specified Skin', 'All Skin', 'Off']) -> None:
        """เปลี่ยนโหมดแจ้งเตือน | Set Skin Notifications mode"""
        ...

    @notify.command(name='test')
    @dynamic_cooldown(cooldown_5s)
    async def notify_test(self, interaction: Interaction) -> None:
        """ ทดสอบแจ้งเตือน | Test Notifications"""
        ...
