class Player:
    def __init__(self, name, hero, team, did_win):
        self.name = name
        self.hero = hero
        self.team = team
        self.did_win = did_win



class SerializedGame:
    def __init__(self, players):
        self.players = players


class Game:
    def __init__(self, players, owner_name):
        self.players = players
        self.owner = None

        for player in players:
            if player.name == owner_name:
                self.owner = player
                break
        else:  # no break
            raise ValueError('Couldn\'t find player called "{}".'.format(owner_name))


class GameList(list):
    def filter(self, predicate):
        return GameList(filter(predicate, self))

    @property
    def winrate(self):
        wins = self.filter(lambda game: game.owner.did_win)
        return WinRate(wins=len(wins), total=len(self))

    def __str__(self):
        return str(self.winrate)


class WinRate:
    def __init__(self, wins, total):
        self.wins = wins
        self.total = total

        if total == 0:
            self.percentage = 0.0
        else:
            self.percentage = float(wins) / total

    def __str__(self):
        return '{}% ({}/{})'.format(int(round(100 * self.percentage)), self.wins, self.total)


class Predicate:
    def __init__(self, func):
        self.func = func

    def __call__(self, x):
        return self.func(x)

    def __and__(self, other):
        return Predicate(lambda x: self(x) and other(x))

    def __or__(self, other):
        return Predicate(lambda x: self(x) or other(x))

    def __invert__(self):
        return Predicate(lambda x: not self(x))


class OwnerPredicate(Predicate):
    def __init__(self, hero=None):
        self._hero = hero

    def hero(self, hero):
        return OwnerPredicate(hero)

    def __call__(self, game):
        assert self._hero is not None
        return game.owner.hero == self._hero


class PlayerPredicate(Predicate):
    def __init__(self, is_owner_teammate, name=None, hero=None):
        self._is_owner_teammate = is_owner_teammate
        self._name = name
        self._hero = hero

    def player(self, name):
        return PlayerPredicate(self._is_owner_teammate, name, self._hero)

    def hero(self, hero):
        return PlayerPredicate(self._is_owner_teammate, self._name, hero)

    def as_(self, hero):
        return self.hero(hero)

    def __call__(self, game):
        assert self._name is not None or self._hero is not None, "You have to provide either a hero or a player name."
        return any(
            (p.team == game.owner.team) == self._is_owner_teammate
            and self._name in [None, p.name]
            and self._hero in [None, p.hero]
            for p in game.players
        )
