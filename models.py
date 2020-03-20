# encoding: utf-8

import text


AVERAGE_KEY = 'AVERAGE'


class Player:
    def __init__(self, name, hero, team, party, did_win):
        # TODO: remove encoding hacks
        if hero == u'LÃºcio':
            hero = 'Lucio'

        self.name = name
        self.hero = hero
        self.team = team
        self.party = party
        self.did_win = did_win

    def __repr__(self):
        return '<Player: {}>'.format(str(self))

    def __str__(self):
        return '{name} as {hero}'.format(**vars(self))


class SerializedGame:
    def __init__(self, players, map, started_at):
        self.players = players
        self.map = map
        self.started_at = started_at


class SerializedData:
    def __init__(self, paths=None, games=None):
        self.paths = paths or set()
        self.games = games or list()


class Game:
    def __init__(self, players, map, started_at, owner_name):
        self.players = players
        self.map = map
        self.started_at = started_at
        self.owner = None

        for player in players:
            if player.name == owner_name:
                self.owner = player
                break
        else:  # no break
            raise ValueError('Couldn\'t find player called "{}".'.format(owner_name))

    @property
    def teammates(self):
        """
        Teammates of the owner.
        """
        return [p for p in self.players if p.team == self.owner.team and p != self.owner]

    @property
    def enemies(self):
        """
        Enemies of the owner.
        """
        return [p for p in self.players if p.team != self.owner.team]

    @property
    def party(self):
        """
        Players in a party with the owner.
        """
        return [p for p in self.teammates if p.party is not None and p.party == self.owner.party]

    def __str__(self):
        result = 'win' if self.owner.did_win else 'loss'
        return '{} ({})'.format(self.map, result)


class GameList(list):
    def filter(self, predicate):
        return GameList(filter(predicate, self))

    def by(self, get_keys, including_average=False):
        dct = DictWithGames()
        for game in self:
            keys = get_keys(game)
            for key in keys:
                if key in dct:
                    dct[key].append(game)
                else:
                    dct[key] = GameList([game])

        if dct and including_average:
            dct[AVERAGE_KEY] = self

        return dct

    def by_owner_hero(self):
        return self.by(get_keys=lambda game: [game.owner.hero])

    def by_enemy_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team != game.owner.team],
                       including_average=True)

    def by_teammate_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team == game.owner.team and p != game.owner],
                       including_average=True)

    def by_hero(self, hero):
        def get_keys(game):
            for p in game.players:
                if p.hero == hero:
                    if p.team == game.owner.team:
                        yield 'with ' + hero
                    else:
                        yield 'vs ' + hero

        return self.by(get_keys=get_keys, including_average=True)

    def by_map(self, including_average=True):
        return self.by(get_keys=lambda game: [game.map],
                       including_average=including_average)

    def by_pairs(self, teammate_predicate=None, teammate_name=None):
        if teammate_name:
            teammate_predicate = PlayerPredicate(is_owner_teammate=True, name=teammate_name)
        elif teammate_predicate:
            teammate_name = teammate_predicate._name

        if teammate_predicate:
            games = self.filter(teammate_predicate)
        else:
            games = self

        def get_keys(game):
            teammates = game.teammates
            if teammate_name:
                teammate_hero = [p.hero for p in teammates if p.name == teammate_name][0]
                return ["{} as {} + {} as {}".format(game.owner.name, game.owner.hero, teammate_name, teammate_hero)]
            else:
                return ["{} as {} + {}".format(game.owner.name, game.owner.hero, p.hero) for p in teammates]

        return games.by(get_keys)

    def by_hour(self):
        to_key = lambda hour: str(hour).zfill(2) + ":00"
        keys = map(to_key, list(range(6, 24)) + list(range(0, 6)))
        return self.by(get_keys=lambda game: [to_key(game.started_at.hour)]).sorted_by_keys(keys)

    def by_party(self, including_party_size=True, including_player_names=True):
        def get_keys(game):
            # get other players in owner's party
            party = game.party

            keys = []
            if including_player_names:
                keys.extend(p.name for p in party)

            if party:
                if including_party_size:
                    n = len(party) + 1
                    keys.append('party of {}'.format(n))
            else:
                keys.append('solo')

            return keys

        return self.by(get_keys, including_average=True)


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

    SORTING_KEY_ATTRIBUTE = 'sorting_key'

    def at_least(self, n):
        return DictWithGames((key, games) for (key, games) in self.items() if len(games) >= n)

    def get_sorting_key(self):
        # sort by descending winrate by default
        # t = (key, winrate)
        default_key = lambda t: (-t[1].percentage, t[0])
        return getattr(self, self.SORTING_KEY_ATTRIBUTE, default_key)

    def sorted_by(self, key):
        setattr(self, self.SORTING_KEY_ATTRIBUTE, key)
        return self

    def sorted_by_keys(self, keys):
        return self.sorted_by(key=lambda t: keys.index(t[0]))

    def __nonzero__(self):
        keys = self.keys()
        if keys == [] or keys == [AVERAGE_KEY]:
            return False
        else:
            return True

    def __str__(self):
        if not self:
            return ''

        # store text as rows and columns, so we can fill with spaces and have a nice "table"
        rows = []

        k_wr = [(key, games.winrate) for (key, games) in self.items()]
        display_key_for_average = '-' * (1 + max(len(k) for (k, wr) in k_wr if k != AVERAGE_KEY))

        for (key, winrate) in sorted(k_wr, key=self.get_sorting_key()):
            rows.append(map(str, [
                display_key_for_average if key == AVERAGE_KEY else key + ": ",
                winrate.percentage_text,
                " (",
                winrate.wins,
                "/",
                winrate.total,
                ") (",
                winrate.diff_sign,
                abs(winrate.diff),
                ")",
            ]))

        return text.align_rows(rows)


class WinRate:
    def __init__(self, wins, total):
        self.wins = wins
        self.total = total

        if total == 0:
            self.percentage = 0.0
        else:
            self.percentage = float(wins) / total

    @property
    def percentage_text(self):
        return str(int(round(100 * self.percentage))) + "%"

    @property
    def loses(self):
        return self.total - self.wins

    @property
    def diff(self):
        return self.wins - self.loses

    @property
    def diff_sign(self):
        diff = self.diff
        if diff < 0:
            return "-"
        elif diff == 0:
            return ""
        else:
            return "+"

    def __str__(self):
        return '{} ({}/{}) ({}{})'.format(self.percentage_text, self.wins, self.total, self.diff_sign, abs(self.diff))


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
