import discord
import os

from PIL import Image

import zone
import imageActions as IA
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
    speedProgress = 0
    statusEffects: dict = {}

    def __init__(self, PosX: int, PosY: int, Team, movementSpeed=2):
        self.posX = PosX
        self.posY = PosY
        self.team = Team
        self.doingAbility = None
        self.DamageTakenMultiplier = 1
        self.DamageDealtMultiplier = 1
        self.movementSpeed = movementSpeed
        self.bleedAmount = 0
        self.bleedTimer = 0
        self.currentHP = 0
        self.maxHP = 0
        self.abilityCooldowns = []
        self.speedProgress = 0
        self.dead = False
        self.statusEffects = {}
        for i in range(5):
            self.abilityCooldowns.append(0)


class player:
    s = S
    member: discord.Member
    hero = None
    myGame = None  # Game, cannot import because of circular dependency
    outOfCombatNext = None
    savedMove = None

    def __init__(self, x, y, member, heroName, myGame, team):
        self.s = S(x, y, team)
        self.hero = hero(heroName, self)
        self.myGame = myGame
        self.savedMove = None
        self.member = member
        self.outOfCombatNext = None
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

    async def PrintStatus(self):
        StatString = "player " + self.hero.heroName + " from team " + str(self.s.team) + "\r position:(" + str(
            self.s.posX + 1) + ", " + str(
            self.s.posY + 1) + ")\r HP: " + str(self.s.currentHP) + "/" + str(
            self.s.maxHP) + "\rDamage Dealt multiplier:" + str(
            self.s.DamageDealtMultiplier) + "\rDamage Taken multiplier: " + str(
            self.s.DamageTakenMultiplier) + "\r"
        embed = discord.Embed()
        embed.set_thumbnail(url="attachment://hero.png")
        embed.add_field(name="stats: \r", value=StatString, inline=True)
        await self.myGame.ctx.send(embed=embed)

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
                    if not zones[i][j].isOccupied() or zones[i][j].myPlayer == self:
                        canMove.append((i + 1, j + 1))
                    else:
                        if zones[i][j].myPlayer != self:
                            enemyZones.append((i + 1, j + 1))
        return canMove

    async def adjacentEnemies(self):
        """
        Returns an array of players that are adjacent to the player.
        """
        adjacentEnemies = []
        for i in range(self.s.posX - 1, self.s.posX + 2):
            for j in range(self.s.posY - 1, self.s.posY + 2):
                if 0 <= i < self.myGame.lengthX and 0 <= j < self.myGame.lengthY:
                    if self.myGame.zones[i][j].isOccupied() and self.myGame.zones[i][j].myPlayer != self and \
                            self.myGame.zones[i][j].myPlayer.s.team != self.s.team:
                        adjacentEnemies.append(self.myGame.zones[i][j].myPlayer)
        return adjacentEnemies

    async def executeEffects(self, effectName, amount):
        if effectName == "bleed":
            await self.TakeDamage(amount)
            return self.hero.heroName.upper() + " bled out and took " + str(amount) + " damage! \n" \
                                                                                      "Current HP: " + str(
                self.s.currentHP)

    async def usableOutOfCombatAbilities(self):
        outOfCombatAbilities = []
        for ability in self.hero.heroObject.moveList:
            if self.hero.heroObject.moveList[ability]['abilityType'] == "outOfCombat" and \
                    self.hero.heroObject.coolDowns[ability] <= 0 and getattr(self.hero.heroObject,
                                                                             ability + "Possible")():
                outOfCombatAbilities.append(ability)
        return outOfCombatAbilities

    async def allOutOfCombatAbilities(self):
        """
        Returns an array of all out of combat abilities.
        """
        outOfCombatAbilities = []
        for ability in self.hero.heroObject.moveList:
            if self.hero.heroObject.moveList[ability]['abilityType'] == "outOfCombat":
                outOfCombatAbilities.append(ability)
        return outOfCombatAbilities

    async def checkProgression(self):
        if self.s.speedProgress >= 1:
            self.s.speedProgress = 0
            self.s.movementSpeed += 1
            await self.myGame.ctx.send(
                "{0}'s movement speed has increased to {1}!".format(self.hero.heroName, self.s.movementSpeed),
                delete_after=5)


class Sobek:
    myPlayer: player = None
    image: Image
    maxHP: int = 3000
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 5}
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 2, "abilityName": "Bleeding Strike"
        , "abilityDesc": "Sobek Strikes his enemy, dealing 100 DAMAGE, refreshing BLEED's Duration on the target, "
                         "and applying BLEED according to damage dealt. After that, DOUBLE the target's BLEED amount.",
                       "actionLine": "SOBEK Strikes! It deals {damageDealt} to {target}! {target} now BLEEDS for {bleed}!"},
                "a2": {"abilityType": "outOfCombat", "maxCooldown": 4, "abilityName": "Hunter's Chase",
                       "abilityDesc": "Dash 2 tiles. After that, refresh BLEED's Duration on all enemies in a 3x3 area",
                       "actionLine": "SOBEK dashes! {target} now BLEEDS for {bleed}!"}
        , "a3": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Open Wounds",
                 "abilityDesc": "Sobek strikes the enemy, dealing 200 DAMAGE, and applying BLEED to the target. If the "
                                "target is already BLEEDING, the damage is doubled.",
                 "actionLine": "SOBEK Opens {target}'s wounds! {target} now BLEEDS for {bleed}! {damageDealt} dealt! "
                               "{additionalText}"}
        , "ult": {"abilityType": "inCombat", "maxCooldown": 10, "abilityName": "Brutalize",
                  "abilityDesc": "Sobek Strikes the enemy with all of his hatred, dealing the amount of BLEED stacks on the enemy.",
                  "actionLine": "SOBEK destroys the enemy with all of his HATRED! It deals {damageDealt} to {target}!"}}
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
        await target.TakeDamage(round(100 * self.myPlayer.s.DamageDealtMultiplier))
        if "bleed" not in target.s.statusEffects:
            target.s.statusEffects["bleed"] = {}
            target.s.statusEffects["bleed"]['amount'] = 0
        target.s.statusEffects[
            'bleed']['amount'] += 100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
        target.s.statusEffects['bleed']['amount'] *= 2
        target.s.statusEffects['bleed']['bleedTimer'] = 2
        return {"damageDealt": 100 * target.s.DamageTakenMultiplier * round(self.myPlayer.s.DamageDealtMultiplier)
            , "target": target.member.display_name, "bleed": target.s.statusEffects['bleed']['amount']}

    def a2Possible(self):
        return True

    async def a2(self):
        await doAbility(abilityRequest={"Dash": {"range": 2},
                                        "CauseEffect": {"rangeWidth": 3, "rangeHeight": 3, "effect": "bleed",
                                                        "duration": 2, "amount": None}}
                        , playerDo=self.myPlayer)

    async def a3(self, target: player):
        dmgmult = 1
        if "bleed" in target.s.statusEffects:
            dmgmult = 2
        else:
            target.s.statusEffects['bleed'] = {}
            target.s.statusEffects['bleed']['amount'] = 0
            target.s.statusEffects['bleed']['bleedTimer'] = 2
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
    maxHP: int = 2000
    SandStacks: int = 1
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 0}
    moveList = {"a1": {"abilityType": "outOfCombat", "maxCooldown": 0, "abilityName": "Arise!"
        , "abilityDesc": "Horus consumes a sand stack to summon 2 sand soldiers at random areas across the map."},
                "a2": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Conquering Sands",
                       "abilityDesc": "Horus challenges the enemy, granting himself a sand stack and increases the damage the target takes by 10% permanently!",
                       "actionLine": "Horus challenged {target}. they are Vulnerable!"}
        , "a3": {"abilityType": "outOfCombat", "maxCooldown": 1, "abilityName": "Shifting Sands",
                 "abilityDesc": "Horus consumes a sand stack to Dash the amount of sand soldiers on the field. then leaves a sand soldier in his original position!"}
        , "ult": {"abilityType": "outOfCombat", "maxCooldown": 4, "abilityName": "Emperor's Divide",
                  "abilityDesc": "Horus empowers all current soldiers, granting them 5x damage and 1000 bonus max health."}}
    playStyle = "Horus is the emperor of the sands. Horus summons sand soldiers to fight for him, and challenges his opponent to increase his damage. play around your soldiers to control the field and win"

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 2000
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Horus_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP
        self.myPlayer.s.movementSpeed = 1

    async def p(self, x: int = None, y: int = None):
        if x is None and y is None:
            x = random.randint(0, self.myPlayer.myGame.lengthX - 1)
            y = random.randint(0, self.myPlayer.myGame.lengthY - 1)
        if self.myPlayer.myGame.zones[x][y].isOccupied() or self.myPlayer.myGame.zones[x][y].myEvent is not None:
            await self.p(x, y)
        else:
            await doAbility(abilityRequest={"Summon": {"hero": "SandSoldier", "x": x, "y": y}}, playerDo=self.myPlayer)

    def a1Possible(self):
        return self.SandStacks > 0

    async def a1(self):
        self.SandStacks -= 1
        for i in range(2):
            await self.p()
        await doAbility(abilityRequest={"Dash": {"range": 1}}, playerDo=self.myPlayer)

    async def a2(self, target: player):
        target.s.DamageTakenMultiplier += 0.1
        await target.TakeDamage(10 * self.myPlayer.s.DamageDealtMultiplier)
        self.SandStacks += 1
        return {"damage": round(10 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier),
                "target": target.member.display_name}

    def a3Possible(self):
        if self.SandStacks < 0:
            return False
        for plyer in self.myPlayer.myGame.playerObjects:
            if plyer.hero.heroName == "SandSoldier" and plyer.s.team == self.myPlayer.s.team:
                return True
        return False

    async def a3(self):
        originalX = self.myPlayer.s.posX
        originalY = self.myPlayer.s.posY
        self.SandStacks -= 1
        dashLength: int = 0
        for plyer in self.myPlayer.myGame.playerObjects:
            if plyer.hero.heroName == "SandSoldier" and plyer.s.team == self.myPlayer.s.team:
                dashLength += 1
        await doAbility(abilityRequest={"Dash": {"range": dashLength}}, playerDo=self.myPlayer)
        await self.p(originalX, originalY)

    def ultPossible(self):
        for plyer in self.myPlayer.myGame.playerObjects:
            if plyer.hero.heroName == "SandSoldier" and plyer.s.team == self.myPlayer.s.team:
                return True
        return False

    async def ult(self):
        plyerList = []
        for plyer in self.myPlayer.myGame.playerObjects:
            if plyer.hero.heroName == "SandSoldier" and plyer.s.team == self.myPlayer.s.team:
                plyerList.append(plyer)
        await doAbility(abilityRequest={"Buff": {"plyerList": plyerList, "Buff": "empower"}}, playerDo=self.myPlayer)
        await doAbility(abilityRequest={"Dash": {"range": 1}}, playerDo=self.myPlayer)


class SandSoldier:
    myPlayer: player = None
    image: Image
    maxHP: int = 500
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 0}
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Ordered Strike",
                       "abilityDesc": "Strike the enemy on horus's command, dealing 50 DAMAGE.",
                       "actionLine": "The sand soldier strikes! It deals {damage} to {target}!"},
                "a2": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Consuming strike",
                       "abilityDesc": "The sand soldier strikes for 100 damage but increases the enemies defense by 10% permanently"
                                      "increases the damage the enemy takes by 10% permanently!",
                       "actionLine": "The sand soldier strikes! It deals {damage} to {target}! they feel stronger now..."},
                "a3": {"abilityType": "inCombat", "maxCooldown": 2, "abilityName": "Sand Duel",
                       "abilityDesc": "The sand soldier challenges the enemy,"
                                      "increasing the damage the enemy takes by 10% permanently!",
                       "actionLine": "Horus challenged {target}. they are Vulnerable!"},
                "ult": {"abilityType": "inCombat", "maxCooldown": 5, "abilityName": "Valiant Sacrifice",
                        "abilityDesc": "The sand soldier sacrifices its life to deal 200 damage",
                        "actionLine": "The sand soldier strikes with its life! It deals {damage} to {target}!"}}

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 500
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\SandSoldier_Face.png")
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

    async def a1(self, target: player):
        await target.TakeDamage(50 * self.myPlayer.s.DamageDealtMultiplier)
        return {"damage": round(50 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier),
                "target": target.member.display_name}

    async def a2(self, target: player):
        await target.TakeDamage(100 * self.myPlayer.s.DamageDealtMultiplier)
        target.s.DamageTakenMultiplier -= 0.1
        return {"damage": round(100 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier),
                "target": target.member.display_name}

    async def a3(self, target: player):
        await target.TakeDamage(5 * self.myPlayer.s.DamageDealtMultiplier)
        target.s.DamageTakenMultiplier += 0.1
        return {"damage": round(5 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier),
                "target": target.member.display_name}

    async def ult(self, target: player):
        await target.TakeDamage(200 * self.myPlayer.s.DamageDealtMultiplier)
        await self.myPlayer.TakeDamage(100000)
        return {"damage": round(200 * self.myPlayer.s.DamageDealtMultiplier), "target": target.member.display_name}


class Ra:
    myPlayer: player = None
    image: Image
    maxHP: int = 3500
    coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 9999}
    SunOrbs: int = 0
    moveList = {"a1": {"abilityType": "inCombat", "maxCooldown": 0, "abilityName": "Solar Strike",
                       "abilityDesc": "Ra commands the sun to fire at his enemy, dealing 50 DAMAGE. if Ra has 5 or "
                                      "more Sun orbs, the beam will deal an additional 150 damage. ",
                       "actionLine": "Ra Fires! It deals {damageDealt} to {target}!""{additionalText}"},
                "a2": {"abilityType": "inCombat", "maxCooldown": 4, "abilityName": "Sun Light's Guard",
                       "abilityDesc": "Reduces my damage taken by 10 for each stack of Sun Light. cooldown is reduced by 1 whenever Ra picks "
                                      "a Sun orb.",
                       "actionLine": "the sun surrounds Ra, granting him {amount} damage reduction!"}
        , "a3": {"abilityType": "outOfCombat", "maxCooldown": 2, "abilityName": "Advanced Maneuver",
                 "abilityDesc": "Ra utilizes his full potential for 1 turn, gaining 1 bonus move range for each "
                                "stack of his Sun orbs"}
        , "ult": {"abilityType": "inCombat", "maxCooldown": 2, "abilityName": "Sun Gods Searing Wrath",
                  "abilityDesc": "Ra channels the full power of the sun, dealing 2000 damage and healing himself for "
                                 "the damage dealt",
                  "actionLine": "Ra obliterates {target}! It deals {damageDealt} and heals Ra for {damageDealt}"}}
    playStyle = "Ra is the Sun God, by collecting sun orbs he can ascend to his full potential, dealing incredible " \
                "damage with very strong tools be sure to collect your orbs before your enemy destroys them to gain power and win the game!"

    def __init__(self, plyer):
        self.myPlayer = plyer
        self.maxHP = 3500
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Ra_Face.png")
        self.coolDowns = {"a1": 0, "a2": 0, "a3": 0, "ult": 9999}
        self.myPlayer.s.maxHP = self.maxHP
        self.myPlayer.s.currentHP = self.myPlayer.s.maxHP

    def p(self):
        x = random.randint(0, self.myPlayer.myGame.lengthX - 1)
        y = random.randint(0, self.myPlayer.myGame.lengthY - 1)
        if self.myPlayer.myGame.zones[x][y].isOccupied() or self.myPlayer.myGame.zones[x][y].myEvent is not None:
            self.p()
        else:
            gotZone = self.myPlayer.myGame.zones[x][y]
            gotZone.myEvent = gotZone.event("sunOrb")
            print("passive event created on zone " + str(x) + " " + str(y))

    async def a1(self, target: player):
        damagedealt = 0
        await target.TakeDamage(50 * self.myPlayer.s.DamageDealtMultiplier)
        damagedealt += 50 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
        if self.SunOrbs >= 5:
            await target.TakeDamage(150 * self.myPlayer.s.DamageDealtMultiplier)
            damagedealt += 150 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier
            return {"damageDealt": int(damagedealt), "target": target.hero.heroName,
                    "additionalText": "The Sun Scorched the enemy, dealing bonus damage!"}
        return {"damageDealt": int(damagedealt), "target": target.hero.heroName,
                "additionalText": "the attacks potential is not unleashed..."}

    async def a2(self, target: player):
        self.myPlayer.s.DamageTakenMultiplier -= self.SunOrbs * 0.1
        return {"amount": self.SunOrbs * 10}

    def a3Possible(self):
        return self.SunOrbs > 0

    async def a3(self):
        await doAbility(abilityRequest={"Dash": {"range": self.SunOrbs + 1}}, playerDo=self.myPlayer)
        return {"damageDealt": self.SunOrbs}

    async def ult(self, target: player):
        await target.TakeDamage(2000 * self.myPlayer.s.DamageDealtMultiplier)
        self.myPlayer.s.currentHP = max(
            min(self.myPlayer.s.currentHP + 2000 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier,
                self.myPlayer.s.maxHP), self.myPlayer.s.currentHP)
        return {"damageDealt": int(2000 * target.s.DamageTakenMultiplier * self.myPlayer.s.DamageDealtMultiplier),
                "target": target.hero.heroName}


class hero:
    heroName: str
    heroObject = None

    def __init__(self, heroName: str, plyer: player):
        self.heroName = heroName
        heroObjects = {
            "Sobek": Sobek,
            "Ra": Ra,
            "Horus": Horus,
            "SandSoldier": SandSoldier
        }
        self.heroObject = heroObjects[heroName](plyer)
        plyer.s.maxHP = self.heroObject.maxHP
        plyer.s.currentHP = self.heroObject.maxHP


async def doAbility(abilityRequest: dict, playerDo: player):
    """
    Ability requests are built of a dict that is in order to what the end user needs to do.
    ability types:
    Dash (includes range)
    Cause Effect (includes effect -> REQUIRED, amount, duration (one of these are required, replace the others with None)
    Damage (Zone, amount)
    Heal (Zone, amount)
    :param playerDo:
    :param abilityRequest:
    :return:
    """
    playerDo.doingAbility = True
    if playerDo.savedMove is None:
        playerDo.savedMove = playerDo.s.movementSpeed
    if "Dash" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        await doDash(playerDo, abilityRequest[do]['range'])
        abilityRequest.pop(do)
        playerDo.outOfCombatNext = abilityRequest
        print(playerDo.outOfCombatNext)
        msg = False
    elif "CauseEffect" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        await doEffect(playerDo, abilityRequest[do]['rangeWidth'], abilityRequest[do]['rangeHeight'],
                       abilityRequest[do]['effect'], abilityRequest[do]['duration'], abilityRequest[do]['amount'])
        abilityRequest.pop(do)
        playerDo.outOfCombatNext = abilityRequest
        print(playerDo.outOfCombatNext)
        msg = True
    elif "Summon" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        print(abilityRequest[do])
        await Summon(playerDo, abilityRequest[do]["hero"], abilityRequest[do]["x"], abilityRequest[do]["y"])
        msg = True
    elif "Buff" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        print(abilityRequest[do])
        await Buff(abilityRequest[do]["plyerList"], abilityRequest[do]["Buff"])
        msg = True
    return msg


async def doDash(player, range):
    # we need to render the map with the ability range
    player.s.movementSpeed = range
    await player.myGame.generate_map()
    possibleMoves = player.canMoveTo()
    await IA.add_checks_to_map(possibleMoves, player.myGame.id, player.s.posX, player.s.posY, abilityChecks=True)
    try:
        await player.myGame.mapMessage.delete()
    except:
        # if we can't delete the map message, were probably just executing this dash after another ability, so its fine
        pass
    mapMessage = await player.myGame.ctx.send(file=discord.File(player.myGame.directoryPath + "\\map.png"))
    player.myGame.mapMessage = mapMessage
    return False


async def doEffect(player, rangeWidth, rangeHeight, effect, duration, amount):
    await player.myGame.mapMessage.delete()
    zones = player.myGame.zones
    conditional = amount is None
    await player.myGame.ctx.send(player.hero.heroName + " Inflicts " + str(effect) + "...", delete_after=3)
    for i in range(rangeWidth):
        for j in range(rangeHeight):
            if zones[i][j].isOccupied():
                if conditional:
                    currentPlayer = zones[i][j].myPlayer
                    if currentPlayer == player:
                        continue
                    if effect not in currentPlayer.s.statusEffects:
                        return
                    currentPlayer.s.statusEffects[effect][effect + 'Timer'] = duration
                    await player.myGame.ctx.send(
                        currentPlayer.hero.heroName + " Is feeling the effects of " + effect + "!",
                        delete_after=3)
                else:
                    currentPlayer = zones[i][j].myPlayer
                    currentPlayer.s.statusEffects[effect] = {}
                    currentPlayer.s.statusEffects[effect][effect + 'Timer'] = duration
                    await player.myGame.ctx.send("Can you feel the " + effect + ", " + player.hero.heroName,
                                                 delete_after=3)
    # passive abilities dont generate maps


async def Buff(plyerList, Buff):
    if Buff == "empower":
        for plyer in plyerList:
            plyer.s.DamageDealtMultiplier += 5
            plyer.s.maxHP += 1000
            plyer.s.currentHP += 1000
        await plyerList[0].myGame.ctx.send(
            "All soldiers in team " + str(plyerList[0].s.team) + " feel empowered! Damage x5, Health +1000!",
            delete_after=3)


async def Summon(creator: player, Hero: str, posX: int, posY: int):
    newPlayer = player(posX, posY, creator.member, Hero, creator.myGame, creator.s.team)
    creator.myGame.playerObjects.append(newPlayer)
    creator.myGame.zones[posX][posY].myPlayer = newPlayer
    newPlayer.s.movementSpeed = creator.s.movementSpeed
    await creator.myGame.ctx.send(
        creator.hero.heroName + " Has Summoned " + Hero + " to the field!",
        delete_after=3)
