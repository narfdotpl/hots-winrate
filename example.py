from api import *


all_games = load_games(owner="narf")
back_to_SL = date(2019, 7, 15)
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

print '## Pairs\n'
for name in ["plasticbag", "jhgrng", "barcode", "Tuddels"]:
    s = str(since_back_to_SL.by_pairs(teammate_name=name).at_least(5))
    if s:
        print s
print

print_days_of_the_week(since_back_to_SL)
print_week_by_week(all_games)
