from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import Interaction, app_commands, ui
from discord.ext import commands

if TYPE_CHECKING:
    from bot import ValorantBot


class Admin(commands.Cog):
    """Error handler"""

    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, sync_type: Literal['guild', 'global']) -> None:
        """Sync the application commands"""

        async with ctx.typing():
            if sync_type == 'guild':
                self.bot.tree.copy_global_to(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                await ctx.reply(f"Synced guild !")
                return

            await self.bot.tree.sync()
            await ctx.reply(f"Synced global !")

    @commands.command()
    @commands.is_owner()
    async def unsync(self, ctx: commands.Context, unsync_type: Literal['guild', 'global']) -> None:
        """Unsync the application commands"""

        async with ctx.typing():
            if unsync_type == 'guild':
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                await ctx.reply(f"Un-Synced guild !")
                return

            self.bot.tree.clear_commands()
            await self.bot.tree.sync()
            await ctx.reply(f"Un-Synced global !")

    @app_commands.command(description='Shows basic information about the bot.')
    async def about(self, interaction: Interaction) -> None:
        """Shows basic information about the bot."""

        owner_url = f'https://discord.com/users/240059262297047041'
        github_project = 'https://github.com/staciax/Valorant-DiscordBot'
        support_url = 'https://discord.gg/FJSXPqQZgz'

        embed = discord.Embed(color=0xFFFFFF)
        embed.set_author(name='VALORANT BOT PROJECT', url=github_project)
        embed.set_thumbnail(url='https://i.imgur.com/ZtuNW0Z.png')
        embed.add_field(name='DEV:', value=f"[ꜱᴛᴀᴄɪᴀ.#7475]({owner_url})", inline=False)
        embed.add_field(
            name='ᴄᴏɴᴛʀɪʙᴜᴛᴏʀꜱ:',
            value=f"[kiznick](https://github.com/kiznick)\n"
            "[KANATAISGOD](https://github.com/KANATAISGOD)\n"
            "[TMADZ2007](https://github.com/KANATAISGOD')\n"
            "[sevzin](https://github.com/sevzin)\n"
            "[miigoxyz](https://github.com/miigoxyz)\n"
            "[Connor](https://github.com/ConnorDoesDev)\n"
            "[KohanaSann](https://github.com/KohanaSann)\n"
            "[RyugaXhypeR](https://github.com/RyugaXhypeR)\n"
            "[Austin Hornhead](https://github.com/marchingon12)\n",
            inline=False,
        )
        view = ui.View()
        view.add_item(ui.Button(label='GITHUB', url=github_project, row=0))
        view.add_item(ui.Button(label='KO-FI', url='https://ko-fi.com/staciax', row=0))
        view.add_item(ui.Button(label='SUPPORT SERVER', url=support_url, row=0))

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Admin(bot))
