import discord
from Sobek import Sobek

from PIL import Image
from imageActions import crop_points

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
    myGame = None

    def __init__(self, x, y, member, heroName, myGame):
        self.s = S(x, y)
        self.member = member
        dict = {
            "Sobek": hero.Sobek,
        }
        self.hero = dict[heroName](player=self)
        self.myGame = myGame

    def moveTo(self, x, y):
        self.s.posX = x
        self.s.posY = y

    def TakeDamage(self, amount: int):
        self.s.currentHP -= amount * self.s.DamageTakenMultiplier

    def PrintStatus(self):
        return "position:(" + str(self.s.posX) + ", " + str(self.s.posY) + ") \r HP: " + str(self.s.maxHP) + "/" + str(
            self.s.currentHP)


class hero:
    heroName: str
    heroObject = None

    class Sobek:
        myPlayer = None
        image: Image
        maxHP: int = 3000

        def __init__(self, player):
            self.myPlayer = player
            self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek.png")
            self.image = crop_points(self.image, [9, 165, 309, 465])
            self.myPlayer.s.maxHP = self.maxHP
            self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

        def a1(self, target: player):
            target.TakeDamage(100)
            target.s.bleedAmount += 100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
            if target.s.bleedAmount > 0:
                target.s.bleedAmount *= 2
            target.s.bleedTimer = 2

        def a2Possible(self, target: player):
            for i in range(3):
                for j in range(3):
                    if not (i == 1 or j == 1):  # and grid[i,j]
                        print("")

        def a3(self, target: player):
            dmgmult = 1
            if target.s.bleedAmount > 0:
                dmgmult = 2
            target.TakeDamage(200 * dmgmult)
            target.s.bleedAmount += 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier
            target.s.bleedTimer = 2

        def ult(self, target: player):
            bonus = target.s.bleedAmount
            target.TakeDamage(bonus * self.myPlayer.s.DamageDealtMultiplier)

    def __init__(self, heroName: str):
        self.heroName = heroName
        self.heroObject = exec(str("Hero." + heroName))
