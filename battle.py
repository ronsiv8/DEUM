import os
import random

from Player import player
from game import Game
from PIL import Image
from PIL import ImageOps


class Battle:
    defendingTeam: player
    attackingTeam: player
    turn: int  # 0 for attacking, 1 for defending
    turnNum: int  # number of turns taken
    myGame: Game
    battleImagePath: str

    def __init__(self, defendingTeam, attackingTeam, myGame):
        self.defendingTeam = defendingTeam
        self.attackingTeam = attackingTeam
        self.turn = 1  # defender starts
        self.turnNum = 0
        self.myGame: Game = myGame
        # init battle image
        # create a new directory
        path = myGame.directoryPath
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
        os.mkdir(path + "\\Battles\\" + name)
        # create a new image
        pathOfScript = os.path.dirname(os.path.realpath(__file__))
        originalBattleImage = Image.open(pathOfScript + "\\images\\battleBg.jpg")
        # create a new image
        self.battleImage = originalBattleImage.copy()
        count = 0
        heroImage = Image.open(pathOfScript + "\\images\\" + attackingTeam.hero.heroName + ".png")
        heroImage = ImageOps.flip(heroImage)
        self.battleImage.paste(heroImage, (attackingTeam.x * 100, attackingTeam.y * 100))
        count += 1
        count = 0
        for player in defendingTeam:
            heroImage = Image.open(pathOfScript + "\\images\\" + player.hero.heroName + ".png")
            self.battleImage.paste(heroImage, (1000 + count * 100, 400 + count * 100))
            count += 1
        self.battleImage.save(path + "\\Battles\\" + name + "\\battle.png")
        self.battleImagePath = path + "\\Battles\\" + name + "\\battle.png"





