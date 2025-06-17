from typing import List
from typeguard import typechecked

from rstt import Duel
from rstt.stypes import SPlayer

import warnings


@typechecked
def playersToDuel(players: List[SPlayer]) -> List[Duel]:
    return [Duel(players[2*i], players[2*i+1]) for i in range(len(players)//2)]


@typechecked
def new_matchup(game: Duel, games: List[Duel], symetric: bool = True) -> bool:
    p1, p2 = game.player1(), game.player2()
    confrontations = [(duel.player1(), duel.player2()) for duel in games]
    if (p1, p2) in confrontations:
        return False
    if symetric and (p2, p1) in confrontations:
        return False
    return True


@typechecked
def find_valid_draw(draws: List[List[Duel]], games: List[Duel], symetric: bool = True) -> List[Duel]:
    # !!! symetric -> valid_draw(...) -> new_matchup(...)
    # avoid side-effect (usage of .pop)
    draws = [option for option in draws]

    # default return value
    first_option = draws[0]

    # find draw
    good_draw = None
    while not good_draw and draws:
        option = draws.pop(0)
        if valid_draw(option, games):
            good_draw = option

    # deal with mission failed
    if not good_draw:
        good_draw = first_option
        msg = f"No Valid matchups where found"
        warnings.warn(msg, RuntimeWarning)

    return good_draw


@typechecked
def valid_draw(draw: List[Duel], games: List[Duel]) -> bool:
    for game in draw:
        if not new_matchup(game, games):
            return False
    return True
