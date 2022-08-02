import discord

class S:  # short for status,stores stats
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    DamageTakenMultiplier:int
    DamageDealtMultiplier:int

    def __init__(self, MaxHP, PosX, PosY):
        self.maxHP = MaxHP
        self.currentHP=MaxHP
        self.posX = PosX
        self.posY = PosY
        self.DamageTakenMultiplier=1
        self.DamageDealtMultiplier=1


class player:
    s = S
    member: discord.Member
    def __init__(self, maxHP, x, y, member):
        self.s = S(maxHP, x, y)
        self.member = member

    def moveTo(self, x, y):
        self.s.posX = x
        self.s.posY = y

    def PrintPos(self):
        return "position:("+str(self.s.posX) + ", " + str(self.s.posY)+") \r HP: "+str(self.s.maxHP)+"/"+str(self.s.currentHP)
