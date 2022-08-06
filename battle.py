import asyncio
import os
import random
import textwrap

import discord

from Player import player
from Player import hero
from game import Game
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageOps


class Battle:
    defendingTeam: player
    attackingTeam: player
    defenderAbility = None
    attackerAbility = None
    turn: int  # 0 for attacking, 1 for defending
    turnNum: int  # number of turns taken
    overallTurns: int = 0
    myGame: Game
    ctx = None
    battleMessage = None
    battleImagePath: str

    async def generateBattleImage(self):
        # init battle image
        # create a new directory
        path = self.myGame.directoryPath
        print(path)
        # check if there is a Battles directory
        if not os.path.exists(path + "\\Battles"):
            os.makedirs(path + "\\Battles")
        name = ""
        name += self.attackingTeam.member.name + " "
        name += "-"
        name += self.defendingTeam.member.name + " "
        # delete the last space in name
        name = name[:-1]
        if not os.path.exists(path + "\\Battles\\" + name):
            os.mkdir(path + "\\Battles\\" + name)
        # create a new image
        pathOfScript = os.path.dirname(os.path.realpath(__file__))
        originalBattleImage = Image.open(pathOfScript + "\\images\\battleBg.jpg")
        # create a new image
        self.battleImage = originalBattleImage.copy()
        heroImage = Image.open(pathOfScript + "\\images\\" + self.attackingTeam.hero.heroName + ".png")
        heroImage = ImageOps.mirror(heroImage)
        self.battleImage.paste(heroImage, (1500, 700))
        # draw healthbar
        draw = ImageDraw.Draw(self.battleImage)

        def new_bar(x, y, width, height, progress, bg=(129, 66, 97), fg=(0, 255, 0), fg2=(255, 255, 255)):
            # Draw the background
            draw.rectangle((x + (height / 2), y, x + width + (height / 2), y + height), fill=fg2, width=10)
            draw.ellipse((x + width, y, x + height + width, y + height), fill=fg2)
            draw.ellipse((x, y, x + height, y + height), fill=fg2)
            width = int(width * progress)
            # Draw the part of the progress bar that is actually filled
            draw.rectangle((x + (height / 2), y, x + width + (height / 2), y + height), fill=fg, width=10)
            draw.ellipse((x + width, y, x + height + width, y + height), fill=fg)
            draw.ellipse((x, y, x + height, y + height), fill=fg)

        heroImage = Image.open(pathOfScript + "\\images\\" + self.defendingTeam.hero.heroName + ".png")
        self.battleImage.paste(heroImage, (900, 700))
        # abilities
        nameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 100)
        progress = max(0, self.defendingTeam.s.currentHP / self.defendingTeam.s.maxHP)
        new_bar(50 + nameFont.getsize(self.defendingTeam.hero.heroName.upper())[0] + 50, 75, 300, 50, progress)
        draw.text(xy=(50, 50), text=self.defendingTeam.hero.heroName.upper(),
                  fill=(255, 255, 255), align="left", font=nameFont)
        nameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 60)
        draw.text(xy=(50, 150), text=self.defendingTeam.member.display_name, fill=(255, 255, 255), align="left",
                  font=nameFont)
        heroAbilities = self.defendingTeam.hero.heroObject.moveList
        abilityNameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 75)
        abilityDescriptionFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 50)
        count = 0
        for i in heroAbilities:
            if heroAbilities[i]['abilityType'] != "inCombat":
                continue
            coolDown = self.defendingTeam.hero.heroObject.coolDowns[i]
            if coolDown > 0:
                draw.text(xy=(50, 200 + count * 350), text=heroAbilities[i]['abilityName'] + " / " + str(coolDown),
                          fill=(255, 255, 255),
                          align="left", font=abilityNameFont)
            else:
                draw.text(xy=(50, 200 + count * 350), text=heroAbilities[i]['abilityName'], fill=(255, 255, 255),
                          align="left", font=abilityNameFont)
            wrap = textwrap.wrap(heroAbilities[i]['abilityDesc'], width=40)
            yheight = 0
            for j in wrap:
                draw.text(xy=(50, 275 + count * 350 + yheight * 50), text=j, fill=(255, 255, 255), align="left",
                          font=abilityDescriptionFont)
                yheight += 1
            count += 1
        # attacker abilities
        nameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 100)
        progress = max(0, self.attackingTeam.s.currentHP / self.attackingTeam.s.maxHP)
        new_bar(2550 - nameFont.getsize(self.attackingTeam.hero.heroName.upper())[0] * 2, 75, 300, 50, progress)
        draw.text(xy=(2600, 50), text=self.attackingTeam.hero.heroName.upper(),
                  fill=(255, 255, 255), anchor="ra", font=nameFont)
        nameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 60)
        draw.text(xy=(2600, 150), text=self.attackingTeam.member.display_name, fill=(255, 255, 255), anchor="ra",
                  font=nameFont)
        heroAbilities = self.attackingTeam.hero.heroObject.moveList
        abilityNameFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 75)
        abilityDescriptionFont = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 50)
        count = 0
        for i in heroAbilities:
            if heroAbilities[i]['abilityType'] != "inCombat":
                continue
            coolDown = self.attackingTeam.hero.heroObject.coolDowns[i]
            if coolDown > 0:
                draw.text(xy=(2600, 200 + count * 350), text=heroAbilities[i]['abilityName'] + " / " + str(coolDown),
                          fill=(255, 255, 255),
                          anchor="ra", font=abilityNameFont)
            else:
                draw.text(xy=(2600, 200 + count * 350), text=heroAbilities[i]['abilityName'], fill=(255, 255, 255),
                          anchor="ra", font=abilityNameFont)
            wrap = textwrap.wrap(heroAbilities[i]['abilityDesc'], width=50)
            yheight = 0
            for j in wrap:
                draw.text(xy=(2600, 275 + count * 350 + yheight * 50), text=j, fill=(255, 255, 255), anchor="ra",
                          font=abilityDescriptionFont)
                yheight += 1
            count += 1
        font = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 100)
        draw.text(xy=(1325, 50), text="ROUND " + str(self.overallTurns), fill=(255, 255, 255), align="center",
                  anchor="mm", font=font)
        font = ImageFont.truetype(pathOfScript + "\\fonts\\arial.ttf", 50)
        if self.turn == 0:
            draw.text(xy=(1325, 150), text="DEFENDER MOVE", fill=(255, 255, 255), align="center", anchor="mm",
                      font=font)
        elif self.turn == 1:
            draw.text(xy=(1325, 150), text="ATTACKER MOVE", fill=(255, 255, 255), align="center", anchor="mm",
                      font=font)
        self.battleImage.save(path + "\\Battles\\" + name + "\\battle.png")
        self.battleImagePath = path + "\\Battles\\" + name + "\\battle.png"
        if self.battleMessage is None:
            self.battleMessage = await self.ctx.send(file=discord.File(self.battleImagePath))
        else:
            await self.battleMessage.delete()
            self.battleMessage = await self.ctx.send(file=discord.File(self.battleImagePath))

    def __init__(self, defendingTeam, attackingTeam, myGame, ctx):
        self.defendingTeam = defendingTeam
        self.attackingTeam = attackingTeam
        self.turn = 1  # defender starts
        self.myGame: Game = myGame
        self.ctx = ctx
        self.overallTurns = 1

    async def ChooseAbility(self, plyer: player, abilityFunction):
        ability = getattr(plyer.hero.heroObject, abilityFunction)
        if plyer == self.defendingTeam:
            ability = ability(self.attackingTeam)
        else:
            ability = ability(self.defendingTeam)
        self.overallTurns += 1
        await self.generateBattleImage()
        if plyer == self.defendingTeam:
            print(ability)
            self.turn = 1
            abilityActionLine = self.defendingTeam.hero.heroObject.moveList[abilityFunction]['actionLine']
            finalAbility = abilityActionLine
            for key in ability:
                finalAbility = finalAbility.replace("{" + key + "}", str(ability[key]))
            finalAbility += "\n HP: " + str(self.attackingTeam.s.currentHP) + "/" + str(self.attackingTeam.s.maxHP)
            await self.ctx.send(finalAbility, delete_after=10)
        elif plyer == self.attackingTeam:
            self.turn = 0
            abilityActionLine = self.attackingTeam.hero.heroObject.moveList[abilityFunction]['actionLine']
            finalAbility = abilityActionLine
            for key in ability:
                finalAbility = finalAbility.replace("{" + key + "}", str(ability[key]))
            finalAbility += "\n HP: " + str(self.defendingTeam.s.currentHP) + "/" + str(self.defendingTeam.s.maxHP)
            await self.ctx.send(finalAbility, delete_after=10)

        plyer.hero.heroObject.coolDowns[abilityFunction] = plyer.hero.heroObject.moveList[abilityFunction][
            'maxCooldown']

    async def executeCombat(self):
        # apply cooldowns
        for i in self.defendingTeam.hero.heroObject.coolDowns:
            if self.defendingTeam.hero.heroObject.coolDowns[i] > 0:
                self.defendingTeam.hero.heroObject.coolDowns[i] -= 1
        await self.ChooseAbility(self.defendingTeam, self.defenderAbility)
        await asyncio.sleep(10)
        await self.ChooseAbility(self.attackingTeam, self.attackerAbility)
        await asyncio.sleep(10)
        self.attackerAbility = None
        self.defenderAbility = None

    def getCurrentTurn(self):
        if self.turn == 0:
            return self.attackingTeam
        elif self.turn == 1:
            return self.defendingTeam
