# Standard
import os
import traceback
import aiohttp
import discord
from dotenv import load_dotenv
from typing import Union
from discord import Embed, Interaction
from discord.ext import commands
from discord.app_commands import (
    AppCommandError,
    CommandInvokeError,
    CommandNotFound,
    MissingPermissions,
    BotMissingPermissions
)

# Local
from utils.valorant.db import DATABASE
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.cache import get_cache

load_dotenv()

initial_extensions = [
    'cogs.valorant',
    'cogs.notify'
]  

class ValorantBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='-', case_insensitive=True, intents=intents)
        owner_id = os.getenv('OWNER_ID')
        if owner_id is not None:
            try:
                self.owner_id = int(owner_id)
            except ValueError:
                pass
        self.languages = {}
        self.theme = 0xffffff
        self.bot_version = '0.0.1a'
        
    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            await self.load_extension(ext)

    def setup_cache(self) -> None:
        try:
            open('data/cache.json')
        except FileNotFoundError:
            get_cache()
              
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        
        self.db = DATABASE()
        self.endpoint = API_ENDPOINT(self.session)
        
        self.setup_cache()
        await self.load_cogs()
        
    async def close(self) -> None:
        await self.session.close()
            
    async def on_ready(self) -> None:     
        await self.tree.sync()
        print(f"\nLogged in as: {self.user}\n\n BOT IS READY !")
    
bot = ValorantBot()

@bot.command()
# @commands.is_owner()
async def sync(ctx: commands.Context, sync_type: str):

    if bot.owner_id is None:
        if ctx.author.guild_permissions.administrator != True:
            await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
            return

    try:
        if sync_type == 'guild':
            guild = discord.Object(id=ctx.guild.id)
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            await ctx.reply(f"Synced guild !")
        elif sync_type == 'global':
            await bot.tree.sync()
            await ctx.reply(f"Synced global !")
    except discord.Forbidden:
        await ctx.send("Bot don't have permission to sync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
    except discord.HTTPException:
        await ctx.send('Failed to sync.', delete_after=30)

@bot.command()
# @commands.is_owner()
async def unsync(ctx: commands.Context, sync_type: str):

    if bot.owner_id is None:
        if ctx.author.guild_permissions.administrator != True:
            await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
            return

    try:
        if sync_type == 'guild':
            guild = discord.Object(id=ctx.guild.id)
            commands = bot.tree.get_commands(guild=guild)
            for command in commands:
                bot.tree.remove_command(command, guild=guild)
            await bot.tree.sync(guild=guild)
            await ctx.reply(f"Un-Synced guild !")    
        elif sync_type == 'global':
            commands = bot.tree.get_commands()
            for command in commands:
                bot.tree.remove_command(command)
            await bot.tree.sync()
            await ctx.reply(f"Un-Synced global !")
    except discord.Forbidden:
        await ctx.send("Bot don't have permission to unsync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
    except discord.HTTPException:
        await ctx.send('Failed to unsync.', delete_after=30)

@bot.tree.error
async def tree_error_handler(interaction: Interaction, error: AppCommandError) -> None:
    """ Handles errors for all application commands."""

    if isinstance(error, CommandInvokeError):
        error = error.original
        traceback.print_exception(type(error), error, error.__traceback__)
    elif isinstance(error, Union[CommandNotFound, MissingPermissions, BotMissingPermissions]):
        error = error
    else:
        error = f"An unknown error occurred, sorry"
        traceback.print_exception(type(error), error, error.__traceback__)
    
    embed = Embed(description=f'{str(error)[:2000]}', color=0xfe676e)
    if interaction.response.is_done():
        return await interaction.followup.send(embed=embed, ephemeral=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))