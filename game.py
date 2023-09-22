import enum
import random
import sys
from copy import deepcopy

from db_conection import *


# Helper functions
def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


# Game Modes
class GameMode(enum.IntEnum):
    ADVENTURE = 1
    BATTLE = 2


# Living creatures
class Actor:
    def __init__(self, name, hp, max_hp, attack, defense, xp, gold):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.xp = xp
        self.gold = gold

    def fight(self, other):
        defense = min(other.defense, 19)  # cap defense value
        chance_to_hit = random.randint(0, 20 - defense)

        if chance_to_hit:
            damage = self.attack
        else:
            damage = 0

        other.hp -= damage

        return (self.attack, other.hp <= 0)  # (damage, fatal)


class Character(Actor):
    level_cap = 10

    def __init__(
        self,
        name,
        hp,
        max_hp,
        attack,
        defense,
        mana,
        level,
        xp,
        gold,
        inventory,
        mode,
        battling,
        user_id,
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
            characters.insert_one(
                {"_id": self.user_id, "character": character_dict}
            )

    def fight(self, enemy):
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

    def flee(self, enemy):
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

    def defeat(self, enemy):
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


class Enemy(Actor):
    def __init__(self, name, max_hp, attack, defense, xp, gold):
        super().__init__(name, max_hp, max_hp, attack, defense, xp, gold)
        self.enemy = self.__class__.__name__

    def rehydrate(self, name, hp, max_hp, attack, defense, xp, gold, enemy):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.xp = xp
        self.gold = gold


class GiantRat(Enemy):
    min_level = 1

    def __init__(self):
        super().__init__("🐀 Giant Rat", 2, 1, 1, 1, 1)  # HP, attack, defense, XP, gold


class GiantSpider(Enemy):
    min_level = 1

    def __init__(self):
        super().__init__(
            "🕷️ Giant Spider", 3, 2, 1, 1, 2
        )  # HP, attack, defense, XP, gold


class Bat(Enemy):
    min_level = 1

    def __init__(self):
        super().__init__("🦇 Bat", 4, 2, 1, 2, 1)  # HP, attack, defense, XP, gold


class Crocodile(Enemy):
    min_level = 2

    def __init__(self):
        super().__init__("🐊 Crocodile", 5, 3, 1, 2, 2)  # HP, attack, defense, XP, gold


class Wolf(Enemy):
    min_level = 2

    def __init__(self):
        super().__init__("🐺 Wolf", 6, 3, 2, 2, 2)  # HP, attack, defense, XP, gold


class Poodle(Enemy):
    min_level = 3

    def __init__(self):
        super().__init__("🐩 Poodle", 7, 4, 1, 3, 3)  # HP, attack, defense, XP, gold


class Snake(Enemy):
    min_level = 3

    def __init__(self):
        super().__init__("🐍 Snake", 8, 4, 2, 3, 3)  # HP, attack, defense, XP, gold


class Lion(Enemy):
    min_level = 4

    def __init__(self):
        super().__init__("🦁 Lion", 9, 5, 1, 4, 4)  # HP, attack, defense, XP, gold


class Dragon(Enemy):
    min_level = 5

    def __init__(self):
        super().__init__("🐉 Dragon", 10, 6, 2, 5, 5)  # HP, attack, defense, XP, gold
