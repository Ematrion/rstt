"""Module for 'kock-out' Competition.

Such tournament do have a strict elimination process and losing participants are quickly cut of the event.
Standing is based on 'how far' the competitors go.
"""

from typing import Callable, Protocol
from enum import StrEnum
from typeguard import typechecked


from . import Competition
from rstt.ranking.ranking import Ranking
from rstt import BetterWin, Duel
from rstt.stypes import Solver, SPlayer

from rstt.utils import utils as uu, matching as um, competition as uc

import math


def balanced_tree(rounds):
    matches = [1, 2]
    for round in range(2, rounds+1):
        check_sum = pow(2, round)+1
        new_matches = []
        for i in matches:
            new_matches.append([i, check_sum-i])
        matches = uu.flatten(new_matches)

    return matches


class SingleEliminationBracket(Competition):
    """Single Elimination Bracket or tournament

    One of the most famous and used competition model, specialy in internationl events, 
    Participants are placed in a binary tree where the winner of a confrontation advance to the next stage and the loser is eliminated.

    More detail on the `single-elimination-bracket <https://en.wikipedia.org/wiki/Single-elimination_tournament>`_  wikipedia page.

    .. note::
        Currently the first round matching is the standard policy. for example with 8 participants:
        Seed1 versus Seed8; Seed4 versus Seed5; Seed2 versus Seed7; Seed3 versus Seed6.

        Future version will support custom first round matching.
        In the mean time, to fine tune the first round, it is possible to reorder a ranking with a permutation using the :func:`rstt.ranking.ranking.Ranking.rerank` method.
        This needs to be called on a ranking before passing it to a competition.
    """
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),
                 cashprize: dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

    # --- override --- #
    def _initialise(self):
        msg = (f'{type(self)} '
               'needs a power of two as number of participants '
               '(2,4,8,16,...)'
               f', given {len(self.participants())}')
        assert uu.power_of_two(len(self.participants())), msg

        nb_rounds = int(math.log(len(self.participants()), 2))
        self.players_left = self.seeding[[
            i-1 for i in balanced_tree(nb_rounds)]]

    def generate_games(self):
        return uc.playersToDuel(self.players_left)

    def _end_of_stage(self) -> bool:
        return True if len(self.players_left) == 1 else False

    def _update(self):
        next = [game.winner() for game in self.played_matches[-1]]
        self.players_left = next

    def _standing(self) -> dict[SPlayer, int]:
        standing = {}
        top = len(self.participants())
        for round in self.played_matches:
            for game in round:
                standing[game.loser()] = top
            top = len(self.participants()) - len(standing)

        # winner
        standing[self.played_matches[-1][0].winner()] = 1
        return standing






class Bracket(StrEnum):
    UPPER       = "Upper"
    INJECTOR    = "Injector"
    LOWER       = "Lower"
    
    FIRSTUPPER  = "FirstUpper"
    GRANDFINAL  = "GrandFinal"


class DEB(Protocol):
    played_matches: list[list[Duel]]
    _brackets: dict[Bracket, list[SPlayer]]


Transition = Callable[[Competition], Bracket]

def from_firstupper(deb: DEB) -> Bracket:
    winners = [game.winner() for game in deb.played_matches[-1]]
    losers = [game.loser() for game in deb.played_matches[-1]]
    deb._brackets[Bracket.UPPER] = winners
    deb._brackets[Bracket.LOWER] = losers
    return Bracket.LOWER

def from_upper(deb: DEB) -> Bracket:
    winners = [game.winner() for game in deb.played_matches[-1]]
    losers = [game.loser() for game in deb.played_matches[-1]]
    if len(winners) == 1:
        deb._brackets[Bracket.GRANDFINAL] = winners
    else:
        deb._brackets[Bracket.UPPER] = winners
    deb._brackets[Bracket.INJECTOR] += losers
    return Bracket.INJECTOR

def from_injector(deb: DEB) -> Bracket:
    winners = [game.winner() for game in deb.played_matches[-1]]
    if len(winners) == 1:
        deb._brackets[Bracket.GRANDFINAL] += winners
        return Bracket.GRANDFINAL
    deb._brackets[Bracket.LOWER] = winners
    return Bracket.LOWER

def from_lower(deb: DEB) -> Bracket:
    winners = [game.winner() for game in deb.played_matches[-1]]
    deb._brackets[Bracket.INJECTOR] = winners
    return Bracket.UPPER


TRANSITIONS = {
    Bracket.FIRSTUPPER: from_firstupper,
    Bracket.UPPER: from_upper,
    Bracket.INJECTOR: from_injector,
    Bracket.LOWER: from_lower,
    Bracket.GRANDFINAL: lambda x: Bracket.GRANDFINAL
}


class DoubleEliminationBracket(Competition):
    # TODO:
    # + upper / lower / injector (riffle_shuffle ?) matching policy
    # Try to fit in the game generator of SwissBracket
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),

                 cashprize: dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

        self._brackets: dict[Bracket, list[SPlayer]] = {bracket: [] for bracket in Bracket}
        self._current = Bracket.FIRSTUPPER

        # TODO: add matching specifications
        # self.policies : dict[(str, int): matching_policy]

    # --- override --- #
    def _initialise(self):
        msg = (f'{type(self)} '
               'needs a power of two as number of participants '
               '(2,4,8,16,...)'
               f', given {len(self.participants())}')
        assert uu.power_of_two(len(self.participants())), msg
        nb_rounds = int(math.log(len(self.participants()), 2))
        self._brackets[Bracket.FIRSTUPPER] = self.seeding[[i-1 for i in balanced_tree(nb_rounds)]] # type: ignore

    def generate_games(self):
        games = uc.playersToDuel(self._brackets[self._current]) #type: ignore
        self._brackets[self._current] = []
        return games
    
    def _update(self):
        self._current = TRANSITIONS[self._current](self)

    def _end_of_stage(self) -> bool:
        return self._current == Bracket.GRANDFINAL and self._brackets[self._current] == []
    
    def _standing(self) -> dict[SPlayer, int]:
        final_standing = {}
        top = len(self.participants())
        loser_bracket = set()
        for round in self.played_matches:
            eliminated = set()
            for player in [game.loser() for game in round]:
                if player in loser_bracket:
                    eliminated.add(player)
                else:
                    loser_bracket.add(player)
            final_standing.update({player: top for player in eliminated})
            top -= len(eliminated)
        final_standing[self.played_matches[-1][0].winner()] = 1
        final_standing[self.played_matches[-1][0].loser()] = 2
        return final_standing
    
    @typechecked
    def games(self, by_rounds=False, upper=False, lower=False, injector=False):
        games = []
        if (upper and lower) or (upper and injector) or (lower and injector):
            msg = f"At most one of upper, lower and injector can be True. Received values upper: {upper}, lower: {lower}, injector: {injector}"
            raise ValueError(msg)
        
        if upper: 
            games = [self.played_matches[0]] + self.played_matches[2:-2:3]
        elif lower:
            games = self.played_matches[1:-1:3]
        elif injector:
            games = self.played_matches[3:-1:3]
        else:
            # ALT: games = self.played_matches
            return super().games(by_rounds=by_rounds)
        
        if by_rounds:
            return games
        else:
            return uu.flatten(games)