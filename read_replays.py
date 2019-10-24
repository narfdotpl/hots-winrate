from os.path import basename, dirname, exists, join, realpath, splitext

import datetime
import json
import multiprocessing
import os
import pickle
import platform
import re
import subprocess
import sys

from constants import game_modes
from models import Player, SerializedData, SerializedGame


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


def get_creation_time(replay_path):
    return datetime.datetime.fromtimestamp(os.path.getctime(replay_path))


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
    if started_at is None:
        started_at = get_creation_time(replay_path)

    return SerializedGame(players=players, map=map, started_at=started_at)


if __name__ == '__main__':
    # load old games first
    path = PICKLED_DATA_PATH
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = pickle.load(f)
    else:
        data = SerializedData()

    # only add games with new paths
    old_paths = data.paths
    all_paths = set(get_replay_paths())
    new_paths = all_paths - old_paths
    if not new_paths:
        exit(0)

    data.paths = all_paths

    # process replays in parallel, but only on macOS
    is_macOS = platform.system() == 'Darwin'
    is_parallel = is_macOS
    if is_parallel:
        with multiprocessing.Manager() as manager:
            games = manager.list()

            def append_game(path):
                print path
                game = get_game(path)
                if game:
                    games.append(game)

            pool = multiprocessing.Pool(multiprocessing.cpu_count())
            pool.map(append_game, sorted(new_paths))
            pool.terminate()

            data.games += games
    else:
        def print_and_get_game(path):
            print path
            return get_game(path)

        data.games += filter(None, map(print_and_get_game, sorted(new_paths)))

    # keep order
    data.games = sorted(data.games, key=lambda g: g.started_at)

    # save
    with open(path, 'wb') as f:
        pickle.dump(data, f)
        print 'Saved data to', path
