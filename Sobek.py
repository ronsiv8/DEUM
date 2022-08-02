import Player


class Sobek:
    myPlayer: Player.player

    def __init__(self, x: int, y: int):
        self.myPlayer = Player.player(3000, x, y)
