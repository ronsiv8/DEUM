import asyncio
import gc
import io
import json, os
import random

from game import Game

from Player import player
from PIL import Image
import json
import discord
from discord import Button
import imageActions as IA
import databaseActions as DA

currentGames = []

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()



@bot.event
async def on_ready():
    print("its morbin time")


async def playerToImage(player):
    image = Image.open(directoryPath + "\\images\\bg.jpg")
    pfp = Image.open(io.BytesIO(await player.member.display_avatar.read()))
    pfp = IA.crop_center(pfp, 300, 300)
    image.paste(pfp, (player.s.posX * 300, player.s.posY * 300))
    image.save(directoryPath + "\\images\\grid.jpg")
    image = IA.draw_grid_over_image(directoryPath + "\\images\\grid.jpg")
    image.savefig(directoryPath + "\\images\\grid.jpg")
    img = discord.File(directoryPath + "\\images\\grid.jpg")
    return img


@bot.slash_command(name="start", description="Start the game!", guild_ids=[756058242781806703])
async def start(ctx):
    await ctx.interaction.response.defer()
    timer = 60
    users = [ctx.author.id]
    embed = discord.Embed(title="WELCOME TO DEUM.",
                          description="A battle arena of the gods you and your friends are about to verse in!",
                          color=0xff0000)
    embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
    embed.add_field(name="Game will start in " + str(timer),
                    value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
    embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b", inline=True)
    embed.add_field(name="AMOUNT OF PLAYERS - " + str(len(users)), value="\u200b", inline=True)
    joinButton = discord.ui.Button(label="JOIN!", style=discord.ButtonStyle.green)
    forceStartButton = discord.ui.Button(label="FORCE START", style=discord.ButtonStyle.red)
    view = discord.ui.View()
    timer = 60

    async def init_game():
        """
        So basically this is here only to account for the _very_ rare case where there the gameId is already in use.
        VERY. RARE. Thank you copilot. :D <- that was copilot, not me. <- that was also copilot. <- that was copilot. <- that was copilot.
        :return:
        """
        # copilot, whats 1 + 1? 1 + 1 = 2?
        # copilot, whats 12341302 + 439582? 12341302 + 439582 = 12341346? how interesting, thats wrong.
        # AI is interesting because it can actually be wrong.
        gameId = random.randint(10000, 99999)
        # check if directory with the name gameId exists
        if not os.path.exists(directoryPath + "\\games\\" + str(gameId)):
            gameJson = {"creator": ctx.author.id, "players": users, "gameId": gameId, "ctx": ctx}
            await start_game(gameJson)
        else:
            await init_game()

    async def timerLoop():
        nonlocal timer, origiMsg
        await asyncio.sleep(1)
        timer -= 1
        embed = discord.Embed(title="WELCOME TO DEUM.",
                              description="A battle arena of the gods where you and your friends are about to verse in!",
                              color=0xff0000)
        embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
        embed.add_field(name="Game will start in " + str(timer),
                        value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
        embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b",
                        inline=True)
        embed.add_field(name="AMOUNT OF PLAYERS - " + str(len(users)), value="\u200b", inline=True)
        await origiMsg.edit(embed=embed)
        if timer > 0:
            await timerLoop()
        else:
            await origiMsg.delete()
            await init_game()

    async def forceStart(interaction):
        nonlocal ctx, timer
        if interaction.user.id == ctx.author.id:
            if timer > 5:
                timer = 5
                embed = discord.Embed(title="WELCOME TO DEUM.",
                                      description="A battle arena of the gods where you and your friends are about to verse in!",
                                      color=0xff0000)
                embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
                embed.add_field(name="Game will start in " + str(timer),
                                value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
                embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b",
                                inline=True)
                embed.add_field(name="AMOUNT OF PLAYERS - " + str(len(users)), value="\u200b", inline=True)
                await origiMsg.edit(embed=embed)

    async def joinButtonCallback(interaction):
        if interaction.user.id in users:
            await interaction.response.defer()
            return
        users.append(interaction.user.id)
        embed = discord.Embed(title="WELCOME TO DEUM.",
                              description="A battle arena of the gods where you and your friends are about to verse in!",
                              color=0xff0000)
        embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
        embed.add_field(name="Game will start in " + str(timer),
                        value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
        embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b",
                        inline=True)
        embed.add_field(name="AMOUNT OF PLAYERS - " + str(len(users)), value="\u200b", inline=True)
        await interaction.response.defer()
        await origiMsg.edit(embed=embed)

    forceStartButton.callback = forceStart
    view.add_item(forceStartButton)
    joinButton.callback = joinButtonCallback
    view.add_item(joinButton)
    origiMsg = await ctx.respond(embed=embed, view=view)
    await timerLoop()


async def getSizeOfBoard():
    img = Image.open(directoryPath + "\\images\\bg.jpg")
    return [img.width // 300, img.height // 300]


async def start_game(gameStats):
    ctx = gameStats["ctx"]
    # create directory with the name of the gameId
    os.mkdir(directoryPath + "\\games\\" + str(gameStats["gameId"]))
    img = Image.open(directoryPath + "\\images\\bg.jpg")
    imageCopy = img.copy()
    imageCopy = imageCopy.resize((2700, 2700))
    imageCopy.save(directoryPath + "\\games\\" + str(gameStats["gameId"]) + "\\bg.jpg")
    memberList = []
    for player in gameStats['players']:
        newMember = bot.get_user(player)
        if newMember is None:
            newMember = await bot.fetch_user(player)
        memberList.append(newMember)
    game = Game(gameStats["gameId"], gameStats["creator"], memberList, gameStats["ctx"],
                imageCopy.width // 300
                , imageCopy.height // 300, bot)
    currentGames.append(game)
    await game.generate_map()
    await game.doTurn()
    currentPlayer = await game.getCurrentPlayerTurn()
    currentPlayerMoves = currentPlayer.canMoveTo()
    await IA.add_checks_to_map(currentPlayerMoves, game.id, currentPlayer.s.posX, currentPlayer.s.posY)
    await ctx.respond(file=discord.File(directoryPath + "\\games\\" + str(gameStats["gameId"]) + "\\map.png"))


async def findPlayerObject(userId):
    # look through all players and find the one with the same id as the userId.
    for player in currentGames:
        for playerObject in player.playerObjects:
            if playerObject.member.id == userId:
                return playerObject
    return None


@bot.slash_command(name='move_to', description='move to x,y', guild_ids=[756058242781806703])
async def moveTo(ctx, *, x: int, y: int):
    await ctx.defer()
    userPlayer: player = await findPlayerObject(ctx.author.id)
    if userPlayer is None:
        await ctx.respond("You are not in a game!")
        return
    if userPlayer.myGame.awaitingMoves is None or userPlayer.myGame.awaitingMoves != ctx.author.id:
        await ctx.respond("It is not your turn!")
        return
    possibleMoves = userPlayer.canMoveTo()
    if (x, y) not in possibleMoves:
        await ctx.respond("You can't move there! Moves:" + str(possibleMoves))
        return
    userPlayer.moveTo(x - 1, y - 1)
    await ctx.send("CURRENT: " + userPlayer.PrintStatus())
    await userPlayer.myGame.generate_map()
    # add checks
    nextPlayerMoves = await userPlayer.myGame.getNextPlayerTurn()
    nextPlayerMoves = nextPlayerMoves.canMoveTo()
    await IA.add_checks_to_map(nextPlayerMoves, userPlayer.myGame.id, userPlayer.s.posX, userPlayer.s.posY)
    await ctx.respond(file=discord.File(directoryPath + "\\games\\" + str(userPlayer.myGame.id) + "\\map.png"))
    await userPlayer.myGame.doTurn()


@bot.slash_command(name='set_pos', description='amogus', guild_ids=[756058242781806703])
async def setPos(ctx, *, x: int, y: int):
    await ctx.defer()
    userPlayer: player = await findPlayerObject(ctx.author.id)
    if userPlayer is None:
        await ctx.respond("You are not in a game!")
        return
    userPlayer.moveTo(x - 1, y - 1)
    await ctx.send("CURRENT: " + userPlayer.PrintStatus())
    await ctx.send("POSSIBLE MOVES: " + str(userPlayer.canMoveTo()))
    await userPlayer.myGame.generate_map()
    await ctx.respond(file=discord.File(directoryPath + "\\games\\" + str(userPlayer.myGame.id) + "\\map.png"))
bot.run(token)
