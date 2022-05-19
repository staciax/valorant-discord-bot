import discord
from discord.ext import commands

class Admin(commands.Cog):
    """Error handler"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    # @commands.is_owner()
    async def sync(self, ctx: commands.Context, sync_type: str = None) -> None:

        if self.bot.owner_id is None:
            if ctx.author.guild_permissions.administrator != True:
                await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
                return

        if sync_type is None:
            return await ctx.send('you need to specify a sync type.')

        try:
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Synced guild !")
            elif sync_type == 'global':
                await self.bot.tree.sync()
                await ctx.reply(f"Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to sync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to sync.', delete_after=30)

    @commands.command()
    # @commands.is_owner()
    async def unsync(self, ctx: commands.Context, unsync_type: str = None) -> None:

        if self.bot.owner_id is None:
            if ctx.author.guild_permissions.administrator != True:
                await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
                return
        
        if unsync_type is None:
            return await ctx.send('you need to specify a unsync type.')

        try:
            if unsync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                commands = self.bot.tree.get_commands(guild=guild)
                for command in commands:
                    self.bot.tree.remove_command(command, guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Un-Synced guild !")    
            elif unsync_type == 'global':
                commands = self.bot.tree.get_commands()
                for command in commands:
                    self.bot.tree.remove_command(command)
                await self.bot.tree.sync()
                await ctx.reply(f"Un-Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to unsync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to unsync.', delete_after=30)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))