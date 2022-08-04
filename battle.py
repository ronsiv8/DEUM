import os
import random

from Player import player
from game import Game
from PIL import Image


class Battle:
    defendingTeam: [player]
    attackingTeam: [player]
    turn: int  # 0 for attacking, 1 for defending
    turnNum: int  # number of turns taken
    turnOrderDefending: [player]  # list of players in turn order
    turnOrderAttacking: [player]  # list of players in turn order
    myGame: Game

    def __init__(self, defendingTeam, attackingTeam, myGame):
        self.defendingTeam = defendingTeam
        self.attackingTeam = attackingTeam
        self.turn = 1  # defender starts
        self.turnNum = 0
        self.turnOrderDefending = random.sample(self.defendingTeam, len(self.defendingTeam))
        self.turnOrderAttacking = random.sample(self.attackingTeam, len(self.attackingTeam))
        self.myGame: Game = myGame
        # init battle image
        # create a new directory
        path = myGame.directoryPath
        print(path)
        # check if there is a Battles directory
        if not os.path.exists(path + "\\Battles"):
            os.makedirs(path + "\\Battles")
        name = ""
        for player in self.defendingTeam:
            name += player.member.name + " "
        name += "-"
        for player in self.attackingTeam:
            name += player.member.name + " "
        # delete the last space in name
        name = name[:-1]
        os.mkdir(path + "\\Battles\\" + name)
        # create a new image
        pathOfScript = os.path.dirname(os.path.realpath(__file__))
        originalBattleImage = Image.open(pathOfScript + "\\images\\battleBg.jpg")
        # create a new image
        self.battleImage = originalBattleImage.copy()
        self.battleImage.save(path + "\\Battles\\" + name + "\\battle.png")



