import pytest

from rstt import SingleEliminationBracket as SEB, DoubleEliminationBracket as DEB
from rstt import RoundRobin, SwissBracket, SwissRound, Snake
from rstt import Player, BetterWin, BTRanking

from rstt.ranking.inferer import EventScoring

import itertools


@pytest.fixture
def gt():
    population = Player.create(nb=16)
    groundtruth = BTRanking('GT', players=population)
    return groundtruth


@pytest.fixture
def seb(gt):
    cup = SEB('SEB', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def deb(gt):
    cup = DEB('DEB', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def rr(gt):
    cup = RoundRobin('RR', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def sr(gt):
    cup = SwissRound('SR', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def sb(gt):
    cup = SwissBracket('SB', seeding=gt, solver=BetterWin())
    cup.registration(gt.players())
    cup.run()
    return cup


@pytest.fixture
def snake(gt):
    cup = Snake('Snake', seeding=gt, solver=BetterWin())
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


@pytest.fixture
def important_event(minor_event):
    return {place: 2*point for place, point in minor_event.items()}


@pytest.fixture
def major_event(important_event):
    return {place: 2 * point for place, point in important_event.items()}


def test_rate_not_tracked_event(seb, deb, rr, sr, snake):
    inferer = EventScoring()
    for event in [seb, deb, rr, sr, snake]:
        for p in event.participants:
            r = inferer.rate(p)
            assert r == pytest.approx(0.0, 0.0001)


def test_rate_higher_place_higher_rating(seb, deb, rr, sr, snake):
    inferer = EventScoring()
    for event in [seb, deb, rr, sr, snake]:
        inferer.add_event(event)
        for p1, p2 in itertools.combinations(event.participants, 2):
            r1 = inferer.rate(p1)
            r2 = inferer.rate(p2)
            s1 = event.standing()[p1]
            s2 = event.standing()[p2]
            if s1 > s2:
                assert r2 > r1
            if s1 < s2:
                assert r2 < r1
            if s1 == s2:
                assert r1 == r2


def test_rate_event_relevance(rr, minor_event, important_event, major_event):
    minor = EventScoring()
    important = EventScoring()
    major = EventScoring()

    inferers = [minor, important, major]
    relevances = [minor_event, important_event, major_event]
    for inferer, relevance in zip(inferers, relevances):
        inferer.add_event(rr, relevance)

    for player in rr.participants:
        rating_minor = minor.rate(player)
        rating_important = important.rate(player)
        rating_major = major.rate(player)
        # only make sense if every place gives points  !=0 to all players
        assert rating_minor < rating_important < rating_major


@pytest.mark.parametrize("nb", [1, 2, 3, 4, 5, 6])
def test_more_event_more_point(gt, minor_event, nb):
    for i in range(1, nb+1):
        inferer = EventScoring(window_range=i, tops=i)
        for j in range(i+1):
            cup = RoundRobin(
                f'More_Event_More_Point {i} - {j}', gt, BetterWin())
            cup.registration(gt.players())
            cup.run()
            inferer.add_event(cup, minor_event)

        for p in gt:
            target_points = sum([minor_event[achive.place]
                                for achive in p.achievements()][-i:])
            assert target_points == inferer.rate(p)


@pytest.mark.parametrize("nb", [1, 2, 3, 4, 5, 6])
def test_rate_more_event_than_window(gt, minor_event, nb):
    # Like test_more_event_point with twice the amount of cup but the same window
    for i in range(1, 2*nb+1):
        inferer = EventScoring(window_range=i, tops=i)
        for j in range(i+1):
            cup = RoundRobin(
                f'More_Event_More_Point {i} - {j}', gt, BetterWin())
            cup.registration(gt.players())
            cup.run()
            inferer.add_event(cup, minor_event)

        for p in gt:
            target_points = sum([minor_event[achive.place]
                                for achive in p.achievements()[-i:]])
            assert target_points == inferer.rate(p)


@pytest.mark.parametrize("nb, tops", [(1, 1), (2, 1), (3, 2), (4, 2), (5, 2), (6, 5)])
def test_rate_more_event_than_tops(gt, minor_event, nb, tops):
    for i in range(1, nb+1):
        inferer = EventScoring(window_range=i, tops=tops)
        for j in range(i+1):
            cup = RoundRobin(
                f'More_Event_More_Point {i} - {j}', gt, BetterWin())
            cup.registration(gt.players())
            cup.run()
            inferer.add_event(cup, minor_event)

        for p in gt:
            target_points = minor_event[p.achievements()[0].place] * tops
            assert target_points == inferer.rate(p)
