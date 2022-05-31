# Standard
import os
import asyncio
import aiohttp
import discord
from dotenv import load_dotenv
from discord.ext import commands

# Local
from utils.valorant.db import DATABASE
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.cache import get_cache

load_dotenv()

initial_extensions = [
    'cogs.error_handler',
    'cogs.admin',
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
        self.bot_version = '3.1.0-pre'

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:     
        await self.tree.sync()
        print(f"\nLogged in as: {self.user}\n\n BOT IS READY !")
        print(f"Version: {self.bot_version}")
              
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
    
        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id
            
        self.db = DATABASE()
        self.endpoint = API_ENDPOINT(self.session)
        
        self.setup_cache()
        await self.load_cogs()
    
    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            await self.load_extension(ext)

    def setup_cache(self) -> None:
        try:
            open('data/cache.json')
        except FileNotFoundError:
            get_cache()

    async def close(self) -> None:
        await self.session.close()
            
    async def start(self, debug:bool = False) -> None:
        self.debug = debug
        return await super().start(os.getenv('TOKEN'), reconnect=True)

def run_bot():
    bot = ValorantBot()
    asyncio.run(bot.start(debug=False))

if __name__ == '__main__':
    run_bot()