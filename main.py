import discord
from discord.ext import commands

from config import DISCORD_TOKEN
from db_conection import *
from game import *

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Helper functions
def load_character(user_id):
    return Character(**list(characters.find({"_id": user_id}))[0]["character"])


MODE_COLOR = {
    GameMode.BATTLE: 0xDC143C,
    GameMode.ADVENTURE: 0x005EB8,
}


def status_embed(ctx, character):
    mode_text = ""

    # Current mode
    if character.mode == GameMode.BATTLE:
        mode_text = f"Currently battling a {character.battling.name}."
    elif character.mode == GameMode.ADVENTURE:
        mode_text = "Currently adventuring."

    # Create embed with description as current mode
    embed = discord.Embed(
        title=f"**{character.name}** status",
        description=mode_text,
        color=MODE_COLOR[character.mode],
    )
    embed.set_author(name=ctx.author.display_name)

    # Stats field
    _, xp_needed = character.ready_to_level_up()

    embed.add_field(
        name="Stats",
        value=f"""
**HP:**    {character.hp}/{character.max_hp}
**ATTACK:**   {character.attack}
**DEFENSE:**   {character.defense}
**MANA:**  {character.mana}
**LEVEL:** {character.level}
**XP:**    {character.xp}/{character.xp+xp_needed}
    """,
        inline=True,
    )

    # Inventory field
    inventory_text = f"Gold: {character.gold}\n"
    if character.inventory:
        inventory_text += "\n".join(character.inventory)

    embed.add_field(name="Inventory", value=inventory_text, inline=True)

    return embed


# Commands
@bot.command(name="create", help="Create a character.")
async def create(ctx, name=None):
    user_id = ctx.message.author.id

    # if no name is specified, use the creator's nickname
    if not name:
        name = ctx.message.author.name

    # only create a new character if the user does not already have one
    if not characters.count_documents({"_id": user_id}):
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


@bot.command(name="status", help="Get information about your character.")
async def status(ctx):
    user_id = ctx.message.author.id

    if not characters.count_documents({"_id": user_id}):
        await ctx.message.reply(
            f"You have no charatacter, first you need to create one with `!create`."
        )
        return

    character = load_character(user_id)

    embed = status_embed(ctx, character)
    await ctx.message.reply(embed=embed)


@bot.command(name="hunt", help="Look for an enemy to fight.")
async def hunt(ctx):
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


@bot.command(name="fight", help="Fight the current enemy.")
async def fight(ctx):
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
    enemy = character.battling if character.battling else Enemy("", "", "", "", "", "")

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


@bot.command(name="flee", help="Flee the current enemy.")
async def flee(ctx):
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

    enemy = character.battling if character.battling else Enemy("", "", "", "", "", "")
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


@bot.command(
    name="levelup",
    help="Advance to the next level. Specify a stat to increase (HP, ATTACK, DEFENSE).",
)
async def levelup(ctx, increase=None):
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


@bot.command(name="die", help="Destroy current character.")
async def die(ctx):
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


@bot.command(name="reset", help="[DEV] Destroy and recreate current character.")
async def reset(ctx):
    user_id = ctx.message.author.id

    if not characters.count_documents({"_id": user_id}):
        await ctx.message.reply(
            f"You have no charatacter, first you need to create one with `!create`."
        )
        return

    characters.delete_one({"_id": user_id})

    await ctx.message.reply(f"Character deleted.")
    await create(ctx)


@bot.event
async def on_ready():
    print(f"{bot.user} connected to Discord!")


bot.run(f"{DISCORD_TOKEN}")
