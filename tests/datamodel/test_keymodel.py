import pytest

from rstt.ranking.datamodel import KeyModel
from rstt.ranking.rating import GlickoRating, Glicko2Rating
from rstt import BasicPlayer


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
    assert km.rtype() is type(value)


@pytest.mark.parametrize("default", [1500, GlickoRating(1500, 350), Glicko2Rating(1500, 350, 0.06)])
def test_init_with_default(default, dummy):
    datamodel = KeyModel(default=default)
    assert datamodel.get(dummy) == default


@pytest.mark.parametrize("template, rating", [(int, 0), (GlickoRating, GlickoRating()), (Glicko2Rating, Glicko2Rating())])
def test_init_with_template(template, dummy, rating):
    datamodel = KeyModel(template=template)
    assert datamodel.get(dummy) == rating


@pytest.mark.parametrize("template, kwargs, rating", [(GlickoRating, {'mu': 1500, 'sigma': 350}, GlickoRating(1500, 350)),
                                                      (Glicko2Rating, {'mu': 1500, 'sigma': 350, 'volatility': 0.06}, Glicko2Rating(1500, 350, 0.06))])
def test_init_with_template_kwargs(template, kwargs, dummy, rating):
    datamodel = KeyModel(template=template, **kwargs)
    assert datamodel.get(dummy) == rating


@pytest.mark.parametrize("factory, rating", [(lambda player: GlickoRating(mu=player.level()), GlickoRating(DUMMY_LEVEL)),
                                             (lambda player: Glicko2Rating(mu=player.level()), Glicko2Rating(DUMMY_LEVEL))])
def test_init_with_factory(factory, dummy, rating):
    datamodel = KeyModel(factory=factory)
    assert datamodel.get(dummy) == rating


@pytest.mark.parametrize("factory, kwargs, rating", [(lambda player, **kwargs: GlickoRating(mu=player.level(), **kwargs), {'sigma': 200}, GlickoRating(DUMMY_LEVEL, 200)),
                                                     (lambda player, **kwargs: Glicko2Rating(mu=player.level(), **kwargs), {'sigma': 100, 'volatility': 0.03}, Glicko2Rating(DUMMY_LEVEL, 100, 0.03))])
def test_init_with_facotry_kwargs(factory, kwargs, dummy, rating):
    datamodel = KeyModel(factory=factory, **kwargs)
    assert datamodel.get(dummy) == rating
