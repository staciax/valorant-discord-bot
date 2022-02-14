# Standard
import discord
import os
from discord.ext import commands, tasks

# Local
from utils.json_loader import data_read, data_save, config_read, config_save
from utils.useful import get_valorant_version, fetch_skin, fetch_tier, pre_fetch_price, data_folder, create_json

class valorant_bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        # Stuff
        self.format_version = 1
        super().__init__(command_prefix='.', case_insensitive = True, *args, **kwargs)

    async def on_ready(self):
        if not get_version.is_running():
            get_version.start()
            
        # create data folder
        data_folder()
        create_json('skins', {'formats': self.format_version})
        
        print(f'\nBot: {bot.user}')
        print('\nCog loaded:')

bot = valorant_bot()

@tasks.loop(minutes=30)
async def get_version():
    bot.game_version = get_valorant_version()

    # data_store
    data = data_read('skins')
    data['formats'] = bot.format_version
    data['gameversion'] = bot.game_version
    data_save('skins', data)
    
    try:
        if data['skins']["version"] != bot.game_version: fetch_skin()
        if data['tiers']["version"] != bot.game_version: fetch_tier()
    except KeyError:
        fetch_skin()
        pre_fetch_price()
        fetch_tier()

@bot.event
async def on_message(message):
    # SETUP BOT
    
    cog:commands.Cog = bot.get_cog('valorant')
    command  = cog.get_commands()

    async def check_perm() -> bool:
        if message.author.guild_permissions.administrator == True:
            return True
        await message.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
        return False
    
    if message.content.startswith('-setup guild'):
        if await check_perm():
            msg = await message.reply('setting up . . .')
            await bot.sync_commands(commands=command, guild_ids=[message.guild.id], register_guild_commands=True, force=True)
            return await msg.edit('Setup in guild!')

    if message.content.startswith('-unsetup guild'):
        if await check_perm():
            msg = await message.reply('unsetup guild . . . ')
            await bot.sync_commands(commands=command, register_guild_commands=True, unregister_guilds=[message.guild.id], force=True)
            await msg.edit('Unsetup in guild!')

    if message.content.startswith('-setup global'):
        if await check_perm():
            await bot.register_commands(commands=command, guild_id=message.guild.id, force=True)
            return await message.reply('Setup in global!')

    # EMBED OPTIONAL
    data = config_read()
    if message.content.startswith('-embed pillow'):
        if await check_perm():
            data["embed_design"] = 'ꜱᴛᴀᴄɪᴀ.#7475'
            config_save(data)
            return await message.reply('`changed to embed pillow(ꜱᴛᴀᴄɪᴀ.#7475)`')
    
    if message.content.startswith('-embed split'):
        if await check_perm():
            data["embed_design"] = 'Giorgio#0609'
            config_save(data)
            return await message.reply('`changed to embed split(Giorgio#0609)`')

if __name__ == "__main__":
    TOKEN = config_read()['TOKEN']

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f'cogs.{file[:-3]}')

    bot.run(TOKEN)