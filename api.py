import datetime
import os
import pickle

from constants import maps
from models import Game, GameList, OwnerPredicate, PlayerPredicate, Predicate
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

    return GameList(Game(g.players, g.map, g.started_at, owner) for g in serialized_games)


def map_(map):
    return lambda game: game.map == map

on = map_

owner = OwnerPredicate()
teammate = PlayerPredicate(is_owner_teammate=True)
enemy = PlayerPredicate(is_owner_teammate=False)

as_ = owner.hero
with_ = teammate.hero
vs = enemy.hero


def since(date=None, days=0, weeks=0):
    if date is None:
        date = datetime.date.today() - datetime.timedelta(days=days, weeks=weeks)

    return Predicate(lambda game: date <= game.started_at.date())


def print_synergies(games, at_least=3):
    print "## Synergies"
    print

    by_owner = games.by_owner_hero()
    for (owner_hero, games) in sorted(by_owner.items(), key=lambda t: (-t[1].winrate.percentage, t[0])):
        dct = games.by_teammate_hero().at_least(at_least)
        if dct:
            print "When you play as {} with".format(owner_hero)
            print dct
            print

    print


def print_counters(games, at_least=3):
    print "## Targets / Counters"
    print

    by_owner = games.by_owner_hero()
    for (owner_hero, games) in sorted(by_owner.items(), key=lambda t: (-t[1].winrate.percentage, t[0])):
        dct = games.by_enemy_hero().at_least(at_least)
        if dct:
            print "When you play as {} vs".format(owner_hero)
            print dct
            print

    print


def print_heroes_by_map(games, at_least=3):
    print "## Heroes by map"
    print

    by_map = games.by_map()
    for (map, games) in sorted(by_map.items(), key=lambda t: (-t[1].winrate.percentage, t[0])):
        dct = games.by_owner_hero().at_least(at_least)
        if dct:
            print "When you play on {} as".format(map)
            print dct
            print

    print
