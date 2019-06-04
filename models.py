# encoding: utf-8
class Player:
    def __init__(self, name, hero, team, did_win):
        self.name = name
        self.hero = hero
        self.team = team
        self.did_win = did_win



class SerializedGame:
    def __init__(self, players, map):
        self.players = players
        self.map = map


class Game:
    def __init__(self, players, map, owner_name):
        self.players = players
        self.map = map
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

    def by(self, get_keys):
        dct = DictWithGames()
        for game in self:
            keys = get_keys(game)
            for key in keys:
                if key in dct:
                    dct[key].append(game)
                else:
                    dct[key] = GameList([game])

        return dct

    @property
    def by_owner_hero(self):
        return self.by(get_keys=lambda game: [game.owner.hero])

    @property
    def by_enemy_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team != game.owner.team])

    @property
    def by_teammate_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team == game.owner.team and p != game.owner])

    @property
    def by_map(self):
        return self.by(get_keys=lambda game: [game.map])

    @property
    def winrate(self):
        wins = self.filter(lambda game: game.owner.did_win)
        return WinRate(wins=len(wins), total=len(self))

    def __str__(self):
        return str(self.winrate)


class DictWithGames(dict):
    """
    Type: Dict[str, GameList]
    """

    def at_least(self, n):
        return DictWithGames((key, games) for (key, games) in self.items() if len(games) >= n)

    def __str__(self):
        """
        Items sorted by descending win rate.
        """

        lines = []
        k_wr = [(key, games.winrate) for (key, games) in self.items()]
        for (key, winrate) in sorted(k_wr, key=lambda t: (-t[1].percentage, t[0])):
            # TODO: remove encoding hacks
            if key == u'LÃºcio':
                key = 'Lucio'

            lines.append("{}: {}".format(key.decode('utf8'), winrate))

        return '\n'.join(lines)


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
