import pytest

from rstt import BasicPlayer
import random

NB = 20

numb_params = {}
numbers = list(map(str, range(NB)))
def numb_gen(): return numbers.pop(0)


concat_params = {'char1': 'aaa_', 'char2': ':_zzz'}
def concat_letters(char1, char2): return char1+char2


naming_tests = [(numb_gen, numb_params), (concat_letters, concat_params)]

list_params = {}
levels = list(range(NB))
def list_levels(): return levels.pop(0)


gauss = {'mu': 1000, 'sigma': 100}
gamma = {'alpha': 50, 'beta': 100}
level_tests = [(list_levels, list_params),
               (random.gauss, gauss),
               (random.gammavariate, gamma)]

seeded_tests = [(0, 100), (600, 10)]
# --- TESTS --- #


def test_player_level(level=1500):
    player = BasicPlayer('test', level)
    assert player.level() == level


def test_player_name(name='test'):
    player = BasicPlayer(name, 1500)
    assert player.name() == name


def test_create_nb():
    pop = BasicPlayer.create(nb=NB)
    assert len(set(pop)) == NB


@pytest.mark.parametrize('generator, parameters', naming_tests)
def test_create_name_gen_params(generator, parameters):
    pop = BasicPlayer.create(nb=NB, name_gen=generator, name_params=parameters)
    assert len(set(pop)) == NB


@pytest.mark.parametrize('distribution, parameters', level_tests)
def test_create_level_dist_params(distribution, parameters):
    pop = BasicPlayer.create(
        nb=NB, level_dist=distribution, level_params=parameters)
    assert len(set(pop)) == NB


@pytest.mark.parametrize('start, inc', seeded_tests)
def test_seeded_players(start, inc):
    pop = BasicPlayer.seeded_players(NB, start, inc)
    assert len(set(pop)) == NB
    assert len(set([p.name() for p in pop])) == NB
    assert len(set([p.level() for p in pop])) == NB
