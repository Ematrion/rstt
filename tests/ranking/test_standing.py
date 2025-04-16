import pytest


from rstt import Player
from rstt.ranking import Standing, BTRanking

from collections import namedtuple

# TODO: add test for decorator, and decorated methods (sorting done properly)

# default params
pop = [Player(name=f"player_{i}", level=1500) for i in range(3)]
vals = [30, 20, 10]
indices = [0, 1, 2]

# basic standing
standing = Standing()
standing.add(pop, vals)

# make it to namedtuple
RankedPlayer = namedtuple('RankedPlayer', ['index', 'player', 'value'])
rankedpop = [RankedPlayer._make(triplet)
             for triplet in zip(indices, pop, vals)]
p0, p1, p2 = rankedpop


def test_add_error():
    with pytest.raises(KeyError):
        standing.add([p0.player])


def test_keys():
    assert set(pop) == set(standing.keys())


def test_values():
    assert set(vals) == set(standing.values())


def test_items():
    keys_vals = [(p.player, p.value) for p in rankedpop]
    assert set(keys_vals) == set(standing.items())


def test_keys_order():
    assert pop == standing.keys()


def test_values_order():
    assert vals == standing.values()


def test_items_order():
    assert vals == standing.values()


def test_value(val=1500):
    stand = Standing()
    stand.add([p0.player], [p0.value])
    assert stand.value(p0.player) == p0.value


def test_value_error():
    stand = Standing()
    with pytest.raises(ValueError):
        stand.value(p0.player)


def test_default_value(default=10):
    stand = Standing(default=default)
    stand.add([p0.player])
    assert stand.value(p0.player) == default


def test_upper_value(upper=1500):
    stand = Standing(upper=upper)
    stand.add([p0.player], [upper+1])
    assert stand.value(p0.player) == upper


def test_lower_value(lower=1500):
    stand = Standing(lower=lower)
    stand.add([p0.player], [lower-1])
    assert stand.value(p0.player) == lower


def test_index():
    assert standing.index(p1.player) == p1.index


def test_index_error():
    stand = Standing()
    stand.add([p0.player, p1.player])
    with pytest.raises(ValueError):
        stand.index(p2.player)


def test_insert(index=0):
    stand = Standing()
    stand.add([p0.player, p1.player], [1000, 2000])
    stand.insert(index=index, key=p2.player)
    assert stand.index(p2.player) == index


def test_pop_by_index():
    stand = Standing()
    stand.add(pop, vals)
    assert stand.pop(p2.index) == p2.player


def test_pop_by_player():
    stand = Standing()
    stand.add(pop, vals)
    assert stand.pop(p2.player) == p2.index


def test_pop_by_list():
    stand = Standing()
    stand.add(pop, vals)
    assert stand.pop([p0.index, p2.index]) == [p0.player, p2.player]


def test_pop_by_players():
    stand = Standing()
    stand.add(pop, vals)
    assert stand.pop([p0.player, p2.player]) == [p0.index, p2.index]


def test_dict_player_index():
    assert standing[p0.player] == p0.index


def test_dict_list_player():
    assert standing[p0.index] == p0.player


def test_contain():
    assert p0.player in standing


def test_iter():
    for ps, p in zip(standing, pop):
        assert ps == p


def test_percentile():
    # test for a hundred entries
    players = Player.create(nb=100)
    stand = Standing()
    stand.add(players, [player.level() for player in players])
    gt = BTRanking(players=players)
    for i in range(0, 100):
        assert stand.percentile(gt[i]) == (i+1)/100 * 100.00
