import json, os
import discord
import imageActions as IA
import Player

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()

testPlayer=None


@bot.event
async def on_ready():
    print("its morbin time")
    global testPlayer
    testPlayer=Player.player(10,0,0)


@bot.slash_command(name='test', description='test', guild_ids=[756058242781806703])
async def test(ctx):
    await ctx.respond(IA.draw_grid_over_image(directoryPath + "\\images\\bg.jpg"))


@bot.slash_command(name='move_to', description='move to x,y', guild_ids=[756058242781806703])
async def moveTo(ctx, *, x:int,y:int):
    global testPlayer
    print(testPlayer.PrintPos())
    testPlayer.moveTo(x, y)
    await ctx.respond(testPlayer.PrintPos())


bot.run(token)
