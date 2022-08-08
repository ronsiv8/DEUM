import os
import random
import shutil

import discord.ext.commands.context
import numpy as np
from PIL import Image

from zone import zone
from Player import player
import imageActions as IA


class Game:
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
    battleTurnLimit = 3
    zones = None

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
        self.battleTurnLimit = 1
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
                newPlayer = player(playerX, playerY, discordId, "Horus", self, -1)
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
        possibleMoves = await turnPlayer.usableOutOfCombatAbilities()
        text = ""
        view = discord.ui.View()

        async def outOfCombatAbility(interaction):
            if interaction.user.id != turnPlayer.member.id:
                return
            ability = interaction.data['custom_id']
            ability = getattr(turnPlayer.hero.heroObject, ability)
            await ability()

        for move in possibleMoves:
            moveJson = turnPlayer.hero.heroObject.moveList[move]
            text += moveJson['abilityName'] + "\n" + moveJson['abilityDesc'] + "\n"
            abilityButton = discord.ui.Button(label="Use " + moveJson['abilityName'], style=discord.ButtonStyle.green,
                                              custom_id=move)
            abilityButton.callback = outOfCombatAbility
            view.add_item(abilityButton)
        if text == "":
            text = "\u200b"
        embed.add_field(name="And use moves:", value=text, inline=True)

        if self.actMessage is None:
            self.actMessage = await self.ctx.send(embed=embed, view=view)
            self.awaitingMoves = turnPlayer.member.id
            return
        await self.actMessage.edit(embed=embed, view=view)
        self.awaitingMoves = turnPlayer.member.id

    async def RoundStartFunctions(self):
        for plyer in self.playerObjects:
            if plyer.hero.heroName == "Ra":
                plyer.hero.heroObject.p()

    async def getNextPlayerTurn(self):
        if self.turnNum + 1 == len(self.playerObjects):
            return self.playerObjects[0]
        return self.playerObjects[self.turnNum + 1]

    async def getCurrentPlayerTurn(self):
        return self.playerObjects[self.turnNum]

    async def checkFinish(self):
        """
        Checks if the game is finished, returns result
        """
        playersAlive = []
        for player in self.playerObjects:
            if player.s.currentHP > 0:
                playersAlive.append(player)
            if len(playersAlive) > 1:
                return False
        return playersAlive[0]

    async def endGame(self, winner: player):
        """
        Ends the game, deletes the game folder and sends a message to the channel
        """
        # remove directory with things in it
        shutil.rmtree(self.directoryPath)
        await self.ctx.send("VICTORY FOR " + winner.member.display_name + " (" + winner.hero.heroName + ")! THEY HAVE "
                                                                                                        "SURVIVED DEUM!")
        # delete all players
        for player in self.playerObjects:
            del player
        self.playerObjects = []
        await self.actMessage.delete()
        await self.mapMessage.delete()
        # delete game
        del self

    async def checkFinishWhole(self):
        """
        Checks if the game is finished and if so ends the game
        """
        if await self.checkFinish() is not False:
            await self.endGame(await self.checkFinish())
            return True
        return False

    async def killPlayer(self, player: player):
        """
        Kills a player
        """
        await self.ctx.send("|FALLEN| " + player.hero.heroName.upper() + " HAS FALLEN! |FALLEN|")
        # remove player from playerObjects
        self.playerObjects.remove(player)
