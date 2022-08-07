import discord
import os

from PIL import Image

import zone
from imageActions import crop_points

import random


class S:  # short for status,stores stats
    team: int
    maxHP: int
    currentHP: int
    posX: int
    posY: int
    movementSpeed: int
    DamageTakenMultiplier: float
    DamageDealtMultiplier: float
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
        self.currentHP = 0
        self.maxHP = 0
        self.abilityCooldowns = []
        self.dead = False
        self.statusEffects = {}
        for i in range(5):
            self.abilityCooldowns.append(0)


class player:
    s = S
    member: discord.Member
    hero = None
    myGame = None  # Game, cannot import because of circular dependency

    def __init__(self, x, y, member, heroName, myGame, team):
        self.s = S(x, y, team)
        self.hero = hero(heroName, self)
        self.myGame = myGame
        self.member = member
        self.dead = False

    def moveTo(self, x, y):
        self.myGame.zones[self.s.posX][self.s.posY].myPlayer = None
        self.s.posX = x
        self.s.posY = y
        self.myGame.zones[self.s.posX][self.s.posY].myPlayer = self

    async def TakeDamage(self, amount: int):
        self.s.currentHP -= int(amount * self.s.DamageTakenMultiplier)
        if self.s.currentHP <= 0:
            self.s.currentHP = 0
            self.dead = True
            await self.myGame.killPlayer(self)

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
        enemyZones = []
        for i in range(self.s.posX - self.s.movementSpeed, self.s.posX + self.s.movementSpeed + 1):
            for j in range(self.s.posY - self.s.movementSpeed, self.s.posY + self.s.movementSpeed + 1):
                if 0 <= i < self.myGame.lengthX and 0 <= j < self.myGame.lengthY:
                    if not zones[i][j].isOccupied():
                        canMove.append((i + 1, j + 1))
                    else:
                        if zones[i][j].myPlayer != self:
                            enemyZones.append((i + 1, j + 1))
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

    async def executeEffects(self, effectName, amount):
        if effectName == "bleed":
            await self.TakeDamage(amount)
            return self.hero.heroName.upper() + " bled out and took " + str(amount) + " damage! \n" \
                                                                                      "Current HP: " + str(
                self.s.currentHP)

    async def usableOutOfCombatAbilities(self):
        outOfCombatAbilities = []
        for ability in self.hero.heroObject.moveList:
            if self.hero.heroObject.moveList[ability]['abilityType'] == "outOfCombat":
                outOfCombatAbilities.append(ability)
        for ability in outOfCombatAbilities:
            if self.hero.heroObject.coolDowns[ability] != 0:
                outOfCombatAbilities.remove(ability)
            canUse = getattr(self.hero.heroObject, ability + "Possible")
            if not canUse():
                outOfCombatAbilities.remove(ability)

        return outOfCombatAbilities


class Sobek:
    myPlayer: player = None
    image: Image
    maxHP: int = 3000
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 5}
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 2, "abilityName": "Bleeding Strike"
        , "abilityDesc": "Sobek Strikes his enemy, dealing 100 DAMAGE, refreshing BLEED's Duration on the target, "
                         "and applying BLEED according to damage dealt. After that, DOUBLE the target's BLEED amount.",
                       "actionLine": "SOBEK Strikes! It deals {damageDealt} to {target}! {target} now BLEEDS for {bleed}!"},
                "a2": {"abilityType": "outOfCombat", "maxCooldown": 4, "abilityName": "Hunter's Chase'",
                       "abilityDesc": "Dash 2 tiles. After that, refresh BLEED's Duration on all enemies in a 3x3 area",
                       "actionLine": "SOBEK dashes! {target} now BLEEDS for {bleed}!"}
        , "a3": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Open Wounds",
                 "abilityDesc": "Sobek strikes the enemy, dealing 200 DAMAGE, and applying BLEED to the target. If the "
                                "target is already BLEEDING, the damage is doubled.",
                 "actionLine": "SOBEK Opens {target}'s wounds! {target} now BLEEDS for {bleed}! {damageDealt} dealt! "
                               "{additionalText}"}
        , "ult": {"abilityType": "inCombat", "maxCooldown": 10, "abilityName": "Sobek's Rage",
                  "abilityDesc": "Sobek Strikes the enemy with all of his RAGE, dealing the amount of BLEED stacks on the enemy.",
                  "actionLine": "SOBEK destroys the enemy with all of his RAGE! It deals {damageDealt} to {target}!"}}
    playStyle = "Sobek is a well trained fighter, causing enemies to BLEED being his main power source. You have to " \
                "play aggressively and cause your enemies to BLEED if you want to win. "

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 3000
        self.coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 5}
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

    async def a1(self, target: player):
        await target.TakeDamage(100 * self.myPlayer.s.DamageDealtMultiplier)
        if "bleed" not in target.s.statusEffects:
            target.s.statusEffects["bleed"] = {}
            target.s.statusEffects["bleed"]['amount'] = 0
        target.s.statusEffects[
            'bleed']['amount'] += 100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
        target.s.statusEffects['bleed']['amount'] *= 2
        target.s.statusEffects['bleed']['bleedTimer'] = 2
        return {"damageDealt": 100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
            , "target": target.member.display_name, "bleed": target.s.statusEffects['bleed']['amount']}

    def a2Possible(self):
        return True

    def a2(self, x: int, y: int):
        if not self.myPlayer.myGame.zones[x][y].isOccupied():
            self.myPlayer.moveTo(x, y)
        for i in range(3):
            for j in range(3):
                if self.myPlayer.myGame.zones[i][j].isOccupied() and self.myPlayer.myGame.zones[i][
                    j].myPlayer.s.team != self.myPlayer.s.team and 'bleed' in self.myPlayer.myGame.zones[i][
                    j].myPlayer.s.statusEffects:
                    self.myPlayer.myGame.zones[i][j].myPlayer.s.statusEffects['bleedTimer'] = 2

    async def a3(self, target: player):
        dmgmult = 1
        if "bleed" in target.s.statusEffects:
            dmgmult = 2
        else:
            target.s.statusEffects['bleed'] = {}
            target.s.statusEffects['bleed']['amount'] = 0
        await target.TakeDamage(200 * dmgmult)
        target.s.statusEffects[
            'bleed']['amount'] += 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier
        target.s.statusEffects['bleed']['bleedTimer'] = 2
        if dmgmult == 2:
            return {
                "damageDealt": 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier
                , "target": target.member.display_name, "bleed": target.s.statusEffects['bleed']['amount'],
                "additionalText": "The target was already BLEEDING!"
                                  " The damage is doubled!"}
        return {
            "damageDealt": 200 * target.s.DamageTakenMultiplier * dmgmult * self.myPlayer.s.DamageDealtMultiplier,
            "target": target.member.display_name, "bleed": target.s.statusEffects['bleed']['amount'],
            "additionalText": "SOBEK didnt fully "
                              "utilize his power!"}

    async def ult(self, target: player):
        bonus = 0
        if "bleed" in target.s.statusEffects:
            bonus = target.s.statusEffects['bleed']['amount']
            await target.TakeDamage(bonus * self.myPlayer.s.DamageDealtMultiplier)
        return {"damageDealt": bonus * self.myPlayer.s.DamageDealtMultiplier, "target": target.member.display_name}


class Horus:
    myPlayer: player = None
    image: Image
    maxHP: int = 3000
    SandStacks: int = 1
    SandSoldierList = None
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 5}
    moveList = {"a1": {"abilityType": "outOfCombat", "maxCooldown": 2, "abilityName": "Arise!"
        , "abilityDesc": "Horus summons 2 sand soldiers at random areas across the map.",
                       "actionLine": "change this when it works"},
                "a2": {"abilityType": "inCombat", "maxCooldown": 4, "abilityName": "Conquering Sands",
                       "abilityDesc": "Horus challenges the enemy, granting him a stack of sand soldiers and increases the damage the enemy takes by 10% permanently!",
                       "actionLine": "Horus challenged {target}. {target} is Vulnerable!"}
        , "a3": {"abilityType": "outOfCombat", "maxCooldown": 0, "abilityName": "Shifting Sands",
                 "abilityDesc": "Horus consumes a stack of his sand soldiers to Dash the amount of sand soldiers on the field. then leaves a sand soldier in his original position!",
                 "actionLine": "change this when it works"}
        , "ult": {"abilityType": "outOfCombat", "maxCooldown": 5, "abilityName": "Emperor's Divide",
                  "abilityDesc": "Horus imbues all current soldiers with power, granting them 5x damage and 1000 bonus max health.",
                  "actionLine": "change this when it works"}}
    playStyle = "Horus is the emperor of the sands. Horus summons sand soldiers to find for him, and challenges his opponent to increase his damage. play around your soldiers to control the field and win" \

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 3000
        self.coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 5}
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Horus_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP
        self.SandSoldierList = []

    def p(self, x: int, y: int):
        if self.myPlayer.myGame.zones[x][y].isOccupied() or self.myPlayer.myGame.zones[x][y].myEvent is not None:
            x = random.randint(0, self.myPlayer.myGame.lengthX - 1)
            y = random.randint(0, self.myPlayer.myGame.lengthY - 1)
            self.p(x, y)
        else:
            self.SandSoldierList.append(SandSoldier())

    def a1Possible(self):
        return self.SandStacks > 0

    async def a1(self):
        self.SandStacks -= 1
        for i in range(2):
            x = random.randint(0, self.myPlayer.myGame.lengthX - 1)
            y = random.randint(0, self.myPlayer.myGame.lengthY - 1)
            self.p(x, y)

    def a2(self, target: player):
        target.s.DamageTakenMultiplier += 0.1
        self.SandStacks += 1
        return {"target":target.hero.heroName}

    def a3Possible(self):
        return len(self.SandSoldierList)

    def a3(self):
        pass

    def ultPossible(self):
        return len(self.SandSoldierList)>0

    def ult(self):
        for soldier in len(self.SandSoldierList):
            soldier.myPlayer.s.DamageDealtMultiplier += 5
            soldier.myPlayer.s.maxHP += 1000
            soldier.myPlayer.s.currentHP += 1000


class SandSoldier:
    myPlayer: player = None
    image: Image
    maxHP: int = 500
    coolDowns = {"a1"}
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Solar Strike",
                       "abilityDesc": "Ra commands the sun to fire at his enemy, dealing 50 DAMAGE. if Ra has 5 or "
                                      "more SunLight, the beam will deal an additional 150 damage. ",
                       "actionLine": "Ra Fires! It deals {damageDealt} to {target}!""{additionalText}"}}

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 500
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\SandSoldier_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

    async def a1(self, target: player):
        await target.TakeDamage(150 * self.myPlayer.s.DamageDealtMultiplier)
        return 150 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier


class Ra:
    myPlayer: player = None
    image: Image
    maxHP: int = 3500
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 9999}
    SunOrbs: int = 0
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Solar Strike",
                       "abilityDesc": "Ra commands the sun to fire at his enemy, dealing 50 DAMAGE. if Ra has 5 or "
                                      "more SunLight, the beam will deal an additional 150 damage. ",
                       "actionLine": "Ra Fires! It deals {damageDealt} to {target}!""{additionalText}"},
                "a2": {"abilityType": "inCombat", "maxCooldown": 6, "abilityName": "Sun Light's Guard",
                       "abilityDesc": "Reduces my damage taken by 10 for each stack of Sun Light. cooldown is reduced by 1 whenever Ra picks "
                                      "a sunMorb",
                       "actionLine": "the sun surrounds Ra, granting him {amount} damage reduction!"}
        , "a3": {"abilityType": "outOfCombat", "maxCooldown": 2, "abilityName": "Advanced Maneuver",
                 "abilityDesc": "Ra utlizes his full potentional for 1 turn, gaining 1 bonus move range for each "
                                "stack of his SunLight",
                 "actionLine": "Ra Spreads wings made from SunLight, gaining {damageDealt} dealt! "}
        , "ult": {"abilityType": "inCombat", "maxCooldown": 2, "abilityName": "Sun Gods Searing Wrath",
                  "abilityDesc": "Ra channels the full power of the sun, dealing 2000 damage and healing himself for "
                                 "the damage dealt",
                  "actionLine": "Ra obliterates {target}! It deals {damageDealt} and heals Ra for {damageDealt}"}}
    playStyle = "Ra is the Sun God, by collecting sun orbs he can ascend to his full potentional, dealing incredible " \
                "damage with very strong tools be sure to collect your orbs before your enemy destroys them to gain power and win the game!"

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 3500
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Ra_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

    def p(self):
        x = random.randint(0, self.myPlayer.myGame.lengthX - 1)
        y = random.randint(0, self.myPlayer.myGame.lengthY - 1)
        if self.myPlayer.myGame.zones[x][y].isOccupied() or self.myPlayer.myGame.zones[x][y].myEvent is not None:
            self.p()
        else:
            zone.event("sunOrb", self.myPlayer.myGame.zones[x, y], self.myPlayer.myGame, x, y)

    async def a1(self, target: player):
        damagedealt = 0
        await target.TakeDamage(50 * self.myPlayer.s.DamageDealtMultiplier)
        damagedealt += 50 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
        if self.SunOrbs >= 5:
            await target.TakeDamage(150 * self.myPlayer.s.DamageDealtMultiplier)
            damagedealt += 150 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
        return {"damageDealt": int(damagedealt)}

    async def a2(self, target: player):
        self.myPlayer.s.DamageTakenMultiplier -= self.SunOrbs * 0.1
        return {"amount": self.SunOrbs * 10}

    def a3Possible(self):
        return self.SunOrbs > 0

    def a3(self):
        self.myPlayer.s.movementSpeed += self.SunOrbs
        return {"damageDealt": self.SunOrbs}

    async def ult(self, target: player):
        await target.TakeDamage(2000 * self.myPlayer.s.DamageDealtMultiplier)
        self.myPlayer.s.currentHP = max(
            min(self.myPlayer.s.currentHP + 2000 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier,
                self.myPlayer.s.maxHP), self.myPlayer.s.currentHP)
        return {"damageDealt": int(2000 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier)}


class hero:
    heroName: str
    heroObject = None

    def __init__(self, heroName: str, plyer: player):
        self.heroName = heroName
        heroObjects = {
            "Sobek": Sobek,
            "Ra": Ra,
            "Horus": Horus
        }
        self.heroObject = heroObjects[heroName](plyer)
        plyer.s.maxHP = self.heroObject.maxHP
        plyer.s.currentHP = self.heroObject.maxHP
