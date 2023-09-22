from discord.ext import commands

from connection import characters
from functions import load_character
from helpers import GameMode
from models import Character


class Player(commands.Cog):
    @commands.command(name="create", help="Create a character.")
    async def create(self, ctx, name=None):
        user_id = ctx.message.author.id

        # if no name is specified, use the creator's nickname
        if not name:
            name = ctx.message.author.name

        # only create a new character if the user does not already have one
        if not Character.count_documents({"_id": user_id}):  # type: ignore
            character = Character(
                **{
                    "name": name,
                    "hp": 16,
                    "max_hp": 16,
                    "attack": 2,
                    "defense": 1,
                    "mana": 0,
                    "level": 1,
                    "xp": 0,
                    "gold": 0,
                    "inventory": [],
                    "mode": GameMode.ADVENTURE,
                    "battling": None,
                    "user_id": user_id,
                }
            )
            character.save_to_db()
            await ctx.message.reply(
                f"New level 1 character created: **{name}**. Enter `!status` to see your stats."
            )
        else:
            await ctx.message.reply("You have already created your character.")

    @commands.command(
        name="levelup",
        help="Advance to the next level. Specify a stat to increase (HP, ATTACK, DEFENSE).",
    )
    async def levelup(self, ctx, increase=None):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        if character.mode != GameMode.ADVENTURE:
            await ctx.message.reply("Can only call this command outside of battle!")
            return

        ready, xp_needed = character.ready_to_level_up()
        if not ready:
            await ctx.message.reply(
                f"You need another {xp_needed} to advance to level {character.level+1}"
            )
            return

        if not increase:
            await ctx.message.reply(
                "Please specify a stat to increase (HP, ATTACK, DEFENSE)"
            )
            return

        increase = increase.lower()
        if (
            increase == "hp"
            or increase == "hitpoints"
            or increase == "max_hp"
            or increase == "maxhp"
        ):
            increase = "max_hp"
        elif increase == "attack" or increase == "att":
            increase = "attack"
        elif increase == "defense" or increase == "def" or increase == "defence":
            increase = "defense"

        success, new_level = character.level_up(increase)
        if success:
            await ctx.message.reply(
                f"**{character.name}** advanced to level {new_level}, gaining 1 {increase.upper().replace('_', ' ')}."
            )
        else:
            await ctx.message.reply(f"**{character.name}** failed to level up.")

    @commands.command(name="die", help="Destroy current character.")
    async def die(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        character.die()

        await ctx.message.reply(
            f"Character **{character.name}** is no more. Create a new one with `!create`."
        )

    @commands.command(
        name="reset", help="[DEV] Destroy and recreate current character."
    )
    async def reset(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        characters.delete_one({"_id": user_id})

        await ctx.message.reply(f"Character deleted.")
        await self.create(ctx)


async def setup(bot):
    await bot.add_cog(Player(bot))
