import io
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np

try:
    from PIL import Image
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


def draw_grid_over_image_with_players(filename, players):
    directoryPath = os.path.dirname(os.path.realpath(filename))
    # get the grid image
    originalGrid = draw_grid_over_image(filename)
    # get directory of filename
    # save to disk where filename directory is
    originalGrid.savefig(directoryPath + "/grid.png")
    gridOriginal = Image.open(directoryPath + "/grid.png")
    gridCopy = gridOriginal.copy()
    print(gridOriginal)
    for player in players:
        gridCopy.paste(player.hero.image, (player.s.posX * 300, player.s.posY * 300))
    gridCopy.save(directoryPath + "/map.png")


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
