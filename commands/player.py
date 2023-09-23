from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from connection import characters
from functions import load_character
from helpers import GameMode
from models import Character


async def create_new_player(interaction: discord.Interaction, name=None, vocation=""):
    user_id = interaction.user.id

    # if no name is specified, use the creator's nickname
    if not name:
        name = interaction.user.name

    if vocation == "Guerrero":
        hp = 16
        mana = 6
        attack = 2
        defense = 2
    elif vocation == "Mago":
        hp = 10
        mana = 15
        attack = 3
        defense = 1
    else:
        hp = 10
        mana = 10
        attack = 1
        defense = 1

    character = Character(
        **{
            "name": name,
            "vocation": vocation,
            "hp": hp,
            "max_hp": hp,
            "attack": attack,
            "defense": defense,
            "mana": mana,
            "max_mana": mana,
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


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="crear", description="Crear un nuevo personaje")
    @app_commands.choices(
        vocacion=[
            app_commands.Choice(name="Guerrero", value="guerrero"),
            app_commands.Choice(name="Mago", value="mago"),
        ]
    )
    async def crear(
        self,
        interaction: discord.Interaction,
        name: Optional[str],
        vocacion: app_commands.Choice[str],
    ):
        await interaction.response.defer()

        user_id = interaction.user.id

        # if no name is specified, use the creator's nickname
        if not name:
            name = interaction.user.name

        # only create a new character if the user does not already have one
        if not characters.count_documents({"_id": user_id}):
            await create_new_player(interaction, name, vocacion.name)

            await interaction.followup.send(
                f"Nuevo _{vocacion.value}_ nivel 1 creado: **{name}**. Entra a `/status` para ver tus estadísticas"
            )
        else:
            await interaction.followup.send("Ya tienes a un personaje creado")

    @app_commands.command(name="morir", description="Asesinar a su personaje actual")
    async def morir(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id

        if not characters.count_documents({"_id": user_id}):
            await interaction.followup.send(
                "No tienes personaje, primero debes de crear uno con `/crear`"
            )
            return

        character = load_character(user_id)

        character.die()

        await interaction.followup.send(
            f"El personaje **{character.name}** ha sido eliminado. Crea uno nuevo con `/crear`"
        )

    @app_commands.command(
        name="levelup",
        description="Avanza al siguiente nivel. Especifica la estadística a incrementar",
    )
    @app_commands.choices(
        increase=[
            app_commands.Choice(name="Ataque", value="attack"),
            app_commands.Choice(name="Defensa", value="defense"),
            app_commands.Choice(name="Hp", value="max_hp"),
            app_commands.Choice(name="Mana", value="max_mana"),
        ],
    )
    async def levelup(
        self, interaction: discord.Interaction, increase: app_commands.Choice[str]
    ):
        await interaction.response.defer()
        user_id = interaction.user.id

        if not characters.count_documents({"_id": user_id}):
            await interaction.followup.send(
                "No tienes personaje, primero debes de crear uno con `/crear`"
            )
            return

        character = load_character(user_id)

        if character.mode != GameMode.ADVENTURE:
            await interaction.followup.send(
                "Solo puedes usar este comando fuera de una batalla!"
            )
            return

        ready, xp_needed = character.ready_to_level_up()
        if not ready:
            await interaction.followup.send(
                f"Necesitas {xp_needed} para subir al nivel {character.level+1}"
            )
            return

        success, new_level = character.level_up(increase.value)
        if success:
            await interaction.followup.send(
                f"**{character.name}** subió al nivel {new_level}, ganando 1 punto de {increase.name.upper()}."
            )
        else:
            await interaction.followup.send(f"**{character.name}** failed to level up.")

    @app_commands.command(
        name="reset", description="[DEV] Destruir y crear de nuevo el personaje actual"
    )
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = interaction.user.id

        if not characters.count_documents({"_id": user_id}):
            await interaction.followup.send(
                "No tienes personaje, primero debes de crear uno con `/crear`"
            )
            return
        character = load_character(user_id)
        name, vocation = character.name, character.vocation
        characters.delete_one({"_id": user_id})

        await interaction.followup.send(f"Personaje borrado")

        await create_new_player(interaction, name, vocation)
        await interaction.channel.send(  # type: ignore
            content=f"Nuevo _{vocation.lower()}_ nivel 1 creado: **{name}**. Entra a `/status` para ver tus estadísticas"
        )


async def setup(bot):
    await bot.add_cog(Player(bot))
