from connection import characters
from models import Character


def load_character(user_id: str) -> Character:
    return Character(**list(characters.find({"_id": user_id}))[0]["character"])
