import discord.ext.commands.context
import numpy as np
from zone import zone
from Player import player


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
        for discordId in players:
            def get_zone():
                playerX = np.random.randint(0, lengthX)
                playerY = np.random.randint(0, lengthY)
                if self.zones[playerX][playerY].isOccupied():
                    get_zone()
                newPlayer = player(playerX, playerY, discordId, "Sobek")
                self.playerObjects.append(newPlayer)
                self.zones[playerX][playerY].myPlayer = newPlayer
            get_zone()


