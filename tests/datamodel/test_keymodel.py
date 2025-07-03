import pytest

from rstt.ranking.datamodel import KeyModel
from rstt.ranking.rating import GlickoRating
from rstt import BasicPlayer, Player


# --- Const --- #
MU, SIGMA = 1500.0, 250.0
DUMMY_NAME = 'Dummy'
DUMMY_LEVEL = 1500
RKM = KeyModel(default=GlickoRating())
TKM = KeyModel(template=GlickoRating, mu=MU, sigma=SIGMA)
FKM = KeyModel(factory=lambda x: x.name())
ALLKM = [RKM, TKM, FKM]
RATINGS = [GlickoRating(), GlickoRating(MU, SIGMA), DUMMY_NAME]


# --- Fixtures --- #
@pytest.fixture
def dummy():
    return BasicPlayer(DUMMY_NAME, DUMMY_LEVEL)


@pytest.fixture
def rating_km():
    return KeyModel(default=GlickoRating())


@pytest.fixture
def template_km():
    return KeyModel(template=GlickoRating, mu=MU, sigma=SIGMA)


@pytest.fixture
def factory_km():
    return KeyModel(factory=lambda x: x.name())


# --- TESTING --- #
@pytest.mark.parametrize("km, value", [(km, value) for km, value in zip(ALLKM, RATINGS)])
def test_set(km, value, dummy):
    km.set(dummy, value)
    assert km.get(dummy) == value


@pytest.mark.parametrize("km, value", [(km, value) for km, value in zip(ALLKM, RATINGS)])
def test_get(km, value, dummy):
    assert km.get(dummy) == value


@pytest.mark.parametrize("km, value", [(km, value) for km, value in zip(ALLKM, RATINGS)])
def test_rtypes(km, value):
    assert km.rtype() == type(value)


'''@pytest.mark.parametrize("km, value", [(km, value) for km, value in zip(ALLKM, RATINGS)])    
def test_default(km, value):
    assert km.default() == value

@pytest.mark.parametrize("km, value", [(km, value) for km, value in zip(ALLKM, RATINGS)])     
def test_ordinal_float_value(km, value):
    assert isinstance(km.ordinal(value), float)'''
