from api import *


games = load_games(owner="narf")  # use your name

print "All games:", games
print

print "Fenix games:", games.filter(lambda game: game.owner.hero == "Fenix")
print "Fenix games:", games.filter(owner.hero("Fenix"))
print "Fenix games:", games.filter(as_("Fenix"))
print

fenix_games = games.filter(as_("Fenix"))
print "Fenix games by teammate:"
print fenix_games.by_teammate_hero.at_least(3)
print

print "Fenix games by enemy:"
print fenix_games.by_enemy_hero.at_least(3)
print

print "All games by enemy:"
print games.by_enemy_hero.at_least(5)
print

print "Fenix + Guldan games:", games.filter(as_("Fenix") & with_("Gul'dan"))
print "Greymane + Guldan games:", games.filter(as_("Greymane") & with_("Gul'dan"))
print "Other + Guldan matches:", games.filter(~(as_("Fenix") | as_("Greymane")) & with_("Gul'dan"))
print

print "Fenix vs Varian:", games.filter(as_("Fenix") & vs("Varian"))
print "vs Varian:"
print games.filter(vs("Varian")).by_owner_hero
print

Filip = teammate.player("jhgrng")
Ziom = teammate.player("plasticbag")
print "z Filipem i Ziomem:", games.filter(Filip & Ziom)
print "tylko z Filipem:", games.filter(Filip & ~Ziom)
print "tylko z Ziomem:", games.filter(Ziom & ~Filip)
print "bez chlopakow:", games.filter(~Ziom & ~Filip)
print

print "z Filipem jako Guldanem:", games.filter(Filip.as_("Gul'dan"))
print "z Ziomem jako Guldanem:", games.filter(Ziom.as_("Gul'dan"))
