import asyncio
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

testPlayer = player(10, 2, 2)

img = Image.open(directoryPath + "\\images\\bg.jpg")
img = img.resize((3000, 3000))
img.save(directoryPath + "\\images\\bg.jpg")


@bot.event
async def on_ready():
    print("its morbin time")


@bot.slash_command(name='test', description='test', guild_ids=[756058242781806703])
async def test(ctx):
    global testPlayer
    await ctx.defer()
    image = Image.open(directoryPath + "\\images\\bg.jpg")
    pfp = Image.open(directoryPath + "\\images\\pfp.png")
    pfp = IA.crop_center(pfp, 300, 300)
    image.paste(pfp, (testPlayer.s.posX * 300, testPlayer.s.posY * 300))
    image.save(directoryPath + "\\images\\grid.jpg")
    image = IA.draw_grid_over_image(directoryPath + "\\images\\grid.jpg")
    image.savefig(directoryPath + "\\images\\grid.jpg")
    img = discord.File(directoryPath + "\\images\\grid.jpg")
    await ctx.respond(file=img)


@bot.slash_command(name="start", description="Start the game!", guild_ids=[756058242781806703])
async def start(ctx):
    # ctx.interaction.
    embed = discord.Embed(title="WELCOME TO DEUM.",
                          description="A battle arena of the gods you and your friends are about to verse in!",
                          color=0xff0000)
    embed.add_field(name="JOIN THIS GAME!", value="Press the button...", inline=False)
    embed.add_field(name="Game will start in (TIMER)",
                    value="(It updates every two seconds. Don't worry if it seems stuck!)", inline=True)
    embed.add_field(name="GAME CREATOR - Force start by pressing the FORCE START Button.", value="\u200b", inline=True)
    joinButton = discord.ui.Button(label="JOIN!", style=discord.ButtonStyle.green)
    view = discord.ui.View()
    view.add_item(joinButton)
    timer = 60

    async def timerLoop():
        nonlocal timer, origiMsg
        while True:
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
            await origiMsg.edit(embed=embed)

    origiMsg = await ctx.respond(embed=embed, view=view)


@bot.slash_command(name='move_to', description='move to x,y', guild_ids=[756058242781806703])
async def moveTo(ctx, *, x: int, y: int):
    global testPlayer
    testPlayer.moveTo(x, y)
    await ctx.respond(testPlayer.PrintPos())


bot.run(token)
