import enum


class GameMode(enum.IntEnum):
    ADVENTURE = 1
    BATTLE = 2


MODE_COLOR = {
    GameMode.BATTLE: 0xDC143C,
    GameMode.ADVENTURE: 0x005EB8,
}
