import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from connection import test
from functions import cmd_loader

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"BOT {bot.user} connected to Discord!")
    print(f"MDB connected: {test()}")
    print(f"COG {await cmd_loader(bot)} commands loaded")


bot.run(f"{DISCORD_TOKEN}")
