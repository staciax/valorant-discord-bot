# Standard
import discord
from discord.ext import commands

class error_handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'-{self.__class__.__name__}')

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        # i don't know why isinstance not work
        # if isinstance(error, commands.UserInputError):

        # isinstance artificial
        error = (str(error)).split(':')

        embed = discord.Embed(description=error[2], color=0xfe676e)
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(error_handler(bot))