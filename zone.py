from Player import player


class zone:
    myPlayer: player
    isBattle: bool
    isClosed: bool

    def __init__(self):
        self.myPlayer = None
        self.isBattle = False
        self.isClosed = False

    def isOccupied(self):
        return self.myPlayer is not None
