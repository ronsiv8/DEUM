import imageActions as IA
import discord


async def doAbility(abilityRequest: dict, playerDo):
    """
    Ability requests are built of a dict that is in order to what the end user needs to do.
    ability types:
    Dash (includes range)
    Cause Effect (includes effect -> REQUIRED, amount, duration (one of these are required, replace the others with None)
    Damage (Zone, amount)
    Heal (Zone, amount)
    :param abilityRequest:
    :return:
    """
    playerDo.doingAbility = True
    playerDo.savedMove = playerDo.s.movementSpeed
    if "Dash" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        await doDash(playerDo, abilityRequest[do]['range'])
        abilityRequest.pop(do)
        playerDo.outOfCombatNext = abilityRequest
        print(playerDo.outOfCombatNext)
        msg = False
    elif "CauseEffect" in list(abilityRequest.keys())[0]:
        do = list(abilityRequest.keys())[0]
        await doEffect(playerDo, abilityRequest[do]['rangeWidth'], abilityRequest[do]['rangeHeight'],
                       abilityRequest[do]['effect'], abilityRequest[do]['duration'], abilityRequest[do]['amount'])
        abilityRequest.pop(do)
        playerDo.outOfCombatNext = abilityRequest
        print(playerDo.outOfCombatNext)
        msg = True
    return msg


async def doDash(player, range):
    # we need to render the map with the ability range
    player.s.movementSpeed = range
    await player.myGame.generate_map()
    possibleMoves = player.canMoveTo()
    await IA.add_checks_to_map(possibleMoves, player.myGame.id, player.s.posX, player.s.posY, abilityChecks=True)
    try:
        await player.myGame.mapMessage.delete()
    except:
        # if we can't delete the map message, were probably just executing this dash after another ability, so its fine
        pass
    mapMessage = await player.myGame.ctx.send(file=discord.File(player.myGame.directoryPath + "\\map.png"))
    player.myGame.mapMessage = mapMessage
    return False


async def doEffect(player, rangeWidth, rangeHeight, effect, duration, amount):
    await player.myGame.mapMessage.delete()
    zones = player.myGame.zones
    conditional = amount is None
    await player.myGame.ctx.send(player.hero.heroName + " Inflicts " + str(effect) + "...", delete_after=3)
    for i in range(rangeWidth):
        for j in range(rangeHeight):
            if zones[i][j].isOccupied():
                if conditional:
                    currentPlayer = zones[i][j].myPlayer
                    if currentPlayer == player:
                        continue
                    if effect not in currentPlayer.s.statusEffects:
                        return
                    currentPlayer.s.statusEffects[effect][effect + 'Timer'] = duration
                    await player.myGame.ctx.send(currentPlayer.hero.heroName + " Is feeling the effects of " + effect + "!",
                                                 delete_after=3)
                else:
                    currentPlayer = zones[i][j].myPlayer
                    currentPlayer.s.statusEffects[effect] = {}
                    currentPlayer.s.statusEffects[effect][effect + 'Timer'] = duration
                    await player.myGame.ctx.send("Can you feel the " + effect + ", " + player.hero.heroName,
                                                 delete_after=3)
    # passive abilities dont generate maps
