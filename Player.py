class S:  # short for status,stores stats
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    DamageTakenMultiplier: int
    DamageDealtMultiplier: int

    def __init__(self, MaxHP, PosX, PosY):
        self.maxHP = MaxHP
        self.currentHP = MaxHP
        self.posX = PosX
        self.posY = PosY
        self.DamageTakenMultiplier = 1
        self.DamageDealtMultiplier = 1


class player:
    s = S

    def __init__(self, maxHP, x, y):
        self.s = S(maxHP, x, y)

    def moveTo(self, x, y):
        self.s.posX = x
        self.s.posY = y

    def TakeDamage(self,amount:int):
        self.s.currentHP-=amount

    def PrintStatus(self):
        return "position:(" + str(self.s.posX) + ", " + str(self.s.posY) + ") \r HP: " + str(self.s.maxHP) + "/" + str(
            self.s.currentHP)
