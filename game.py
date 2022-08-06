import os
import random

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
    bot: discord.ext.commands.Bot
    awaitingMoves: int
    turnNum: int = 0
    mapMessage: discord.Message
    actMessage: discord.Message
    lastActMessage: discord.Message
    directoryPath: str

    def __init__(self, id, creator, players, ctx, lengthX, lengthY, bot):
        self.id = id
        self.creator = creator
        self.players = players
        self.ctx = ctx
        self.lengthX = lengthX
        self.lengthY = lengthY
        self.bot = bot
        self.awaitingMoves = None
        self.turnNum = 0
        self.mapMessage = None
        self.actMessage = None
        self.directoryPath = os.path.dirname(os.path.realpath(__file__)) + "\\games\\" + str(self.id)
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
                newPlayer = player(playerX, playerY, discordId, "Ra", self, -1)
                self.playerObjects.append(newPlayer)
                self.zones[playerX][playerY].myPlayer = newPlayer

            get_zone()
        # turn order is determined by the order of the players in the list
        random.shuffle(self.playerObjects)

    async def generate_map(self):
        directoryPath = os.path.dirname(os.path.realpath(__file__))
        img = Image.open(directoryPath + "\\images\\bg.jpg")
        imageCopy = img.copy()
        imageCopy = imageCopy.resize((2700, 2700))
        imageCopy.save(directoryPath + "\\games\\" + str(self.id) + "\\bg.jpg")
        IA.draw_grid_over_image_with_players(directoryPath + "\\games\\" + str(self.id) + "\\bg.jpg"
                                             , self.playerObjects)
        # image is created on map.jpg

    async def doTurn(self):
        self.turnNum += 1
        if self.turnNum == len(self.playerObjects):
            self.turnNum = 0
            await self.RoundStartFunctions()
        turnPlayer = self.playerObjects[self.turnNum]
        moveableTo = turnPlayer.canMoveTo()
        embed = discord.Embed(title=turnPlayer.hero.heroName + " - " + turnPlayer.member.display_name +
                                    " - YOUR TURN TO ACT!", color=0x8bd402)
        embed.add_field(name="You can move to:", value=moveableTo, inline=False)
        embed.add_field(name="And use moves:", value="usable moves", inline=True)
        if self.actMessage is None:
            self.actMessage = await self.ctx.send(embed=embed)
            self.awaitingMoves = turnPlayer.member.id
            return
        await self.actMessage.edit(embed=embed)
        self.awaitingMoves = turnPlayer.member.id

    async def RoundStartFunctions(self):
        pass

    async def getNextPlayerTurn(self):
        if self.turnNum + 1 == len(self.playerObjects):
            return self.playerObjects[0]
        return self.playerObjects[self.turnNum + 1]

    async def getCurrentPlayerTurn(self):
        return self.playerObjects[self.turnNum]
