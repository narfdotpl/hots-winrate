from os.path import basename, dirname, exists, join, realpath, splitext

import datetime
import json
import multiprocessing
import os
import pickle
import re
import subprocess
import sys

from constants import game_modes
from models import Player, SerializedGame


CURRENT_DIR = dirname(realpath(__file__))
PROTOCOL_DIR = join(CURRENT_DIR, 'heroprotocol')
PICKLED_DATA_PATH = join(CURRENT_DIR, 'data')


def get_stdout(arguments):
    command = ['python', join(PROTOCOL_DIR, 'heroprotocol.py')] + arguments
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    return proc.stdout


def get_replays_dir():
    symlink_path = join(CURRENT_DIR, 'replays')
    if exists(symlink_path):
        return symlink_path

    if len(sys.argv) != 2:
        print """
Please provide a path to HotS replay directory:

    python read_replays.py /my/path/to/hots/replays

or symlink it as `replays`:

    ln -s /my/path/to/hots/replays replays
    python read_replays.py
        """.strip()
        exit(1)

    return sys.argv[1]


def get_replay_paths():
    replay_dir = get_replays_dir()
    for name in os.listdir(replay_dir):
        if name.endswith('.StormReplay'):
            yield join(replay_dir, name)


map_re = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}.\d{2}.\d{2})? ?([\w ]+\w)( \(\d+\))?')
def get_map_and_datetime(replay_path):
    # I'm using the name from the filename to get the map name :facepalm:
    # because attributes in the replay are a mess
    # and I don't want to go through all the game events.
    name = basename(replay_path)
    match = map_re.match(name)
    (dt_string, map, index) = match.groups()

    if dt_string:
        dt = datetime.datetime.strptime(dt_string, '%Y-%m-%d %H.%M.%S')
    else:
        dt = None

    return (map, dt)


def get_game(replay_path):
    stdout = get_stdout(['--initdata', '--json', replay_path])
    stdout.next()
    init = json.loads(stdout.next())
    game_mode = init['m_syncLobbyState']['m_gameDescription']['m_gameOptions']['m_ammId']
    if game_mode != game_modes.storm_league:
        return None

    stdout = get_stdout(['--details', '--json', replay_path])
    details = json.loads(stdout.next())
    players = [Player(
        name=d['m_name'],
        hero=d['m_hero'],
        team=d['m_teamId'],
        did_win=d['m_result'] == 1,
    ) for d in details['m_playerList']]

    (map, started_at) = get_map_and_datetime(replay_path)

    return SerializedGame(players=players, map=map)


if __name__ == '__main__':
    # process replays in parallel
    with multiprocessing.Manager() as manager:
        games = manager.list()

        def append_game(path):
            print path
            game = get_game(path)
            if game:
                games.append(game)

        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map(append_game, sorted(get_replay_paths()))
        pool.terminate()

        path = PICKLED_DATA_PATH
        with open(path, 'wb') as f:
            pickle.dump(list(games), f)
            print 'Saved data to', path
