import pytest

from rstt import BasicPlayer
import random
import copy

NB = 20

numbers = list(map(str, range(NB)))
def numb_gen(): return numbers.pop(0)


concat_params = {'char1': 'aaa_', 'char2': ':_zzz'}
def concat_letters(char1, char2): return char1+char2


levels1 = list(range(NB))
levels2 = list(range(NB))


# --- TESTS --- #
def test_player_level(level=1500):
    player = BasicPlayer('test', level)
    assert player.level() == level


def test_player_name(name='test'):
    player = BasicPlayer(name, 1500)
    assert player.name() == name


@pytest.mark.parametrize('generator, parameters', [(numb_gen, {}), (concat_letters, concat_params)])
def test_create_name_gen_params_nb_players(generator, parameters):
    pop = BasicPlayer.create(nb=NB, name_gen=generator, name_params=parameters)
    assert len(set(pop)) == NB


@pytest.mark.parametrize('distribution, parameters', [(lambda **kwargs: levels1.pop(0), {}),
                                                      (random.gauss, {
                                                       'mu': 1000, 'sigma': 100}),
                                                      (random.gammavariate, {'alpha': 50, 'beta': 100})])
def test_create_level_dist_params_correct_nb(distribution, parameters):
    pop = BasicPlayer.create(
        nb=NB, level_dist=distribution, level_params=parameters)
    assert len(set(pop)) == NB


@pytest.mark.parametrize('distribution, parameters, levels', [(lambda **kwargs: levels2.pop(0), {}, copy.copy(levels2)),
                                                              ])
def test_create_level_dist_params_correct_levels(distribution, parameters, levels):
    pop = BasicPlayer.create(
        nb=NB, level_dist=distribution, level_params=parameters)
    for p, l in zip(pop, levels):
        assert p.level() == l


@pytest.mark.parametrize('start, inc', [(0, 100), (600, 10)])
def test_seeded_players_correct_nb(start, inc):
    pop = BasicPlayer.seeded_players(NB, start, inc)
    assert len(set(pop)) == NB
    assert len(set([p.name() for p in pop])) == NB
    assert len(set([p.level() for p in pop])) == NB
