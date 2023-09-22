import os

from discord.ext import commands


async def cog_loader(bot: commands.Bot) -> int:
    cogs = 0
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")
                cogs += 1
            except:
                pass
    return cogs
