class SS:  # short for statusScript,stores stats
    maxHP: int
    currentHP: int
    posX: int
    posY: int

    def __init__(self, MaxHP, PosX, PosY):
        self.maxHP = MaxHP
        self.posX = PosX
        self.posY = PosY


class player:
    ss = SS

    def __init__(self, maxHP, x, y):
        self.ss = SS(maxHP, x, y)

    def moveTo(self, x, y):
        self.ss.posX = x
        self.ss.posY = y

    def PrintPos(self):
        return str(self.ss.posX) + ", " + str(self.ss.posY)
