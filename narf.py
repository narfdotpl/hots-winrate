from api import *


all_games = load_games(owner="narf")
back_to_SL = date(2019, 7, 15)
season1 = date(2019, 8, 6)
since_back_to_SL = all_games.filter(since(back_to_SL))

games = all_games.filter(as_("Sylvanas"))

print '## Overall Sylvanas winrate\n'
print games
print
print

at_least = 10
print_synergies(games, at_least)
print_counters(games, at_least)

print '## Maps\n'
print games.by_map().at_least(at_least)
print

print_days_of_the_week(since_back_to_SL)

print "## Just after work\n"

def after_work(game):
    dt = game.started_at
    is_workday = dt.date().weekday() < 5
    time = (dt.hour, dt.minute)
    return is_workday and (16, 45) <= time <= (17, 45)

print since_back_to_SL.filter(after_work)
print
print

print_week_by_week(all_games)
print

print '## Sylvanas party\n'

def get_party_keys(game):
    names = [
        "jhgrng", "barcode",
        "plasticbag", "plasticbox",
        "dekusss",
        "Thax",
        "Tuddels", "Vesetoth",
    ]
    predicates = map(teammate.player, names)
    solo = reduce((lambda p1, p2: p1 & ~p2), predicates, Predicate(lambda _: True))

    for (key, predicate) in zip(names, predicates) + [("solo", solo)]:
        if predicate(game):
            yield key

print all_games.filter(since(season1) & as_("Sylvanas")).by(get_keys=get_party_keys)