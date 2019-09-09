from api import *


games = load_games(owner="narf")#.filter(as_("Sylvanas"))

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

print '## Pairs with Ziom\n'
print games.by_pairs(teammate_name="plasticbag").at_least(5)
print

print_days_of_the_week(games)
print_week_by_week(games)
