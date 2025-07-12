import pytest

import rstt.player as rp


NB = 10


@pytest.mark.parametrize('model', [rp.BasicPlayer, rp.Player, rp.GaussianPlayer,
                                   rp.ExponentialPlayer, rp.LogisticPlayer, rp.CyclePlayer, rp.JumpPlayer])
def test_create(model):
    pop = model.create(nb=NB)
    # NB players with different names and levels
    assert len(pop) == NB
    assert len(set([p.name() for p in pop])) == NB
    assert len(set(p.level() for p in pop)) == NB
