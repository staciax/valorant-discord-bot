from datetime import datetime, time
from typing import TYPE_CHECKING, Literal

from discord import Interaction, app_commands
from discord.ext import commands, tasks

from utils.checks import owner_only, cooldown_5s
from discord.app_commands.checks import dynamic_cooldown

from ._abc import MixinMeta


class Notify(MixinMeta):

    @tasks.loop(time=time(hour=0, minute=0, second=10))  # utc 00:00:15
    async def notify_task(self) -> None:
        __verify_time = datetime.utcnow()
        if __verify_time.hour == 0:
            ...

    @notify_task.before_loop
    async def before_daily_send(self) -> None:
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')

    notify = app_commands.Group(name='notify', description='Notify commands')

    @notify.command(name='add', description='Set a notification when a specific skin is available on your store')
    @app_commands.describe(skin='The name of the skin you want to notify')
    @app_commands.guild_only()
    @dynamic_cooldown(cooldown_5s)
    async def notify_add(self, interaction: Interaction, skin: str) -> None:
        ...

    @notify.command(name='list', description='View skins you have set a for notification.')
    @dynamic_cooldown(cooldown_5s)
    async def notify_list(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

    @notify.command(name='mode', description='Change notification mode/channel.')
    @app_commands.describe(mode='Select the mode you want to change.')
    @dynamic_cooldown(cooldown_5s)
    async def notify_mode(self, interaction: Interaction, mode: Literal['Specified Skin', 'All Skin', 'Off']) -> None:
        ...

    @notify.command(name='channel', description='Change notification channel.')
    @app_commands.describe(channel='Select the channel you want to change.')
    @dynamic_cooldown(cooldown_5s)
    async def notify_channel(self, interaction: Interaction, channel: Literal['DM Message', 'Channel']) -> None:
        ...

    @notify.command(name='test', description='Testing notification')
    @dynamic_cooldown(cooldown_5s)
    async def notify_test(self, interaction: Interaction) -> None:
        ...

    # @notify.command(name='manage', description='Manage notification list.')
    # @owner_only()
    # async def notify_manage(self, interaction: Interaction) -> None:
    #     ...

