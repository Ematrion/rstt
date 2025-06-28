import pytest

from rstt import BasicPlayer, GaussianPlayer

# from rstt.ranking.inferer import PlayerLevel
from rstt.new_ranking.standard.consensus import PlayerLevel


'''
NOT Backward Compatible.

'''


@pytest.mark.parametrize("level", [-500, 0, 500, 1000, 1500, 2000])
def test_basicplayer_level(level):
    dummy = BasicPlayer(name='dummy', level=level)
    assert PlayerLevel().rate(dummy) == dummy.level()


@pytest.mark.parametrize("mu, sigma, depth", [(-500, 50, 10), (1500, 500, 50)])
def test_gaussianplayer_level(mu, sigma, depth):
    dummy = GaussianPlayer(mu=mu, sigma=sigma)
    assert PlayerLevel().rate(dummy) == dummy.level()
    for i in range(depth):
        dummy.update_level()
        assert PlayerLevel().rate(dummy) == dummy.level()
