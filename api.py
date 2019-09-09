import datetime
import os
import pickle

from constants import maps
from models import Game, GameList, OwnerPredicate, PlayerPredicate, Predicate, align_rows
from read_replays import PICKLED_DATA_PATH


def load_games(owner, path=PICKLED_DATA_PATH, verbose=True):
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

    has_owner = lambda game: any(player.name == owner for player in game.players)
    filtered = filter(has_owner, serialized_games)
    games = GameList(Game(g.players, g.map, g.started_at, owner) for g in filtered)

    if verbose:
        print "Loaded {} Storm League games with owner {}.\n".format(len(games), owner)

    return games


def map_(map):
    return lambda game: game.map == map

on = map_

owner = OwnerPredicate()
teammate = PlayerPredicate(is_owner_teammate=True)
enemy = PlayerPredicate(is_owner_teammate=False)

as_ = owner.hero
with_ = teammate.hero
vs = enemy.hero


date = datetime.date
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)


def before(date):
    return Predicate(lambda game: game.started_at.date() < date)


def after(date):
    return Predicate(lambda game: date < game.started_at.date())


def since(date=None, days=0, weeks=0):
    if date is None:
        date = today - datetime.timedelta(days=days, weeks=weeks)

    return after(date - datetime.timedelta(days=1))


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


def print_days_of_the_week(games):
    print "## Win rate by day of the week\n"

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    get_week_day = lambda game: game.started_at.date().weekday()
    print games.by(lambda g: [day_names[get_week_day(g)]]).sorted_by_keys(day_names)

    is_weekend = lambda n: n >= 5
    names = ['work day', 'weekend']
    to_name = lambda n: names[int(is_weekend(n))]
    print games.by(lambda game: [to_name(get_week_day(game))]).sorted_by_keys(names)
    print


def print_week_by_week(games, start_date=date(2019, 7, 15), end_date=today):
    print "## Win rate week by week\n"

    rows = []

    diff_total = 0
    week = datetime.timedelta(days=7)
    date = start_date

    while date <= end_date:
        period_games = games.filter(since(date) & before(date + week))

        wr = period_games.winrate
        diff = wr.wins - wr.loses
        diff_total += diff

        rows.append(map(str, [
            date.isoformat(),
            ": ",

            "-" if diff < 0 else (" " if diff == 0 else "+"),
            abs(diff),
            ", ",

            wr.percentage_text,
            " (",
            wr.wins,
            "/",
            wr.total,
            ") ",

            "-" * abs(diff_total) if diff_total < 0 else "",
            "+" * diff_total if diff_total > 0 else "",
        ]))
        date += week

    print align_rows(rows, is_column_left_aligned=lambda i: i == 0 or i == len(rows[0]) - 1)
