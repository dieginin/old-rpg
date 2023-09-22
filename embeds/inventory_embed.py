import discord

from models import Character


def inventory_embed(ctx, character: Character):
    # Create embed with invenory description
    embed = discord.Embed(
        title=f"**{character.name}** Inventory",
        color=discord.Color.random(),
    )
    embed.set_author(name=ctx.author.display_name)

    # Inventory field
    inventory_text = f"Gold: {character.gold}\n"
    if character.inventory:
        inventory_text += "\n".join(character.inventory)

    embed.add_field(name="Inventory", value=inventory_text)

    return embed
