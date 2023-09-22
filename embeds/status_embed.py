import discord

from helpers import *


def status_embed(ctx, character) -> discord.Embed:
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
