import os

from PIL import Image
from imageActions import crop_points


class Sobek:
    myPlayer = None
    image: Image
    maxHP: int = 3000

    def __init__(self, player):
        self.myPlayer = player
        self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\Sobek.png")
        self.image = crop_points(self.image, [9, 165, 309, 465])
        self.myPlayer.s.maxHP = self.maxHP
