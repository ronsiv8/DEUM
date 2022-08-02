import json, os

from PIL import Image
import json
import discord
import imageActions as IA

directoryPath = os.path.dirname(os.path.realpath(__file__))
f = open(directoryPath + "\\config.json")

data = json.load(f)

token = data['token']

bot = discord.Bot()

img = Image.open(directoryPath + "\\images\\bg.jpg")
img = img.resize((3000, 3000))
img.save(directoryPath + "\\images\\bg.jpg")

@bot.event
async def on_ready():
    print("ready")


@bot.slash_command(name='test', description='test', guild_ids=[756058242781806703])
async def test(ctx):
    await ctx.defer()
    image = IA.draw_grid_over_image(directoryPath + "\\images\\bg.jpg")
    image.savefig(directoryPath + "\\images\\grid.jpg")
    img = discord.File(directoryPath + "\\images\\grid.jpg")
    await ctx.respond(file=img)

bot.run(token)
