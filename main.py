import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from connection import test
from functions import cog_loader

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"BOT {bot.user} connected to Discord!")
    print(f"MDB connected: {test()}")
    print(f"COG {await cog_loader(bot)} commands loaded")
    print("CMD sincronizando")
    print(f"CMD {len(await bot.tree.sync())} sincronizado")


bot.run(f"{DISCORD_TOKEN}")
