import asyncio
import gc
import io
import json, os
import random

from game import Game

from Player import player
from Player import hero
from PIL import Image, ImageOps
import json
import discord
from discord import Button
import imageActions as IA
import databaseActions as DA
from battle import Battle

currentGames = []

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()

bloodImage = Image.open(directoryPath + "\\images\\icons\\bleed.png")
bloodImage = bloodImage.resize((100, 114))
bloodImage.save(directoryPath + "\\images\\icons\\bleed.png")


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
    await ctx.respond("Here we go!", delete_after=1)
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
    mapMessage = await ctx.send(file=discord.File(directoryPath + "\\games\\" + str(gameStats["gameId"]) + "\\map.png"))
    game.mapMessage = mapMessage


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
        await ctx.respond("It is not your turn!", delete_after=1)
        return
    possibleMoves = userPlayer.canMoveTo()
    if (x, y) not in possibleMoves:
        await ctx.respond("You can't move there! Moves:" + str(possibleMoves), delete_after=1)
        return
    userPlayer.moveTo(x - 1, y - 1)
    await userPlayer.myGame.generate_map()
    # add checks
    nextPlayerMoves = await userPlayer.myGame.getNextPlayerTurn()
    nextPlayerMoves = nextPlayerMoves.canMoveTo()
    await IA.add_checks_to_map(nextPlayerMoves, userPlayer.myGame.id, userPlayer.s.posX, userPlayer.s.posY)
    await ctx.respond("Moved!", delete_after=1)
    await userPlayer.myGame.mapMessage.delete()
    message = await ctx.send(file=discord.File(directoryPath + "\\games\\" + str(userPlayer.myGame.id) + "\\map.png"))
    userPlayer.myGame.mapMessage = message
    adjecentPlayers = await userPlayer.adjacentPlayers()
    if not adjecentPlayers:
        await userPlayer.myGame.doTurn()
        return
    embed = discord.Embed(title="BATTLE DETECTED!", color=0xff0000)
    embed.add_field(name="The following enemies are close enough for you to engage in combat:", value="(ENEMIES)",
                    inline=False)
    embed.add_field(name="What do you want to do?", value="Choose your fights carefully...", inline=False)
    view = discord.ui.View()

    async def fightCallback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.defer()
            return
        userId = interaction.data['custom_id']
        attackPlayer: player = await findPlayerObject(int(userId))
        await fightLoop(attackPlayer, userPlayer, ctx)
        await battleMessage.delete()

    buttons = []
    for player in adjecentPlayers:
        button = discord.ui.Button(label="FIGHT " + player.member.name, style=discord.ButtonStyle.red)
        button.custom_id = str(player.member.id)
        button.callback = fightCallback
        buttons.append(button)
    for button in buttons:
        view.add_item(button)
    runButton = discord.ui.Button(label="Don't engage", style=discord.ButtonStyle.green)
    view.add_item(runButton)
    battleMessage = await ctx.send(embed=embed, view=view)


async def fightLoop(attackingPlayer: player, defendingPlayer: player, ctx, battle=None, choosingMessage=None):
    if battle is None:
        battle: Battle = Battle(attackingPlayer, defendingPlayer, attackingPlayer.myGame, ctx)
    if battle.battleMessage is None:
        await battle.generateBattleImage()

    currentHero = battle.attackingTeam.hero
    currentPlayer = battle.attackingTeam

    class MyView(discord.ui.View):
        nonlocal currentHero, currentPlayer
        optionsArray = []
        for ability in currentHero.heroObject.moveList:
            try:
                if currentHero.heroObject.moveList[ability]['abilityType'] != "inCombat"  or \
                        currentHero.heroObject.coolDowns[ability] != 0:
                    continue
                optionsArray.append(discord.SelectOption(
                    label=currentHero.heroObject.moveList[ability]["abilityName"],
                    description=currentHero.heroObject.moveList[ability]["abilityDesc"],
                    value=ability + "," + currentHero.heroObject.moveList[ability]["abilityName"]
                ))
            except ValueError:
                optionsArray.append(discord.SelectOption(
                    label=currentHero.heroObject.moveList[ability]["abilityName"],
                    description="This description is pretty long... check it out in the battle image!",
                    value=ability + "," + currentHero.heroObject.moveList[ability]["abilityName"]
                ))
        optionsArray.append(discord.SelectOption(
            label="Do Nothing",
            description="Do nothing and wait for the next turn",
            value="nothing"
        ))

        @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
            placeholder="Choose a move!",
            # the placeholder text that will be displayed if nothing is selected
            min_values=1,  # the minimum number of values that must be selected by the users
            max_values=1,  # the maxmimum number of values that can be selected by the users
            options=optionsArray,  # the options that will be displayed to the user
        )
        async def select_callback(self, select,
                                  interaction):  # the function called when the user is done selecting options
            # check if this user is the user that started the interaction
            nonlocal choosingMessage
            started = False
            if battle.getCurrentTurn().member.id == interaction.user.id:
                started = True
            if started:
                await interaction.response.send_message(f"Selected!",
                                                        delete_after=1)
                if battle.turn == 0:
                    battle.attackerAbility = select.values[0].split(',')[0]
                    battle.turn = 1
                else:
                    battle.defenderAbility = select.values[0].split(',')[0]
                    battle.turn = 0
                if battle.defenderAbility is not None and battle.attackerAbility is not None:
                    await choosingMessage.delete()
                    choosingMessage = None
                    await battle.executeCombat()
                    await fightLoop(battle.attackingTeam, battle.defendingTeam, ctx, battle=battle,
                                    choosingMessage=choosingMessage)
                else:
                    await fightLoop(battle.attackingTeam, battle.defendingTeam, ctx, battle=battle,
                                    choosingMessage=choosingMessage)

    if battle.turn == 0:
        currentHero = battle.attackingTeam.hero
        currentPlayer = battle.getCurrentTurn()
        myView = MyView()
        if choosingMessage is None:
            choosingMessage = await ctx.send(currentPlayer.member.mention + "\nATTACKING PLAYER - YOUR MOVE!", view=myView)
        else:
            await choosingMessage.edit(currentPlayer.member.mention + "\nATTACKING PLAYER - YOUR MOVE!", view=myView)
    else:
        currentHero = battle.defendingTeam.hero
        currentPlayer = battle.getCurrentTurn()
        myView = MyView()
        if choosingMessage is None:
            choosingMessage = await ctx.send(currentPlayer.member.mention + "\nDEFENDING PLAYER - YOUR MOVE!", view=myView)
        else:
            await choosingMessage.edit(currentPlayer.member.mention + "\nDEFENDING PLAYER - YOUR MOVE!", view=myView)


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


@bot.slash_command(name="battletest", description="amogus", guild_ids=[756058242781806703])
async def battleTest(ctx):
    bgImage = Image.open(directoryPath + "\\images\\bg.jpg")
    bgImage = bgImage.resize((2700, 1200))
    bgImage.save(directoryPath + "\\games\\battleBg.jpg")
    await ctx.respond(file=discord.File(directoryPath + "\\games\\battleBg.jpg"))


bot.run(token)
