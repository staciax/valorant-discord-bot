from __future__ import annotations

# Standard
import os
import sys
import traceback
import asyncio
import aiohttp
import discord
from dotenv import load_dotenv
from discord.ext import commands
from utils import locale_v2

load_dotenv()

initial_extensions = [
    'cogs.admin',
    'cogs.errors',
    'cogs.notify',
    'cogs.valorant'
]  

# intents required
intents = discord.Intents.default()
intents.message_content = True

BOT_PREFIX = '-'

class ValorantBot(commands.Bot):
    debug: bool
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)
        self.bot_version = '3.1.0-rc1'
        self.tree.interaction_check = self.interaction_check

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:     
        await self.tree.sync()
        print(f"\nLogged in as: {self.user}\n\n BOT IS READY !")
        print(f"Version: {self.bot_version}")

        # bot presence
        activity_type = discord.ActivityType.listening
        await self.change_presence(activity=discord.Activity(type=activity_type, name="(╯•﹏•╰)"))
              
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
    
        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id
        
        await self.load_cogs()
    
    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f'Failed to load extension {ext}.', file=sys.stderr)
                traceback.print_exc()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        locale_v2.set_interaction_locale(interaction.locale) # bot responses localized
        locale_v2.set_valorant_locale(interaction.locale) # valorant localized
        return True 

    async def close(self) -> None:
        await self.session.close()
            
    async def start(self, debug:bool = False) -> None:
        self.debug = debug
        return await super().start(os.getenv('TOKEN'), reconnect=True)

def run_bot() -> None:
    bot = ValorantBot()
    asyncio.run(bot.start(debug=False))

if __name__ == '__main__':
    run_bot()