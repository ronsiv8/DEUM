import discord
import os

try:
    from PIL import Image
except ImportError:
    import Image

from imageActions import crop_points

class zone:
    myPlayer = None  # its a Player, cannot add because of circular dependency
    isBattle: bool
    isClosed: bool

    def __init__(self):
        self.myPlayer = None
        self.isBattle = False
        self.isClosed = False

    def isOccupied(self):
        return self.myPlayer is not None


class event:
    eventName: str
    eventObject: None

    class sunOrb:
        myzone: zone = None

        def __init__(self, Zone: zone):
            pass
            # self.myzone = Zone
            # self.image = Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\images\\sunOrb.png")
            # img.paste(Image.open(directoryPath + "/images/dot.png").convert("RGBA")
            #           , ((location[0] - 1) * 300 + 125, (location[1] - 1) * 300 + 125),
            #           mask=Image.open(directoryPath + "/images/dot.png").convert("RGBA"))
            # print("work?")
            # print(self.image)

    def __init__(self, EventName: str, Zone: zone):
        self.eventName = EventName
        self.eventObject = {
            "sunOrb": self.sunOrb(Zone),
        }.get(self.eventName)
