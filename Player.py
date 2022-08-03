import discord
import os

from PIL import Image

from game import Game
from imageActions import crop_points


class S:  # short for status,stores stats
    team: int
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    DamageTakenMultiplier: int
    DamageDealtMultiplier: int
    abilityCooldowns: [int]
    statusEffects: dict = {}

    def __init__(self, PosX: int, PosY: int, Team):
        self.posX = PosX
        self.posY = PosY
        team = Team
        self.DamageTakenMultiplier = 1
        self.DamageDealtMultiplier = 1
        self.abilityCooldowns = []
        for i in range(5):
            self.abilityCooldowns.append(0)


class player:
    s = S
    member: discord.Member
    hero = None
    myGame: Game = None

    def __init__(self, x, y, heroName, myGame, team):
        self.s = S(x, y, team)
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
        myPlayer: player = None
        image: Image
        maxHP: int = 3000

        def __init__(self, plyer):
            self.myPlayer = plyer
            self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek.png")
            self.image = crop_points(self.image, [9, 165, 309, 465])
            self.myPlayer.s.maxHP = self.maxHP
            self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

        def a1(self, target: player):
            target.TakeDamage(100)
            if not "bleed" in target.s:
                target.s.statusEffects['bleed':0]
                target.s.statusEffects['bleedTimer':0]
            target.s.statusEffects[
                'bleed'] += 100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
            target.s.statusEffects['bleed'] *= 2
            target.s.statusEffects['bleedTimer'] = 2

        def a2Possible(self, target: player):
            for i in range(3):
                for j in range(3):
                    if self.myPlayer.myGame.zones[i][j].isOccupied() and "bleed" in self.myPlayer.myGame.zones[i][
                        j].myPlayer.s.statusEffects:
                        return True
            return False

        def a2(self, x: int, y: int):
            if not self.myPlayer.myGame.zones[x][y].isOccupied():
                self.myPlayer.moveTo(x, y)
            for i in range(3):
                for j in range(3):
                    if self.myPlayer.myGame.zones[i][j].isOccupied() and self.myPlayer.myGame.zones[i][
                        j].myPlayer.s.team != self.myPlayer.s.team and 'bleed' in self.myPlayer.myGame.zones[i][
                        j].myPlayer.s.statusEffects:
                        self.myPlayer.myGame.zones[i][j].myPlayer.s.statusEffects['bleedTimer'] = 2

        def a3(self, target: player):
            dmgmult = 1
            if "bleed" in target.s:
                dmgmult = 2
            else:
                target.s.statusEffects['bleed':0]
                target.s.statusEffects['bleedTimer':0]
            target.TakeDamage(200 * dmgmult)
            target.s.statusEffects[
                'bleed'] += 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier
            target.s.statusEffects['bleedTimer'] = 2

        def ult(self, target: player):
            if "bleed" in target.s.statusEffects:
                bonus = target.s.statusEffects['bleed']
                target.TakeDamage(bonus * self.myPlayer.s.DamageDealtMultiplier)

    def __init__(self, heroName: str):
        self.heroName = heroName
        self.heroObject = exec(str("Hero." + heroName))
