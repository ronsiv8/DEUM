import discord
import os

import game

try:
    from PIL import Image
except ImportError:
    import Image

from imageActions import crop_points


class zone:
    myPlayer = None  # its a Player, cannot add because of circular dependency
    isBattle: bool
    isClosed: bool
    myEvent = None

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

        def __init__(self, Game: game, x: int, y: int):
            directoryPath = os.path.dirname(os.path.realpath(__file__))
            img = Image.open(directoryPath + "/games/" + str(Game.id) + "/map.png")
            img.paste(Image.open(directoryPath + "/images/sunOrb.png").convert("RGBA"), (x * 300, y * 300),
                      mask=Image.open(directoryPath + "/images/sunOrb.png").convert("RGBA"))
            img.save(directoryPath + "/games/" + str(Game.id) + "/map.png")
            print(str(x+1)+", "+str(y+1))

        def ActivateEvent(self, plyer):
            if plyer.hero.heroName == "Ra":
                plyer.hero.heroObject.SunOrbs += 1
                plyer.s.DamageDealtMultiplier += 0.1
                plyer.s.abilityCooldowns[3] -= 1
                if plyer.hero.heroObject.SunOrbs<=1:
                    return "Ra has collected a sun orb! its still not too late to stop him..."
                elif plyer.hero.heroObject.SunOrbs<=3:
                    return "Ra has collected a sun orb! he is getting stronger..."
                elif plyer.hero.heroObject.SunOrbs<=5:
                    return "Ra has collected a sun orb! the power of the sun is unleashed!"
                else:
                    return "Ra has collected a sun orb! Ċ̸̨̙̻̻̞̇͐́͝O̶̩̞̬̯̫̣̍W̴̡̳̩̮̍̇͝E̴̬̯̮̒̀͋ͅͅṘ̵͇̦̣̝̟̹̜́̍̆̕"

    def __init__(self, EventName: str, Zone: zone, Game: game, x: int, y: int):
        self.eventName = EventName
        self.eventObject = {
            "sunOrb": self.sunOrb(Game, x, y),
        }.get(self.eventName)
        Zone.myEvent = self
