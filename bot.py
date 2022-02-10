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

    # SETUP OPTIONAL
    cog:commands.Cog = bot.get_cog('valorant')
    command  = cog.get_commands()
    
    if message.content.startswith('-setup guild'):
        await bot.register_commands(commands=command, force=True)
        await message.channel.send('Setup in guild!')

    if message.content.startswith('-unsetup guild'):
        await bot.sync_commands(commands=command, unregister_guilds=[message.guild.id], force=True)
        await message.channel.send('Unsetup in guild!')
    
    if message.content.startswith('-setup global'):
        await bot.register_commands(commands=command, guild_id=message.guild.id, force=True)
        await message.channel.send('Setup in global!')

    # EMBED OPTIONAL
    data = config_read()
    if message.content.startswith('-embed pillow'):
        data["embed_design"] = 'ꜱᴛᴀᴄɪᴀ.#7475'
        config_save(data)
        await message.channel.send('`changed to embed pillow by ꜱᴛᴀᴄɪᴀ.#7475`')
    
    if message.content.startswith('-embed split'):
        data["embed_design"] = 'Giorgio#0609'
        config_save(data)
        await message.channel.send('`changed to embed split by Giorgio#0609`')

if __name__ == "__main__":
    TOKEN = config_read()['TOKEN']

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f'cogs.{file[:-3]}')

    bot.run(TOKEN)