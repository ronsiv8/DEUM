import asyncio
import io
import json, os
from Player import player, S
from PIL import Image
import json
import discord
from discord import Button
import imageActions as IA

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()

img = Image.open(directoryPath + "\\images\\bg.jpg")
img = img.resize((900, 2100))
img.save(directoryPath + "\\images\\bg.jpg")
testPlayer = None


@bot.event
async def on_ready():
    global testPlayer
    print("its morbin time")
    testPlayer = player(10, 2, 2, await bot.fetch_user(246757653282422795))


@bot.slash_command(name='test', description='test', guild_ids=[756058242781806703])
async def test(ctx):
    global testPlayer
    await ctx.defer()
    img = await playerToImage(testPlayer)
    await ctx.respond(file=img)


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

    async def timerLoop():
        nonlocal timer, origiMsg
        await asyncio.sleep(2)
        timer -= 2
        embed = discord.Embed(title="WELCOME TO DEUM.",
                              description="A battle arena of the gods you and your friends are about to verse in!",
                              color=0xff0000)
        embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
        embed.add_field(name="Game will start in " + str(timer),
                        value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
        embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b",
                        inline=True)
        embed.add_field(name="AMOUNT OF PLAYERS - " + str(len(users)), value="\u200b", inline=True)
        await origiMsg.edit(embed=embed)
        await timerLoop()

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
                              description="A battle arena of the gods you and your friends are about to verse in!",
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


@bot.slash_command(name='move_to', description='move to x,y', guild_ids=[756058242781806703])
async def moveTo(ctx, *, x: int, y: int):
    await ctx.defer()
    size = await getSizeOfBoard()
    if size[0] >= x > 0 and size[1] >= y > 0:
        x -= 1
        y -= 1
        global testPlayer
        testPlayer.moveTo(x, y)
        img = await playerToImage(testPlayer)
        await ctx.respond(file=img)
    else:
        await ctx.respond("not a valid point.")


bot.run(token)
