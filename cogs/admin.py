from __future__ import annotations

import discord
from discord import app_commands, Interaction, ui
from discord.ext import commands

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from bot import ValorantBot

class Admin(commands.Cog):
    """Error handler"""

    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, sync_type: Literal['guild', 'global']) -> None:
        """ Sync the application commands """

        async with ctx.typing():
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Synced guild !")
                return

            await self.bot.tree.sync()
            await ctx.reply(f"Synced global !")

    @commands.command()
    @commands.is_owner()
    async def unsync(self, ctx: commands.Context, unsync_type: Literal['guild', 'global']) -> None:
        """ Unsync the application commands """

        async with ctx.typing():
            if unsync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                commands = self.bot.tree.get_commands(guild=guild)
                for command in commands:
                    self.bot.tree.remove_command(command, guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Un-Synced guild !")    
                return
    
            commands = self.bot.tree.get_commands()
            for command in commands:
                self.bot.tree.remove_command(command)
            await self.bot.tree.sync()
            await ctx.reply(f"Un-Synced global !")

    @app_commands.command(description='Shows basic information about the bot.')
    async def about(self, interaction: Interaction) -> None:
        """ Shows basic information about the bot. """
        
        owner_id = 240059262297047041
        owner_url = f'https://discord.com/users/{owner_id}'
        github_project = 'https://github.com/staciax/Valorant-DiscordBot'
        support_url = 'https://discord.gg/FJSXPqQZgz'
        
        embed = discord.Embed(color=0xffffff)
        embed.set_author(name='ᴠᴀʟᴏʀᴀɴᴛ ʙᴏᴛ ᴘʀᴏᴊᴇᴄᴛ', url=github_project)
        embed.set_thumbnail(url='https://i.imgur.com/ZtuNW0Z.png')
        embed.add_field(
            name='ᴅᴇᴠᴇʟᴏᴘᴇʀ:',
            value=f"[ꜱᴛᴀᴄɪᴀ.#7475]({owner_url})",
            inline=False
        )
        embed.add_field(
            name='ᴄᴏɴᴛʀɪʙᴜᴛᴏʀꜱ:',
            value=f"[kiznick](https://github.com/kiznick)\n"
                "[KANATAISGOD](https://github.com/KANATAISGOD)\n"
                "[TMADZ2007](https://github.com/KANATAISGOD')\n"
                "[sevzin](https://github.com/sevzin)\n"
                "[miigoxyz](https://github.com/miigoxyz)\n"
                "[Connor](https://github.com/ConnorDoesDev)\n"
                "[KohanaSann](https://github.com/KohanaSann)\n",
            inline=False
        )
        view = ui.View()
        view.add_item(ui.Button(label='ɢɪᴛʜᴜʙ', url=github_project, row=0))
        view.add_item(ui.Button(label='ᴋᴏ-ꜰɪ', url='https://ko-fi.com/staciax', row=0))
        view.add_item(ui.Button(label='ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ', url=support_url, row=0))

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Admin(bot))