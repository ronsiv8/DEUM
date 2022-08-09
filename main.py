import asyncio
import gc
import io
import json, os
import random

from game import Game

import Player
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


@bot.slash_command(name="start", description="Start the game!")
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
    embed.add_field(name="AMOUNT OF PLAYERS: " + str(len(users)), value="\u200b", inline=True)
    joinButton = discord.ui.Button(label="JOIN!", style=discord.ButtonStyle.green)
    forceStartButton = discord.ui.Button(label="FORCE START", style=discord.ButtonStyle.red)
    view = discord.ui.View()
    timer = 60

    async def init_game():
        global directoryPath
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
            if timer > 1:
                timer = 1
                embed = discord.Embed(title="WELCOME TO DEUM.",
                                      description="A battle arena of the gods where you and your friends are about to verse in!",
                                      color=0xff0000)
                embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
                embed.add_field(name="Game will start in " + str(timer),
                                value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
                embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b",
                                inline=True)
                embed.add_field(name="AMOUNT OF PLAYERS: " + str(len(users)), value="\u200b", inline=True)
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
    img = Image.open(directoryPath + "\\images\\bg.png")
    imageCopy = img.copy()
    imageCopy = imageCopy.resize((2700, 2700))
    imageCopy.save(directoryPath + "\\games\\" + str(gameStats["gameId"]) + "\\bg.png")
    memberList = []
    for player in gameStats['players']:
        newMember = bot.get_user(player)
        if newMember is None:
            newMember = await bot.fetch_user(player)
        memberList.append(newMember)
    await pickChampions(memberList, ctx, gameStats, imageCopy)


async def pickChampions(memberList, ctx, gameStats, imageCopy):
    completeList = {}
    embed = discord.Embed(title="PICK YOUR CHAMPIONS", description="Everyone must now pick thier champions!",
                          color=0x00ff33)
    embed.add_field(name="Sobek",
                    value="Sobek is a well trained fighter, causing enemies to BLEED being his main power source. You have to play aggressively and cause your enemies to BLEED if you want to win.",
                    inline=False)
    embed.add_field(name="Ra",
                    value="Ra is the Sun God, by collecting sun orbs he can ascend to his full potential, dealing incredible damage with very strong tools be sure to collect your orbs before your enemy destroys them to gain power and win the game!",
                    inline=False)
    embed.add_field(name="Horus",
                    value="Horus is the emperor of the sands. Horus summons sand soldiers to fight for him, and challenges his opponent to increase his damage. play around your soldiers to control the field and win the game!",
                    inline=False)
    view = discord.ui.View()
    SobekButton = discord.ui.Button(label="PICK SOBEK", style=discord.ButtonStyle.green, custom_id="Sobek")
    RaButton = discord.ui.Button(label="PICK RA", style=discord.ButtonStyle.green, custom_id="Ra")
    HorusButton = discord.ui.Button(label="PICK HORUS", style=discord.ButtonStyle.green, custom_id="Horus")

    async def pickChamp(interaction):
        for player in memberList:
            if player.id == interaction.user.id:
                completeList[player] = interaction.custom_id
                break
        if len(completeList) == len(memberList):
            await msg.delete()
            await ctx.send("Here's the library - A 'cheat sheet', if you will. Use it if you need it!")
            await sendLibrary(ctx)
            game = Game(gameStats["gameId"], gameStats["creator"], completeList, gameStats["ctx"],
                        imageCopy.width // 300
                        , imageCopy.height // 300, bot)
            currentGames.append(game)
            await game.generate_map()
            await game.doTurn()
            currentPlayer = await game.getCurrentPlayerTurn()
            currentPlayerMoves = currentPlayer.canMoveTo()
            await IA.add_checks_to_map(currentPlayerMoves, game.id, currentPlayer.s.posX, currentPlayer.s.posY)
            mapMessage = await ctx.send(
                file=discord.File(directoryPath + "\\games\\" + str(gameStats["gameId"]) + "\\map.png"))
            game.mapMessage = mapMessage
            return

    HorusButton.callback = pickChamp
    RaButton.callback = pickChamp
    SobekButton.callback = pickChamp

    view.add_item(SobekButton)
    view.add_item(RaButton)
    view.add_item(HorusButton)
    msg = await ctx.send(embed=embed, view=view)


async def findPlayerObject(userId):
    # look through all players and find the one with the same id as the userId.
    for player in currentGames:
        for playerObject in player.playerObjects:
            if playerObject.member.id == userId:
                return playerObject
    return None


async def findCurrentPlayerObject(userId):
    for player in currentGames:
        for playerObject in player.playerObjects:
            if playerObject.member.id == userId and playerObject == await playerObject.myGame.getCurrentPlayerTurn() and \
                    (playerObject.myGame.awaitingMoves is not None or playerObject.myGame.awaitingMoves == userId):
                return playerObject
    return None


@bot.slash_command(name='pass_turn', description='pass your turn, counts as moving in place')
async def pass_turn(ctx):
    await pass_turnFunc(ctx)


async def pass_turnFunc(ctx):
    userPlayer: Player.player = await findCurrentPlayerObject(ctx.author.id)
    if userPlayer is None:
        userPlayer = await findPlayerObject(ctx.author.id)
        if userPlayer is None:
            await ctx.respond("You are not in a game!")
            return
        else:
            await ctx.respond("It is not your turn!", delete_after=1)
            return
    if userPlayer.myGame.battle is not None:
        await ctx.respond("Please wait for the battle to end!", delete_after=1)
        return
    await moveToFunc(ctx, userPlayer.s.posX+1, userPlayer.s.posY+1)


@bot.slash_command(name='move_to', description='move to x,y')
async def moveTo(ctx, *, x: int, y: int):
    await moveToFunc(ctx, x, y)


async def moveToFunc(ctx, x, y):
    await ctx.respond("moving..", delete_after=1)
    userPlayer: Player.player = await findCurrentPlayerObject(ctx.author.id)
    if userPlayer is None:
        userPlayer = await findPlayerObject(ctx.author.id)
        if userPlayer is None:
            await ctx.respond("You are not in a game!")
            return
        else:
            await ctx.respond("It is not your turn!", delete_after=1)
            return
    if userPlayer.myGame.battle is not None:
        await ctx.respond("Please wait for the battle to end!", delete_after=1)
        return
    possibleMoves = userPlayer.canMoveTo()
    if (x, y) not in possibleMoves:
        await ctx.respond("You can't move there! Moves:" + str(possibleMoves), delete_after=1)
        return
    userPlayer.moveTo(x - 1, y - 1)
    if userPlayer.outOfCombatNext is None:
        await userPlayer.myGame.generate_map()
        # add checks
        nextPlayerMoves = await userPlayer.myGame.getNextPlayerTurn()
        nextPlayerMoves = nextPlayerMoves.canMoveTo()
        await IA.add_checks_to_map(nextPlayerMoves, userPlayer.myGame.id, userPlayer.s.posX, userPlayer.s.posY)
        await ctx.send("Moved!", delete_after=1)
        await userPlayer.myGame.mapMessage.delete()
        message = await ctx.send(
            file=discord.File(directoryPath + "\\games\\" + str(userPlayer.myGame.id) + "\\map.png"))
        userPlayer.myGame.mapMessage = message
    else:
        await ctx.send("Moved!", delete_after=1)
        done = await handleAbilities(userPlayer, ctx)
        if not done: return
    # activate events
    zone = userPlayer.myGame.zones[x - 1][y - 1]
    if zone.myEvent is not None:
        print("event found")
        eventResponse = await zone.myEvent.eventObject.ActivateEvent(userPlayer)
        if eventResponse:
            await ctx.send(eventResponse, delete_after=5)
    adjecentEnemies = await userPlayer.adjacentEnemies()
    if not adjecentEnemies:
        await userPlayer.myGame.doTurn()
        return
    if userPlayer.outOfCombatNext is not None:
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
        x: int = int(interaction.data['custom_id'][-4])
        y: int = int(interaction.data['custom_id'][-1])
        print(str(x) + ", " + str(y))
        attackPlayer: Player.player = userPlayer.myGame.zones[x][y].myPlayer
        await fightLoop(attackPlayer, userPlayer, ctx)
        await battleMessage.delete()

    async def runCallback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.defer()
            return
        await battleMessage.delete()
        await userPlayer.myGame.doTurn()
        return

    adjacentEnemies = await userPlayer.adjacentEnemies()
    buttons = []
    for plyer in adjacentEnemies:
        if plyer.s.team != userPlayer.s.team:
            button = discord.ui.Button(
                label="FIGHT " + plyer.member.name + " at " + str(plyer.s.posX + 1) + ", " + str(plyer.s.posY + 1),
                style=discord.ButtonStyle.red)
            button.custom_id = str(plyer.member.id) + "X:" + str(plyer.s.posX) + "Y:" + str(plyer.s.posY)
            button.callback = fightCallback
            buttons.append(button)
    for button in buttons:
        view.add_item(button)
    runButton = discord.ui.Button(label="Don't engage", style=discord.ButtonStyle.green)
    runButton.callback = runCallback
    view.add_item(runButton)
    userPlayer.myGame.awaitingMoves = True
    battleMessage = await ctx.send(embed=embed, view=view)


async def handleAbilities(playerDo, ctx):
    if playerDo.outOfCombatNext == {}:
        playerDo.outOfCombatNext = None
        playerDo.s.movementSpeed = playerDo.savedMove
        playerDo.savedMove = None
        await playerDo.myGame.generate_map()
        # add checks
        nextPlayerMoves = await playerDo.myGame.getNextPlayerTurn()
        nextPlayerMoves = nextPlayerMoves.canMoveTo()
        try:
            await playerDo.myGame.mapMessage.delete()
        except:
            pass
        await IA.add_checks_to_map(nextPlayerMoves, playerDo.myGame.id, playerDo.s.posX, playerDo.s.posY)
        message = await ctx.send(
            file=discord.File(directoryPath + "\\games\\" + str(playerDo.myGame.id) + "\\map.png"))
        playerDo.myGame.mapMessage = message
        return True
    isPassive = await Player.doAbility(playerDo.outOfCombatNext, playerDo)
    if isPassive:
        await handleAbilities(playerDo, ctx)
    return False


async def fightLoop(attackingPlayer: Player.player, defendingPlayer: Player.player, ctx, battle=None,
                    choosingMessage=None):
    if battle is None:
        battle: Battle = Battle(attackingPlayer, defendingPlayer, attackingPlayer.myGame, ctx)
    if battle.done:
        await attackingPlayer.myGame.doTurn()
        await attackingPlayer.myGame.generate_map()
        # add checks
        nextPlayerMoves = await attackingPlayer.myGame.getCurrentPlayerTurn()
        nextPlayerMoves = nextPlayerMoves.canMoveTo()
        await IA.add_checks_to_map(nextPlayerMoves, attackingPlayer.myGame.id, attackingPlayer.s.posX,
                                   attackingPlayer.s.posY)
        await attackingPlayer.myGame.mapMessage.delete()
        message = await ctx.send(
            file=discord.File(directoryPath + "\\games\\" + str(attackingPlayer.myGame.id) + "\\map.png"))
        attackingPlayer.myGame.mapMessage = message
        return
    if battle.battleMessage is None:
        await battle.generateBattleImage()

    currentHero = battle.attackingTeam.hero
    currentPlayer = battle.attackingTeam

    class MyView(discord.ui.View):
        nonlocal currentHero, currentPlayer, battle
        optionsArray = []

        for ability in currentHero.heroObject.moveList:
            print(currentHero.heroObject.coolDowns)
            currentHero = battle.getCurrentTurn()
            currentHero = currentHero.hero
            try:
                print(currentHero.heroObject.moveList[ability])
                if currentHero.heroObject.moveList[ability]['abilityType'] != "inCombat" or \
                        currentHero.heroObject.coolDowns[ability] != 0:
                    print(currentHero.heroObject.coolDowns)
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
            choosingMessage = await ctx.send(currentPlayer.member.mention + "\nATTACKING PLAYER - YOUR MOVE!",
                                             view=myView)
        else:
            await choosingMessage.edit(currentPlayer.member.mention + "\nATTACKING PLAYER - YOUR MOVE!", view=myView)
    else:
        currentHero = battle.defendingTeam.hero
        currentPlayer = battle.getCurrentTurn()
        myView = MyView()
        if choosingMessage is None:
            choosingMessage = await ctx.send(currentPlayer.member.mention + "\nDEFENDING PLAYER - YOUR MOVE!",
                                             view=myView)
        else:
            await choosingMessage.edit(currentPlayer.member.mention + "\nDEFENDING PLAYER - YOUR MOVE!", view=myView)


@bot.slash_command(name='set_pos', description='amogus')
async def setPos(ctx, *, x: int, y: int):
    await ctx.defer()
    userPlayer: Player.player = await findPlayerObject(ctx.author.id)
    if userPlayer is None:
        await ctx.respond("You are not in a game!")
        return
    userPlayer.moveTo(x - 1, y - 1)
    await ctx.send("CURRENT: " + userPlayer.PrintStatus())
    await ctx.send("POSSIBLE MOVES: " + str(userPlayer.canMoveTo()))
    await userPlayer.myGame.generate_map()
    await ctx.respond(file=discord.File(directoryPath + "\\games\\" + str(userPlayer.myGame.id) + "\\map.png"))


async def sendLibrary(ctx):
    libraryMessage = None

    page = 0
    pageArray = ["basics", "Sobek", "Horus", "sandSolider", "Ra", "Events"]

    view = discord.ui.View()
    buttonNext = discord.ui.Button(label="Next", style=discord.ButtonStyle.green)
    buttonPrevious = discord.ui.Button(label="Previous", style=discord.ButtonStyle.green)

    async def nextPage(interaction):
        nonlocal page
        page += 1
        if page >= len(pageArray):
            page = 0
        if pageArray[page] == "basics":
            await basics(ctx)
        elif pageArray[page] == "Sobek":
            await Sobek(ctx)
        elif pageArray[page] == "Horus":
            await Horus(ctx)
        elif pageArray[page] == "sandSolider":
            await sandSolider(ctx)
        elif pageArray[page] == "Ra":
            await Ra(ctx)
        elif pageArray[page] == "Events":
            await Events(ctx)
        await interaction.response.defer()

    async def previousPage(interaction):
        nonlocal page
        page -= 1
        if page < 0:
            page = len(pageArray) - 1
        if pageArray[page] == "basics":
            await basics(ctx)
        elif pageArray[page] == "Sobek":
            await Sobek(ctx)
        elif pageArray[page] == "Horus":
            await Horus(ctx)
        elif pageArray[page] == "sandSolider":
            await sandSolider(ctx)
        elif pageArray[page] == "Ra":
            await Ra(ctx)
        elif pageArray[page] == "Events":
            await Events(ctx)
        await interaction.response.defer()

    buttonNext.callback = nextPage
    buttonPrevious.callback = previousPage

    view.add_item(buttonNext)
    view.add_item(buttonPrevious)

    async def basics(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="THE DEUM LIBRARY - BASICS")
        embed.add_field(name="WELCOME TO DEUM!",
                        value="We hope you have fun here. This library should help you get to know the game from the ins and outs!",
                        inline=False)
        embed.add_field(name="HOW TO MOVE",
                        value="Use /move_to to move with the X and Y coordinates you want and can (shown with a green dot on the space). ",
                        inline=True)
        embed.add_field(name="HOW TO FIGHT",
                        value="If, at the end of your turn, and after using any abilities, you are standing beside an enemy player, you will be able to engage in combat. In combat, the defender always acts first.",
                        inline=True)
        embed.add_field(name="HOW TO WIN", value="If you are the last player on the board, you have won the game!",
                        inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    async def Sobek(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="Sobek",
                              description="Sobek is a well trained fighter, causing enemies to BLEED being his main power source. You have to play aggressively and cause your enemies to BLEED if you want to win.")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/814938626399404082/1006512095711469598/hero.png")
        embed.add_field(name="passive: Bleeding Blows",
                        value="When Sobek deals damage to an enemy, addtionally apply half the damage dealt as bleed, after 2 turns, bleed expires to deal all of it as damage.",
                        inline=True)
        embed.add_field(name="ability 1: Bleeding Strike",
                        value="Sobek Strikes his enemy, dealing 100 DAMAGE, refreshing BLEED's Duration on the target, and applying BLEED according to damage dealt. After that, DOUBLE the target's BLEED amount",
                        inline=True)
        embed.add_field(name="ability 2: Hunter's Chase",
                        value="Dash 2 tiles. After that, refresh BLEED's Duration on all enemies in a 3x3 area",
                        inline=True)
        embed.add_field(name="ability 3: Open Wounds",
                        value="Sobek strikes the enemy, dealing 200 DAMAGE, and applying BLEED to the target. If the target is already BLEEDING, the damage is doubled.",
                        inline=True)
        embed.add_field(name="Ultimate: Brutalize",
                        value="Sobek Strikes the enemy with all of his HATRED! dealing the amount of BLEED stacks on the enemy.",
                        inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    async def Horus(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="Horus",
                              description="Horus is the emperor of the sands. Horus summons sand soldiers to fight for him, and challenges his opponent to increase his damage. play around your soldiers to control the field and win the game!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1004497816464404550/1006542814454227105/hero.png")
        embed.add_field(name="ability 1: Arise! (out of combat)",
                        value="Horus consumes a sand stack to summon 2 sand soldiers at random areas across the map.",
                        inline=True)
        embed.add_field(name="ability 2: Conquering Sands",
                        value="Horus challenges the enemy, granting himself a stack " \
                              "of sand soldiers and increases the damage the target takes by 10 % permanently!",
                        inline=True)
        embed.add_field(name="ability 3: Shifting Sands (out of combat - cooldown = 1)",
                        value="Horus consumes a stack of his sand soldiers to Dash the amount of sand soldiers on the field. then leaves a sand soldier in his original position!",
                        inline=True)
        embed.add_field(name="Ultimate: Emperors Divide(out of combat - cooldown = 4)",
                        value="Horus empowers all current soldiers, granting them 5x damage and 1000 bonus max health!",
                        inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    async def sandSolider(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="Sand Soldier", description="a simple soldier made out of sand. belongs to Horus.")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/957668331203199028/1006566123170435112/SandSoldier_Face.png")
        embed.add_field(name="ability 1: Ordered Strike",
                        value="Strike the enemy on horus's command, dealing 50 DAMAGE", inline=True)
        embed.add_field(name="ability 2: Consuming strike",
                        value="The sand soldier strikes for 100 damage but increases the enemies defense by 10% permanently",
                        inline=True)
        embed.add_field(name="ability 3: Sand Duel",
                        value="The sand soldier challenges the enemy, increasing the damage the enemy takes by 10% permanently!",
                        inline=True)
        embed.add_field(name="Ultimate: Valiant Sacrifice",
                        value="The sand soldier sacrifices its life to deal 200 damage", inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    async def Ra(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="Ra",
                              description="Ra is the Sun God, by collecting sun orbs he can ascend to his full potential, dealing incredible damage with very strong tools be sure to collect your orbs before your enemy destroys them to gain power and win the game!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1004497816464404550/1006538635933401108/hero.png")
        embed.add_field(name="ability 1: Solar Strike",
                        value="Ra commands the sun to fire at his enemy, dealing 50 damage. if Ra has 5 or more Sun orbs, the beam will deal an additional 150 damage.",
                        inline=True)
        embed.add_field(name="ability 2: Sun Lights Guard (cooldown = 4)",
                        value="Reduces my damage taken by 10 for each stack of Sun Light. cooldown is reduced by 1 whenever Ra picks a Sun orb.",
                        inline=True)
        embed.add_field(name="ability 3: Advanced Maneuver (out of combat - cooldown = 3)",
                        value="Ra utilizes his full potential for 1 turn, gaining 1 bonus move range for each stack of his Sun orbs.",
                        inline=True)
        embed.add_field(name="Ultimate: Sun Gods Searing Wrath (cooldown = 2)",
                        value="Ra channels the full power of the sun, dealing 2000 damage and healing himself for the damage dealt!",
                        inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    async def Events(ctx):
        nonlocal libraryMessage
        embed = discord.Embed(title="Events")
        embed.add_field(name="What are events?",
                        value="Events are a way to upgrade your stats. An event is shown by there being a symbol on a Zone. When you move to the Zone with the symbol, you will activate the event.",
                        inline=False)
        embed.add_field(name="Event rewards?",
                        value="Most of the time stepping on an Event Zone is a good idea, but be careful...",
                        inline=True)
        if libraryMessage is None:
            libraryMessage = await ctx.send(embed=embed, view=view)
        else:
            await libraryMessage.edit(embed=embed, view=view)

    await basics(ctx)


@bot.slash_command(name="library", description="Get familiar with DEUM!")
async def library(ctx):
    await ctx.respond("Here!", delete_after=1)
    await sendLibrary(ctx)


@bot.slash_command(name='stats', description='Shows your current characters stats.')
async def stats(ctx):
    player = await findCurrentPlayerObject(ctx.author.id)
    if player is None:
        player = await findPlayerObject(ctx.author.id)
    if player is None:
        await ctx.respond("you are not in a game!")
        return
    await player.PrintStatus()

bot.run(token)
