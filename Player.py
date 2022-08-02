class SS:  # short for statusScript,stores stats
    maxHP: int
    currentHP: int
    posX: int
    posY: int

    def __init__(self, MaxHP, PosX, PosY):
        self.maxHP = MaxHP
        self.posX = PosX
        self.posY = PosY

    def GetMaxHP(self):
        return self.maxHP
