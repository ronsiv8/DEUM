import matplotlib.pyplot as plt
import numpy as np
try:
    from PIL import Image
except ImportError:
    import Image


def draw_grid_over_image(filename):
    """
    Draws a grid over an image.
    """
    img = Image.open(filename)
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, img.size[0], 1))
    ax.set_yticks(np.arange(-.5, img.size[1], 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal')
    # save and return image
    fig.savefig(filename, dpi=300)
    plt.close(fig)
    return img
