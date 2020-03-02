from api import *


all_games = load_games(owner="narf")
back_to_SL = date(2019, 7, 15)
season1 = date(2019, 8, 6)
season2 = date(2019, 12, 5)
since_back_to_SL = all_games.filter(since(back_to_SL))

games = all_games.filter(as_("Sylvanas"))

print text.h2('Overall Sylvanas winrate')
print games
print

at_least = 10
print_synergies(games, at_least)
print_counters(games, at_least)

print text.h2('Maps')
print games.by_map().at_least(at_least)

print_days_of_the_week(since_back_to_SL)

print text.h2("Just after work")

def after_work(game):
    dt = game.started_at
    is_workday = dt.date().weekday() < 5
    time = (dt.hour, dt.minute)
    return is_workday and (16, 45) <= time <= (17, 45)

print since_back_to_SL.filter(after_work)
print

print_week_by_week(all_games)

print text.h2('Last games')
for n in [10, 20, 30, 40, 50]:
    print 'last', n, 'games:', GameList(all_games[-n:])
print

print_streaks(all_games.filter(since(season2)), at_least=4)

print text.h2('Party in season 2')
games = all_games.filter(since(season2))
print games.by_party(including_party_size=False).at_least(5)
print games.by_party(including_player_names=False)

# print text.h2('Solo games')
# print all_games.filter(since(season2) & solo).by_owner_hero()

# print text.h2('With or against')
# for hero in ['Alarak', 'Auriel', 'Azmodan', 'Deathwing', 'Varian']:
#     print all_games.by_hero(hero)

print all_games[-1]
