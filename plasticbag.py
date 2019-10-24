from api import *


games = load_games(owner="plasticbag")

print_synergies(games, at_least=10)
print_counters(games, at_least=10)
print_heroes_by_map(games, at_least=10)
print_days_of_the_week(games)
print_week_by_week(games)

print "## Pairs with narf\n"
narf = teammate.player("narf")
print games.by_pairs(narf).at_least(5)
print
print

print '## Party\n'
print games.by_friends([
    "narf",
    "jhgrng", "barcode",
    "dekusss",
    "Thax",
    "Tuddels", "Vesetoth",
])
