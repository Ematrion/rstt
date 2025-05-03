import pytest

from rstt import Player, BasicElo
import random


# --- FIXTURE -- #
@pytest.fixture
def total():
    return 10


@pytest.fixture
def players(total):
    return Player.create(nb=total)


@pytest.fixture
def elo(players):
    elo = BasicElo('Consensus', players=players)
    for i, p in enumerate(players):
        elo.set_rating(p, i*100)
    return elo


@pytest.fixture
def cycle_perm(total):
    permutation = []
    for i in range(0, total):
        if i != total-1:
            permutation.append(i+1)
        else:
            permutation.append(0)
    return permutation


@pytest.fixture
def random_perm(total):
    permutation = list(range(total))
    random.shuffle(permutation)
    return permutation


# --- TEST --- #
def test_rerank_error_invalid_index(total, elo):
    permutation = list(range(total))
    permutation[0] = total
    with pytest.raises(ValueError):
        elo.rerank(permutation=permutation)


def test_rerank_error_permutation_lenght(total, elo):
    permutation = list(range(total))
    permutation += [0, 0, 0]
    with pytest.raises(ValueError):
        elo.rerank(permutation=permutation, direct=False)


def test_rerank_renaming(total, elo):
    name = 'test_name'
    elo.rerank(permutation=list(range(total)), name=name)
    assert elo.name == name


def test_rerank_cycle_direct(total, elo, cycle_perm):
    reference = {p: elo[p] for p in elo}
    for _ in range(total):
        elo.rerank(permutation=cycle_perm, direct=True)
    for p in elo:
        assert elo[p] == reference[p]


def test_rerank_cycle_indirect(total, elo, cycle_perm):
    reference = {p: elo[p] for p in elo}
    for _ in range(total):
        elo.rerank(permutation=cycle_perm, direct=False)
    for p in elo:
        assert elo[p] == reference[p]


def test_rerank_direct_and_indirect_cycle(elo, cycle_perm):
    reference = {p: elo[p] for p in elo}
    elo.rerank(permutation=cycle_perm, direct=True)
    elo.rerank(permutation=cycle_perm, direct=False)
    for p in elo:
        assert elo[p] == reference[p]


def test_rerank_direct_and_indirect_random(elo, random_perm):
    reference = {p: elo[p] for p in elo}
    elo.rerank(permutation=random_perm, direct=True)
    elo.rerank(permutation=random_perm, direct=False)
    for p in elo:
        assert elo[p] == reference[p]


def test_fit_unseeded_not_added(elo):
    unseeded = Player.create(nb=5)
    seeding = elo.fit(unseeded)
    for p in unseeded:
        assert p not in elo


def test_fit_seed_unseeded(elo):
    unseeded = Player.create(nb=5)
    seeding = elo.fit(unseeded)
    for p in unseeded:
        assert p in seeding


def test_fit_some_present(elo, players):
    unseeded = Player.create(nb=5)
    seeding = elo.fit(unseeded+players)
    for p in unseeded + players:
        assert p in seeding
