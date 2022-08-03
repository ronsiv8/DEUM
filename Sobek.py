import os

import Player
from PIL import Image
from imageActions import crop_points


class Sobek:
    myPlayer: Player.player
    image: Image

    def __init__(self, player: Player.player):
        self.myPlayer = player
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek.png")
        self.image = crop_points(self.image, [9, 165, 309, 465])
