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
        self.percentage = float(wins) / total

    def __str__(self):
        return '{}% ({}/{})'.format(int(round(100 * self.percentage)), self.wins, self.total)
