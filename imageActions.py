import io
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    import Image


def draw_grid_over_image(filename):
    image = Image.open(filename).copy()
    my_dpi = 500.

    # Set up figure
    fig = plt.figure(figsize=(float(image.size[0]) / my_dpi, float(image.size[1]) / my_dpi), dpi=my_dpi)
    ax = fig.add_subplot(111)

    # Remove whitespace from around the image
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    # Set the gridding interval: here we use the major tick interval
    myInterval = 300.
    loc = plticker.MultipleLocator(base=myInterval)
    ax.xaxis.set_major_locator(loc)
    ax.yaxis.set_major_locator(loc)

    # Add the grid
    ax.grid(which='major', axis='both', linestyle='-', color='r', linewidth=2)

    # Add the image
    ax.imshow(image)

    # Find number of gridsquares in x and y direction
    nx = abs(int(float(ax.get_xlim()[1] - ax.get_xlim()[0]) / float(myInterval)))
    ny = abs(int(float(ax.get_ylim()[1] - ax.get_ylim()[0]) / float(myInterval)))

    # Add some labels to the gridsquares
    for j in range(ny):
        y = j * myInterval + 40
        for i in range(nx):
            x = float(i) * myInterval + 20
            ax.text(x, y, '({0}, {1})'.format(i + 1, j + 1), color='w', ha='left', va='top')

    # Save the figure
    return fig


def draw_grid_over_image_with_players(filename, players, input=False):
    directoryPath = os.path.dirname(os.path.realpath(filename))
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    # check if a grid image already exists
    if not os.path.exists(directoryPath + "/grid.png"):
        # get the grid image
        originalGrid = draw_grid_over_image(filename)
        # get directory of filename
        # save to disk where filename directory is
        originalGrid.savefig(directoryPath + "/grid.png")
    gridOriginal = Image.open(directoryPath + "/grid.png")
    gridCopy = gridOriginal.copy()
    draw = ImageDraw.Draw(gridCopy)
    font = ImageFont.truetype(directoryPath + "/fonts/arial.ttf", 20)
    for player in players:
        if not input:
            gridCopy.paste(player.hero.heroObject.image, (player.s.posX * 300, player.s.posY * 300)) #,mask=player.hero.heroObject.image
        else:
            gridCopy.paste(player.hero.heroObject.image, (player.s.posX * 300, player.s.posY * 300))#mask=player.hero.heroObject.image
        effects = player.s.statusEffects
        count = 0
        for effect in effects:
            # get the image for this effect
            effectImage = Image.open(scriptPath + "/images/icons/" + effect + ".png")
            # paste the image above the player
            gridCopy.paste(effectImage, (player.s.posX * 300 + count * 20, player.s.posY * 300), mask=effectImage)
            draw.text((player.s.posX * 300 + count * 20, player.s.posY * 250), str(effects[effect]['amount']),
                      font=font, fill=(255, 255, 255))
            count += 1
    gridCopy.save(directoryPath + "/map.png")


async def add_checks_to_map(locationArray, gameId, playerX, playerY, abilityChecks = False):
    """
    Receives an array of tuples of locations.
    Adds a checkmark to each location.
    """
    directoryPath = os.path.dirname(os.path.realpath(__file__))
    img = Image.open(directoryPath + "/games/" + str(gameId) + "/map.png")
    if not abilityChecks:
        dotImage = Image.open(directoryPath + "/images/dot.png")
    else:
        dotImage = Image.open(directoryPath + "/images/abilityMove.png")
    for location in locationArray:
        img.paste(dotImage
                  , ((location[0] - 1) * 300 + 125, (location[1] - 1) * 300 + 125),
                  mask=dotImage)
    img.save(directoryPath + "/games/" + str(gameId) + "/map.png")


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_points(pil_img, points):
    img_width, img_height = pil_img.size
    return pil_img.crop(((points[0]),
                         (points[1]),
                         (points[2]),
                         (points[3])))
