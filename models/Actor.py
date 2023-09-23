import random


class Actor:
    def __init__(
        self,
        name: str,
        hp: int,
        max_hp: int,
        attack: int,
        defense: int,
        xp: int,
        gold: int,
    ):
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
            damage = random.randint(
                self.attack - 1 if self.attack > 0 else 0, self.attack + 1
            )
        else:
            damage = 0

        other.hp -= damage

        return (damage, other.hp <= 0)  # (damage, fatal)
