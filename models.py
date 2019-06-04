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
