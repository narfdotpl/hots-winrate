from api import *


games = load_games(owner="jhgrng")

print_synergies(games, at_least=10)
print_counters(games, at_least=10)
print_heroes_by_map(games, at_least=10)

print "## Pairs with Ziom\n"
Ziom = teammate.player("plasticbag")
print games.by_pairs(Ziom).at_least(5)
print
print

print "## After Paradox coaching\n"
print games.filter(after(date(2019, 7, 24))).by_owner_hero()
