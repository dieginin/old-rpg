from models import Actor


class Enemy(Actor):
    def __init__(
        self, name: str, max_hp: int, attack: int, defense: int, xp: int, gold: int
    ):
        super().__init__(name, max_hp, max_hp, attack, defense, xp, gold)
        self.enemy = self.__class__.__name__

    def rehydrate(
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
