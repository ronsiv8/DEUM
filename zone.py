
class zone:
    myPlayer = None # its a Player, cannot add because of circular dependency
    isBattle: bool
    isClosed: bool

    def __init__(self):
        self.myPlayer = None
        self.isBattle = False
        self.isClosed = False

    def isOccupied(self):
        return self.myPlayer is not None
