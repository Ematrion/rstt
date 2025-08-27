import pytest

from rstt import Player, SuccessRanking, RoundRobin, BetterWin, BTRanking


@pytest.fixture
def gt():
    population = Player.create(nb=16)
    groundtruth = BTRanking('GT', players=population)
    return groundtruth


@pytest.fixture
def roundrobin(gt):
    cup = RoundRobin('RoundRobin', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def places(gt):
    return list(range(1, len(gt)+1))


@pytest.fixture
def minor_event(places):
    points = [len(places)-place+1 for place in places]
    return {place: point for place, point in zip(places, points)}


def test_update_event_input(roundrobin):
    sr = SuccessRanking('test')
    # event should be supported
    sr.update(event=roundrobin)


def test_update_event_with_relevance_input(roundrobin, places):
    sr = SuccessRanking('test')
    # relevance should be supported
    sr.update(event=roundrobin, relevance=places)
