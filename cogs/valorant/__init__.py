from bot import LatteBot

from .valorant import Valorant


async def setup(bot: LatteBot) -> None:
    await bot.add_cog(Valorant(bot))
