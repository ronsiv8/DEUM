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

    def event(self, name):
        return event(name, self)


class event:
    eventName: str
    eventObject: None
    imageDirectory = None
    myZone = None

    class sunOrb:
        imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\sunOrb.png"
        myEvent = None

        def __init__(self, given):
            self.imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\sunOrb.png"
            self.myEvent = given

        async def ActivateEvent(self, plyer):
            if plyer.hero.heroName == "Ra":
                self.myEvent.myZone.myEvent = None
                plyer.hero.heroObject.SunOrbs += 1
                plyer.s.DamageDealtMultiplier += 0.1
                plyer.s.abilityCooldowns[3] -= 1
                if plyer.hero.heroObject.SunOrbs <= 1:
                    return "Ra has collected a sun orb! its still not too late to stop him..."
                elif plyer.hero.heroObject.SunOrbs <= 3:
                    return "Ra has collected a sun orb! he is getting stronger..."
                elif plyer.hero.heroObject.SunOrbs <= 5:
                    return "Ra has collected a sun orb! the power of the sun is unleashed!"
                else:
                    plyer.hero.heroObject.coolDowns['ult'] = 0
                    return "Ra has collected a sun orb! ,̶̜̳͛͠ ̴͍̹͎̉͠F̷͍̐Ō̷͔̂R̷̤̫͔̆ ̵̢̛̌̂Ṱ̷̬̺͗̀̓H̵̜̻͈͋̂E̶̼̜͑͜ ̴̢̻͔͝S̷̥̘͝Ứ̴̙̗͜N̵̖̱̜̐̉ ̵̫͖̂́́G̵͍̐̒Ǫ̶̂̃͑D̵̢͔̲͐̈́̓ ̵̘̭̅̂̍İ̶̘Ş̷̠͓̒ ̷̘͐͐̈́C̶̼̽ͅͅỎ̶̢̥̼̾M̴͓̈̌̕Ị̴̥̲͠N̸͔̦͋͝G̴̢͌̑ ̷̩̏T̷̻̱̬̋Õ̷͓̔ ̴̞̝̀̏̽R̴̖̗̂͝E̶̥͍͚͌̈́̊Ả̵̛͉̯P̷̲̗̐ "
            else:
                self.myEvent.myZone.myEvent = None
                return "Ra internally screams at the sight of a precious sun orb being destroyed..."

    class stranger:
        imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\Stranger.png"
        myEvent = None

        def __init__(self, given):
            self.imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\Stranger.png"
            self.myEvent = given

        async def ActivateEvent(self, plyer):
            self.myEvent.myZone.myEvent = None
            view = discord.ui.View()
            button = discord.ui.Button(label="Sacrifice For Speed", custom_id="sacrifice speed",
                                       style=discord.ButtonStyle.red)
            button2 = discord.ui.Button(label="Sacrifice For Power", custom_id="sacrifice damage",
                                        style=discord.ButtonStyle.red)
            button3 = discord.ui.Button(label="Sacrifice For Resistance", custom_id="sacrifice resistance",
                                        style=discord.ButtonStyle.red)
            button4 = discord.ui.Button(label="Reject the offer", custom_id="reject", style=discord.ButtonStyle.green)

            async def callback(interaction):
                choice = interaction.data['custom_id']
                choice = choice.split(" ")
                if choice[0] != "sacrifice":
                    await ctx.send("You say that you appreciate the offer, but you don't want to take it.")
                    await msg.delete()
                    return
                healthSacrifice = plyer.s.currentHP * 0.1
                plyer.s.currentHP -= healthSacrifice
                if choice[1] == "speed":
                    plyer.s.speedProgress += 0.5
                    additional = "Progress towards speed increased by 50%!"
                elif choice[1] == "damage":
                    plyer.s.DamageDealtMultiplier += 0.3
                    additional = "Damage dealt increased by 30%!"
                elif choice[1] == "resistance":
                    additional = "Resistance increased by 10%!"
                    plyer.s.DamageTakenMultiplier -= 0.1

                await ctx.send(
                    "You feel a sharp pain.. You lost " + str(healthSacrifice) + " HP but gained stats! " + additional,
                    delete_after=5)
                await plyer.checkProgression()
                await msg.delete()

            button.callback = callback
            button2.callback = callback
            button3.callback = callback
            button4.callback = callback

            view.add_item(button)
            view.add_item(button2)
            view.add_item(button3)
            view.add_item(button4)

            ctx = plyer.myGame.ctx
            msg = await ctx.send("A stranger approaches " + plyer.hero.heroName + " and offers help.. "
                                                                                  "\n _You see,_ he claims, _I can give you power... but I require... a sacrifice._",
                                 view=view)
            return False

    class brawl:
        imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\brawl.png"
        myEvent = None

        def __init__(self, given):
            self.imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\brawl.png"
            self.myEvent = given

        async def ActivateEvent(self, plyer):
            self.myEvent.myZone.myEvent = None
            plyer.myGame.battleTurnLimit += 1
            return "You pass through a brawl. It inspires you to fight longer! " \
                   "The attack turns limit is increased by 1!"

    class healershut:
        imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\healershut.png"
        myEvent = None

        def __init__(self, given):
            self.imageDirectory = os.path.dirname(os.path.realpath(__file__)) + "\\images\\healershut.png"
            self.myEvent = given

        async def ActivateEvent(self, plyer):
            self.myEvent.myZone.myEvent = None
            plyer.s.currentHP += plyer.s.maxHP * 0.1
            if plyer.s.currentHP > plyer.s.maxHP:
                plyer.s.currentHP = plyer.s.maxHP
            return "You find a healer's hut and heal for 10% of your max HP!"

    def __init__(self, EventName: str, myZone):
        self.eventName = EventName
        possible = {
            "sunOrb": self.sunOrb,
            "Stranger": self.stranger,
            "brawl": self.brawl,
            "healershut": self.healershut
        }
        self.myZone = myZone
        self.eventObject = possible[EventName](self)
        print("zone now has event")
