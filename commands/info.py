from discord.ext import commands

from connection import characters
from embeds import *
from functions import load_character


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="inventory", help="Get inventory.")
    async def inventory(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        embed = inventory_embed(ctx, character)
        await ctx.message.reply(embed=embed)

    @commands.command(name="status", help="Get information about your character.")
    async def status(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        embed = status_embed(ctx, character)
        await ctx.message.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
