import json, os
import discord
import imageActions as IA

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()


@bot.event
async def on_ready():
    print("ready")


@bot.slash_command(name='test', description='test', guild_ids=[756058242781806703])
async def test(ctx):
    await ctx.respond(IA.draw_grid_over_image(directoryPath + "\\images\\bg.jpg"))

bot.run(token)
