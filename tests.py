import datetime

from read_replays import get_map_and_datetime


def test_parses_path_without_date():
    path = 'foo/bar/Alterac Pass (10).StormReplay'
    (map, dt) = get_map_and_datetime(path)
    assert map == 'Alterac Pass'
    assert dt is None


def test_parses_path_with_date():
    path = 'foo/bar/2019-07-28 22.23.26 Cursed Hollow.StormReplay'
    (map, dt) = get_map_and_datetime(path)
    assert map == 'Cursed Hollow'
    assert dt == datetime.datetime(2019, 7, 28, 22, 23, 26)
