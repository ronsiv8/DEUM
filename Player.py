import discord
import os

from PIL import Image

from imageActions import crop_points


class S:  # short for status,stores stats
    team: int
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    movementSpeed: int
    DamageTakenMultiplier: int
    DamageDealtMultiplier: int
    abilityCooldowns: [int]
    statusEffects: dict = {}

    def __init__(self, PosX: int, PosY: int, Team, movementSpeed=3):
        self.posX = PosX
        self.posY = PosY
        team = Team
        self.DamageTakenMultiplier = 1
        self.DamageDealtMultiplier = 1
        self.movementSpeed = movementSpeed
        self.bleedAmount = 0
        self.bleedTimer = 0
        self.abilityCooldowns = []
        self.statusEffects = {}
        for i in range(5):
            self.abilityCooldowns.append(0)


class player:
    s = S
    member: discord.Member
    hero = None
    myGame = None # Game, cannot import because of circular dependency

    def __init__(self, x, y, member, heroName, myGame, team):
        self.s = S(x, y, team)
        dict = {
            "Sobek": hero("Sobek", self),
        }
        self.hero = dict[heroName]
        self.myGame = myGame
        self.member = member

    def moveTo(self, x, y):
        self.myGame.zones[self.s.posX][self.s.posY].myPlayer = None
        self.s.posX = x
        self.s.posY = y
        self.myGame.zones[self.s.posX][self.s.posY].myPlayer = self

    def TakeDamage(self, amount: int):
        self.s.currentHP -= amount * self.s.DamageTakenMultiplier

    def PrintStatus(self):
        return "position:(" + str(self.s.posX) + ", " + str(self.s.posY) + ") (functionally " + \
               str(self.s.posX + 1) + ", " + str(self.s.posY + 1) + ")\r HP: " + str(self.s.maxHP) + "/" + str(
            self.s.currentHP)

    def canMoveTo(self):
        """
        Returns an array of tuples with the coordinates of the tiles that the player can move to.
        """
        zones = self.myGame.zones
        canMove = []
        for i in range(self.s.posX - self.s.movementSpeed, self.s.posX + self.s.movementSpeed + 1):
            for j in range(self.s.posY - self.s.movementSpeed, self.s.posY + self.s.movementSpeed + 1):
                if 0 <= i < self.myGame.lengthX and 0 <= j < self.myGame.lengthY:
                    if not zones[i][j].isOccupied():
                        canMove.append((i + 1, j + 1))
        return canMove

    async def adjacentPlayers(self):
        """
        Returns an array of players that are adjacent to the player.
        """
        adjacentPlayers = []
        for i in range(self.s.posX - 1, self.s.posX + 2):
            for j in range(self.s.posY - 1, self.s.posY + 2):
                if 0 <= i < self.myGame.lengthX and 0 <= j < self.myGame.lengthY:
                    if self.myGame.zones[i][j].isOccupied() and self.myGame.zones[i][j].myPlayer != self:
                        adjacentPlayers.append(self.myGame.zones[i][j].myPlayer)
        return adjacentPlayers


class hero:
    heroName: str
    heroObject = None

    class Sobek:
        myPlayer: player = None
        image: Image
        maxHP: int = 3000
        moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 1}, "a2": {"abilityType": "outOfCombat",
                                                                                "maxCooldown": 3}, "a3": {
            "abilityType": "inCombat", "maxCooldown": 0}, "ult": {"abilityType": "inCombat", "maxCooldown": 10}}

        def __init__(self, plyer):
            self.myPlayer = plyer
            self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek.png")
            self.image = crop_points(self.image, [9, 165, 309, 465])
            self.myPlayer.s.maxHP = self.maxHP
            self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

        def a1(self, target: player):
            target.TakeDamage(100)
            if "bleed" not in target.s:
                target.s.statusEffects['bleed'] = 0
                target.s.statusEffects['bleedTimer'] = 0
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
                target.s.statusEffects['bleed'] = 0
                target.s.statusEffects['bleedTimer'] = 0
            target.TakeDamage(200 * dmgmult)
            target.s.statusEffects[
                'bleed'] += 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier
            target.s.statusEffects['bleedTimer'] = 2

        def ult(self, target: player):
            if "bleed" in target.s.statusEffects:
                bonus = target.s.statusEffects['bleed']
                target.TakeDamage(bonus * self.myPlayer.s.DamageDealtMultiplier)

    def __init__(self, heroName: str, player):
        self.heroName = heroName
        self.heroObject = {
            "Sobek": self.Sobek(player)
        }.get(heroName)
