import random
from copy import deepcopy
from typing import List

from connection import characters
from functions import str_to_class
from helpers import GameMode
from models import Actor, Enemy


class Character(Actor):
    level_cap = 10

    def __init__(
        self,
        name: str,
        hp: int,
        max_hp: int,
        attack: int,
        defense: int,
        mana: int,
        level: int,
        xp: int,
        gold: int,
        inventory: List,
        mode: GameMode,
        battling,
        user_id: int,
    ):
        super().__init__(name, hp, max_hp, attack, defense, xp, gold)
        self.level = level
        self.mana = mana

        self.inventory = inventory

        self.mode = mode
        if battling != None:
            enemy_class = str_to_class(battling["enemy"])
            self.battling = enemy_class()
            self.battling.rehydrate(**battling)
        else:
            self.battling = None
        self.user_id = user_id

    def _in_db(self):
        return characters.count_documents({"_id": self.user_id})

    def save_to_db(self):
        character_dict = deepcopy(vars(self))

        if self.battling != None:
            character_dict["battling"] = deepcopy(vars(self.battling))

        if self._in_db():
            characters.find_one_and_update(
                {"_id": self.user_id}, {"$set": {"character": character_dict}}
            )
        else:
            characters.insert_one({"_id": self.user_id, "character": character_dict})

    def fight(self, enemy: Enemy):
        outcome = super().fight(enemy)

        # Save changes to DB after state change
        self.save_to_db()

        return outcome

    def hunt(self):
        # Generate random enemy to fight
        while True:
            enemy_type = random.choice(Enemy.__subclasses__())

            if enemy_type.min_level <= self.level:  # type: ignore
                break

        enemy = enemy_type()  # type: ignore

        # Enter battle mode
        self.mode = GameMode.BATTLE
        self.battling = enemy

        # Save changes to DB after state change
        self.save_to_db()

        return enemy

    def flee(self, enemy: Enemy):
        if random.randint(0, 1 + self.defense):  # flee unscathed
            damage = 0
        else:  # take damage
            damage = enemy.attack / 2
            self.hp -= damage

        # Exit battle mode
        self.battling = None
        self.mode = GameMode.ADVENTURE

        # Save to DB after state change
        self.save_to_db()

        return (damage, self.hp <= 0)  # (damage, killed)

    def defeat(self, enemy: Enemy):
        if self.level < self.level_cap:  # no more XP after hitting level cap
            self.xp += enemy.xp

        self.gold += enemy.gold  # loot enemy

        # Exit battle mode
        self.battling = None
        self.mode = GameMode.ADVENTURE

        # Check if ready to level up after earning XP
        ready, _ = self.ready_to_level_up()

        # Save to DB after state change
        self.save_to_db()

        return (enemy.xp, enemy.gold, ready)

    def ready_to_level_up(self):
        if self.level == self.level_cap:  # zero values if we've ready the level cap
            return (False, 0)

        xp_needed = (self.level) * 10
        return (self.xp >= xp_needed, xp_needed - self.xp)  # (ready, XP needed)

    def level_up(self, increase):
        ready, _ = self.ready_to_level_up()
        if not ready:
            return (False, self.level)  # (not leveled up, current level)

        self.level += 1  # increase level
        setattr(self, increase, getattr(self, increase) + 1)  # increase chosen stat

        self.hp = self.max_hp  # refill HP

        # Save to DB after state change
        self.save_to_db()

        return (True, self.level)  # (leveled up, new level)

    def die(self):
        if self._in_db():
            characters.delete_one({"_id": self.user_id})
