import discord
from Sobek import Sobek


class S:  # short for status,stores stats
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    DamageTakenMultiplier: int
    DamageDealtMultiplier: int
    abilityCooldowns: [int]
    bleedAmount: int
    bleedTimer: int

    def __init__(self, PosX: int, PosY: int):
        self.posX = PosX
        self.posY = PosY
        self.DamageTakenMultiplier = 1
        self.DamageDealtMultiplier = 1
        for i in range(5):
            self.abilityCooldowns.append(0)
        for i in range(len(self.abilityCooldowns)):
            print(self.abilityCooldowns[i])


class player:
    s = S
    member: discord.Member
    hero = None

    def __init__(self, x, y, member, heroName):
        self.s = S(x, y)
        self.member = member
        dict = {
            "Sobek": Sobek,
        }
        self.hero = dict[heroName](player=self)

    def moveTo(self, x, y):
        self.s.posX = x
        self.s.posY = y

    def TakeDamage(self, amount: int):
        self.s.currentHP -= amount

    def PrintStatus(self):
        return "position:(" + str(self.s.posX) + ", " + str(self.s.posY) + ") \r HP: " + str(self.s.maxHP) + "/" + str(
            self.s.currentHP)
