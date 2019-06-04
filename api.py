import os
import pickle

from models import Game
from read_replays import PICKLED_DATA_PATH


def load_games(owner, path=PICKLED_DATA_PATH):
    if not os.path.exists(path):
        print """
Couldn't find data file: {}
Please run

    python read_replays.py

in order to read replays and prepare data for analysis.
Run this command every time you play new games.
        """.strip().format(path)
        exit(1)

    with open(path, 'rb') as f:
        serialized_games = pickle.load(f)

    return [Game(g.players, owner_name=owner) for g in serialized_games]
