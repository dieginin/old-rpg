from discord.ext import commands

from connection import characters
from functions import load_character
from game import Enemy
from helpers import GameMode


class Combat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="fight", help="Fight the current enemy.")
    async def fight(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        if character.mode != GameMode.BATTLE:
            await ctx.message.reply("Can only call this command in battle!")
            return

        # Simulate battle
        enemy = character.battling if character.battling else Enemy("", 0, 0, 0, 0, 0)

        # Character attacks
        damage, killed = character.fight(enemy)
        if damage:
            await ctx.message.reply(
                f"**{character.name}** attacks {enemy.name}, dealing {damage} damage!"
            )
        else:
            await ctx.message.reply(
                f"**{character.name}** swings at {enemy.name}, but misses!"
            )

        # End battle in victory if enemy killed
        if killed:
            xp, gold, ready_to_level_up = character.defeat(enemy)

            await ctx.send(
                f"**{character.name}** vanquished the {enemy.name}, earning {xp} XP and {gold} GOLD. HP: {character.hp}/{character.max_hp}."
            )

            if ready_to_level_up:
                await ctx.send(
                    f"**{character.name}** has earned enough XP to advance to level {character.level+1}. Enter `!levelup` with the stat (HP, ATTACK, DEFENSE) you would like to increase. e.g. `!levelup hp` or `!levelup attack`."
                )

            return

        # Enemy attacks
        damage, killed = enemy.fight(character)
        if damage:
            await ctx.message.reply(
                f"{enemy.name} attacks **{character.name}**, dealing {damage} damage!"
            )
        else:
            await ctx.message.reply(
                f"{enemy.name} tries to attack **{character.name}**, but misses!"
            )

        character.save_to_db()  # enemy.fight() does not save automatically

        # End battle in death if character killed
        if killed:
            character.die()

            await ctx.message.reply(
                f"**{character.name}** was defeated by a {enemy.name} and is no more. Rest in peace, brave adventurer."
            )
            return

        # No deaths, battle continues
        await ctx.message.reply(f"The battle rages on! Do you `!fight` or `!flee`?")

    @commands.command(name="flee", help="Flee the current enemy.")
    async def flee(self, ctx):
        user_id = ctx.message.author.id

        if not characters.count_documents({"_id": user_id}):
            await ctx.message.reply(
                f"You have no charatacter, first you need to create one with `!create`."
            )
            return

        character = load_character(user_id)

        if character.mode != GameMode.BATTLE:
            await ctx.message.reply("Can only call this command in battle!")
            return

        enemy = character.battling if character.battling else Enemy("", 0, 0, 0, 0, 0)
        damage, killed = character.flee(enemy)

        if killed:
            character.die()
            await ctx.message.reply(
                f"**{character.name}** was killed fleeing the {enemy.name}, and is no more. Rest in peace, brave adventurer."
            )
        elif damage:
            await ctx.message.reply(
                f"**{character.name}** flees the {enemy.name}, taking {damage} damage. HP: {character.hp}/{character.max_hp}"
            )
        else:
            await ctx.message.reply(
                f"**{character.name}** flees the {enemy.name} with their life but not their dignity intact. HP: {character.hp}/{character.max_hp}"
            )

    @commands.command(name="hunt", help="Look for an enemy to fight.")
    async def hunt(self, ctx):
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

        enemy = character.hunt()

        # Send reply
        await ctx.message.reply(
            f"You encounter a {enemy.name}. Do you `!fight` or `!flee`?"
        )


async def setup(bot):
    await bot.add_cog(Combat(bot))
