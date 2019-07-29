# encoding: utf-8


class Player:
    def __init__(self, name, hero, team, did_win):
        # TODO: remove encoding hacks
        if hero == u'LÃºcio':
            hero = 'Lucio'

        self.name = name
        self.hero = hero
        self.team = team
        self.did_win = did_win



class SerializedGame:
    def __init__(self, players, map, started_at):
        self.players = players
        self.map = map
        self.started_at = started_at


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

    def by_owner_hero(self):
        return self.by(get_keys=lambda game: [game.owner.hero])

    def by_enemy_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team != game.owner.team])

    def by_teammate_hero(self):
        return self.by(get_keys=lambda game: [p.hero for p in game.players if p.team == game.owner.team and p != game.owner])

    def by_map(self):
        return self.by(get_keys=lambda game: [game.map])

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
            teammates = [p for p in game.players if p.team == game.owner.team and p != game.owner]
            if teammate_name:
                teammate_hero = [p.hero for p in teammates if p.name == teammate_name][0]
                return ["{} as {} + {} as {}".format(game.owner.name, game.owner.hero, teammate_name, teammate_hero)]
            else:
                return ["{} as {} + {}".format(game.owner.name, game.owner.hero, p.hero) for p in teammates]

        return games.by(get_keys)

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

        if not self:
            return ''

        # store text as rows and columns, so we can fill with spaces and have a nice "table"
        rows = []

        k_wr = [(key, games.winrate) for (key, games) in self.items()]
        for (key, winrate) in sorted(k_wr, key=lambda t: (-t[1].percentage, t[0])):
            rows.append([
                key + ": ", winrate.percentage_text, " (", str(winrate.wins), "/", str(winrate.total), ")"
            ])

        max_widths = [0] * len(rows[0])
        for row in rows:
            widths = map(len, row)
            max_widths = map(max, zip(widths, max_widths))

        lines = []
        for row in rows:
            line = ''
            for (i, (text, max_width)) in enumerate(zip(row, max_widths)):
                width = len(text)
                fill = ' ' * (max_width - width)
                if i == 0:
                    line += text + fill
                else:
                    line += fill + text

            lines.append(line)

        return '\n'.join(lines)


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

    def __str__(self):
        return '{} ({}/{})'.format(self.percentage_text, self.wins, self.total)


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
