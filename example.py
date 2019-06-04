from api import *


games = load_games(owner="narf")  # use your name

print "All games:", games
print

print "Fenix games:", games.filter(lambda game: game.owner.hero == "Fenix")
print "Fenix games:", games.filter(owner.hero("Fenix"))
print "Fenix games:", games.filter(as_("Fenix"))
print

print "Fenix + Guldan games:", games.filter(as_("Fenix") & with_("Gul'dan"))
print "Greymane + Guldan games:", games.filter(as_("Greymane") & with_("Gul'dan"))
print "Other + Guldan matches:", games.filter(~(as_("Fenix") | as_("Greymane")) & with_("Gul'dan"))
print

print "Fenix vs Varian:", games.filter(as_("Fenix") & vs("Varian"))
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
