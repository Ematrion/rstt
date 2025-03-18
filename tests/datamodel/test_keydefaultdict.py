import pytest

from rstt.ranking.datamodel import keydefaultdict
from rstt import BasicPlayer, Player

from collections import defaultdict


@pytest.fixture
def kdd():
    return keydefaultdict(lambda x: x)



def test_dict(kdd):
    assert isinstance(kdd, dict)
    
def test_default_dict(kdd):
    assert isinstance(kdd, defaultdict)

@pytest.mark.parametrize("value", [1, 2, 3, True, False, 'abc', Player('test', 1500), BasicPlayer('test', 1500)])
def test_default_value(kdd, value):
    assert kdd[value] == value



