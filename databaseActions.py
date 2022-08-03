import os
import sqlite3
from game import Game

directoryPath = os.path.dirname(os.path.realpath(__file__))
conn = sqlite3.connect(directoryPath + "/database/main.db")
cursor = conn.cursor()


def add_game(game: Game):
    cursor.execute("INSERT INTO games VALUES (" + str(game.id) + ", " + str(game.creator) + "," + repr('|'.join(
        str(item) for item in game.players))
                   + "," + str(game.lengthX) + ", " + str(game.lengthY) + ")")
    conn.commit()
