import os

import discord.ext.commands.context
import numpy as np
from PIL import Image

from zone import zone
from Player import player
import imageActions as IA


class Game():
    id: int
    creator: int
    players: list[int]
    ctx: discord.ext.commands.context
    lengthX: int
    lengthY: int
    playerObjects: list[player]

    def __init__(self, id, creator, players, ctx, lengthX, lengthY):
        self.id = id
        self.creator = creator
        self.players = players
        self.ctx = ctx
        self.lengthX = lengthX
        self.lengthY = lengthY
        # 2d array with length of lengthX and height of lengthY with object zone
        self.zones = np.empty((lengthX, lengthY), dtype=zone)
        self.playerObjects = []
        for i in range(lengthX):
            for j in range(lengthY):
                self.zones[i][j] = zone()
        for discordId in players:
            def get_zone():
                nonlocal self
                playerX = np.random.randint(0, lengthX)
                playerY = np.random.randint(0, lengthY)
                if self.zones[playerX][playerY].isOccupied():
                    get_zone()
                newPlayer = player(playerX, playerY, discordId, "Sobek", self)
                self.playerObjects.append(newPlayer)
                self.zones[playerX][playerY].myPlayer = newPlayer

            get_zone()

    def generate_map(self):
        directoryPath = os.path.dirname(os.path.realpath(__file__))
        img = Image.open(directoryPath + "\\images\\bg.jpg")
        imageCopy = img.copy()
        imageCopy = imageCopy.resize((2100, 2100))
        imageCopy.save(directoryPath + "\\games\\" + str(self.id) + "\\bg.jpg")
        IA.draw_grid_over_image_with_players(directoryPath + "\\games\\" + str(self.id) + "\\bg.jpg"
                                             , self.playerObjects)
        # image is created on map.jpg
