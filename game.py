import discord.ext.commands.context


class Game():
    id: int
    creator: int
    players: list[int]
    ctx: discord.ext.commands.context
    lengthX: int
    lengthY: int

    def __init__(self, id, creator, players, ctx, lengthX, lengthY):
        self.id = id
        self.creator = creator
        self.players = players
        self.ctx = ctx
        self.lengthX = lengthX
        self.lengthY = lengthY
