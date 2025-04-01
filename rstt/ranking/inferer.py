"""Module for Inferer.

Inferer are protocol providing a rate() method for ranking to update ratings.
"""

from typing import List, Dict, Tuple, Union, Optional, Any
from typeguard import typechecked

import rstt.config as cfg
from rstt.player import Player
from rstt.stypes import SPlayer, Event

import numpy as np
import math
import copy

import warnings


'''
    FIXME:
    - There is no consensus on the return type of the rate() functions
    - It is fine regarding the Protocol, but realy anoying when combine with Observer
'''


# ------------------------ #
# --- Player as Rating --- #
# ------------------------ #
class PlayerLevel:
    @typechecked
    def rate(self, player: SPlayer, *args, **kwars) -> Dict[SPlayer, float]:
        """Inferer based on players's level.

        Rates players on the returned value of the level() method. Usefull for 'Consensus' ranking variation.

        Parameters
        ----------
        player : SPlayer
            A player to rate

        Returns
        -------
        Dict[Player, float]
            the player and its new rating.
        """
        return {player: player.level()}


class PlayerWinPRC:
    def __init__(self, default: float = -1.0, scope: int = np.iinfo(np.int32).max):
        """Inferer based on Player win rate


        Parameters
        ----------
        default : float, optional
            A rating for when no game was yet played, by default -1.0
        scope : int, optional
            The number of game to consider, starting from the most recent one, by default np.iinfo(np.int32).max.
        """
        self.default = default
        self.scope = scope

    @typechecked
    def rate(self, player: Player, *args, **kwargs) -> Dict[Player, float]:
        """Win rate inference

        Parameters
        ----------
        player : Player
            a player to rate

        Returns
        -------
        Dict[Player, float]
            the player and its associated rating
        """
        return {player: self._win_rate(player)}

    def _win_rate(self, player: SPlayer):
        games = player.games()
        if games:
            if self.scope:
                games = games[-self.scope:]
            nb_wins = sum([1 for game in games if player is game.winner()])
            total = len(games)
            winrate = nb_wins / total * 100
        else:
            winrate = self.default
        return winrate


# ------------------------ #
# ----- Event Based ------ #
# ------------------------ #
class EventStanding:
    def __init__(self, buffer: int, nb: int, default: Optional[Dict[int, float]] = None):
        """Inferer tracking performances in tournaments

        Can be usefull to build ranking emulating one like in tennis or formula1.

        Parameters
        ----------
        buffer : int
            The number of event to consider for the rating, starting from the last.
        nb : int
            The actual number of event in the buffer to use for the ratings computation.
        default : Optional[Dict[int, float]], optional
            Mapping placement in event to points for the rating, by default None


        Example
        -------
            >>> EventStanding(buffer=10, nb=5, default={i:100-i for i in range(100)})

            Will rate each player based on his 5 best performances in the last 10 events added to the Inferer.
            Best performances in the sense of most points for his placements, not highest place (which could be different).

        """
        self.buffer = buffer
        self.nb = nb

        self.events = []
        self.points = {}

        self.__default_points = default if default is not None else cfg.EVENTSTANDING_DEFAULT_POINTS

    @typechecked
    def add_event(self, event: Union[Event, str], points: Optional[Dict[int, float]] = None):
        """Add an event to consider for ratings

        Event are always append as the last, thus will stay longer in the buffer than all previous eevnts added.

        Parameters
        ----------
        event : Union[Event, str]
            An event or its identifier.
        points : Optional[Dict[int, float]], optional
            A dictionnary mapping placement with points, by default None. In this case the default one is used for the added event.
        """
        points = points if points else self.__default_points
        if isinstance(event, str):  # by str
            self.events.append(event)
            self.points[event] = points
        else:  # by Event
            self.events.append(event.name())
            self.points[event.name()] = points

    @typechecked
    def remove_event(self, event: Union[Event, str]):
        """Remove an event

        Parameters
        ----------
        event : Union[Event, str]
            The event or its identifier, to remove from ratings considerations.
        """
        if isinstance(event, str):  # by str
            self.events.remove(event)
            del self.points[event]
        else:  # by Event
            self.events.remove(event.name())
            del self.points[event.name()]

    @typechecked
    def rate(self, player: Player) -> Dict[Player, float]:
        """Rate player based on performances.

        Parameters
        ----------
        player : Player
            A player to rate

        Returns
        -------
        Dict[Player, float]
            the player and its new rating.
        """
        # events that matter
        events = self.events[-self.buffer:]

        # collected points in events
        results = []
        for achievement in player.achievements():
            if achievement.event_name in events:
                results.append(
                    self.points[achievement.event_name][achievement.place])

        # get only the best results
        results.sort()
        best_results = results[-min(len(results), self.nb):]

        # sum the best results considered
        points = sum(best_results)
        return {player: points}


# ------------------------ #
# --- Game Score Based --- #
# ------------------------ #
class Elo:
    def __init__(self, k: float = 20.0, lc: float = 400.0):
        """Eo Inferer

        Simple implementation based on `wikipedia <https://en.wikipedia.org/wiki/Elo_rating_system#Theory>`_

        Parameters
        ----------
        k : float, optional
            The K-factor, by default 20.0
        lc : float, optional
            The constant dividing the ratings difference in the expected score formula, by default 400.0.
        """
        self.lc = lc
        self.K = k
        # TODO self.distribution = dist & change expectedScore

    @typechecked
    def rate(self, groups: List[List[float]], scores: List[float], *args, **kwars) -> List[List[float]]:
        """Rate method for elo

        Parameters
        ----------
        groups : List[List[float]]
            Elo ratings formated by teams, for example [[elo_player1], [elo_player2]].
        scores : List[float]
            corresponding scores of the ratings, for example [[1.0],[0.0]] assuming player1 won the duel.

        Returns
        -------
        List[List[float]]
            updated ratings in the formats [[new_elo1][new_elo2]]
        """
        # NOTE: groups: [[winner_elo][loser_elo]], scores [[1.0][0.0]]
        # FIXME: Current implementation does not seem to support a BatchGame observer
        # TODO: add errors for bad params

        # unpack args
        r1, r2 = groups[0][0], groups[1][0]
        s1, s2 = scores
        # cumpute new ratings
        new_r1 = self.update_rating(r1, r2, s1)
        new_r2 = self.update_rating(r2, r1, s2)
        return [[new_r1], [new_r2]]

    @typechecked
    def expectedScore(self, rating1: float, rating2: float) -> float:
        """Compute the expected score

        Parameters
        ----------
        rating1 : float
            a rating
        rating2 : float
            another rating

        Returns
        -------
        float
            expected result of the player with rating1 against the player with rating2
        """
        # TODO: 'DRY' -> use uf.logistic_elo
        return 1.0 / (1.0 + math.pow(10, (rating2-rating1)/self.lc))

    def update_rating(self, rating1: float, rating2: float, score: float):
        """Rating update

        Parameters
        ----------
        rating1 : float
            a rating
        rating2 : float
            another rating
        score : float
            the score associated to rating1

        Returns
        -------
        float
            the 'updated rating1'
        """
        expected_result = self.expectedScore(rating1, rating2)
        return rating1 + (self.K * (score-expected_result))


class Glicko:
    @typechecked
    def __init__(self, minRD: float = 30.0,
                 maxRD: float = 350.0,
                 c: float = 63.2,
                 q: float = math.log(10, math.e)/400,
                 lc: int = 400):
        """Glicko Inferer

        The `Glicko <https://en.wikipedia.org/wiki/Glicko_rating_system>`_ rating system is often described as an improvement of :class:`rstt.ranking.inferer.Elo`.
        here, the implementation is based on Dr. Mark E. Glickman `description <https://www.glicko.net/glicko/glicko.pdf>`_.

        .. note::
            The source paper gives more instruction (notion of rating period) than what an Inferer class should do in RSTT.
            Step1, for example is implemented by the :class:`rstt.ranking.standard.BasicGlicko`
            because it is related to the usage of the system, rather than what the Inferer does.

        .. warning::
            There is no type-checker support for 'Glicko ratings'.
            In the documentation we use the typehint 'GlickoRating'.
            Anything with a public mu and sigma attribute fits the bill.


        Parameters
        ----------
        minRD : float, optional
            minimal value of RD, by default 30.0
        maxRD : float, optional
            maximal value of RD, by default 350.0
        c : float, optional
            constant used for 'inactivity decay', by default 63.2
        q : float, optional
            No idea what it represent, feel free to play arround, by default math.log(10, math.e)/400
        lc : int, optional
            Logistic constant similar to the one in :class:`rstt.rnaking.inferer.Elo`, by default 400
        """

        # model constant
        self.__maxRD = maxRD
        self.__minRD = minRD
        self.lc = lc
        self.C = c
        self.Q = q

    def G(self, rd: float) -> float:
        """_summary_

        Implements: page 3, step2, g(RD) formula.

        Parameters
        ----------
        rd : float
            the RD of a rating

        Returns
        -------
        float
            g(RD)
        """
        return 1 / math.sqrt(1 + 3*self.Q*self.Q*(rd*rd)/(math.pi*math.pi))

    def expectedScore(self, rating1, rating2, update: bool = True) -> float:
        """Compute the expected score

        Implements: page 4, E(s|r,rj,RDj) when update=True
        or page 5, E otherwise.

        Parameters
        ----------
        rating1 : GlickoRating
            'main' rating
        rating2 : GlickoRating
            opponents rating
        update : bool, optional
            Wheter to use the formula for update or not, by default True.

        Returns
        -------
        float
            The expected score of the player with rating1 against player with rating2
        """
        RDi = 0 if update else rating1.sigma
        RDj = rating2.sigma
        ri, rj = rating1.mu, rating2.mu
        return 1 / (1 + math.pow(10, -self.G(math.sqrt(RDi*RDi + RDj*RDj)) * (ri-rj)/400))

    def d2(self, rating1, games: List[Tuple[Any, float]]) -> float:
        """
        Implements: page 4, d^2 formula.

        Parameters
        ----------
        rating1 : GlickoRating
            the main rating
        games : List[Tuple[GlickoRating, float]]
            A list of [opponent_rating, score_of_rating1]

        Returns
        -------
        float
            the d2 value

        Warns
        -----
            Rarely a ZeroDivisionError occurs. In this case, the warning contains all the computational information.
            Execution continues using a very small value instead.
        """
        all_EJ = []
        all_GJ = []
        for rating2, score in games:
            # get needed variables
            Ej = self.expectedScore(rating1, rating2, update=True)
            RDj = rating2.sigma
            Gj = self.G(RDj)

            # store vairables
            all_EJ.append(Ej)
            all_GJ.append(Gj)

        # big sum
        bigSum = 0
        for Gj, Ej, in zip(all_GJ, all_EJ):
            bigSum += Gj*Gj*Ej*(1-Ej)

        '''
        NOTE:
        Try/Expect is not part of the Glicko official algorithm  presentation.
        But I have encountered Unexpected ZeroDivisionError
        
        This is easly fixed by:
        return 1 / min( self.Q*self.Q*bigSum, lower_bound)
        
        However I could note find any specfic details about the choice of the boundary.
        
        Analytically, the term can not be equal to 0.0, it is always >0.
        Nnumercialy, it happens in extreme situation i.e does not arise in standard 'intended' Glicko usage.
        
        The package is for scientifical experimentation,
        It allows extreme case exploration and can not hide arbitrary choices.

        # !!! Do not fix unless it is possible to link a scientifical source justifying the implementation
        '''
        try:
            # d2 formula
            return 1 / (self.Q*self.Q*bigSum)
        except ZeroDivisionError:
            # !!! BUG: ZeroDivisionError observed with extreme rating differences
            # !!! this will now print variable of interest
            # !!! but code will run assuming maximal and mininal expected value possible between 0 and 1

            # HACK: just assume a very low 'bigSum'
            bigSum = 0.00000000001
            correction = 1 / (self.Q*self.Q*bigSum)

            msg = f"Glicko d2 ERROR: {rating1}, {games}\n {bigSum}, {all_EJ}, {all_GJ}\n d2 return value as been adjusted to 1/{bigSum}"
            warnings.warn(msg, RuntimeWarning)
            return correction

    # TODO: how to typecked
    def prePeriod_RD(self, rating: Any) -> float:
        """pre update RD value

        Implements: page 3, step1, formula (b).

        Parameters
        ----------
        rating : GlickoRating
            A rating to 'pre-update'

        Returns
        -------
        float
            the new RD value of the rating. 
        """
        new_RD = math.sqrt(rating.sigma*rating.sigma + self.C*self.C)
        # check boundaries on sigma - ??? move max() elsewhere
        return max(min(new_RD, self.__maxRD), self.__minRD)

    def newRating(self, rating1, games: List[Tuple[Any, float]]):
        """Rating Update method

        Implements: page 3, step2.

        Parameters
        ----------
        rating1 : GlickoRating
            a rating to update.
        games : List[Tuple[GlickoRating, float]]
            A list of results formated under as [opponent_rating, score_of rating1]

        Returns
        -------
        GlickoRating
            the new updated rating
        """

        # compute term 'a'
        d2 = self.d2(rating1, games)
        a = self.Q / ((1/(rating1.sigma*rating1.sigma)) + (1/d2))

        # lcompute term 'b'
        b = 0
        for rating2, score in games:
            b += self.G(rating2.sigma)*(score -
                                        self.expectedScore(rating1, rating2, update=True))

        # create new rating object to avoid 'side effect'
        rating = copy.copy(rating1)
        # post Period R
        rating.mu += a*b
        # post Period RD
        rating.sigma = math.sqrt(1/((1/rating1.sigma**2) + (1/d2)))

        return rating

    # FIXME: Does not support GameByGame observer
    def rate(self, rating, ratings: List[Any], scores: List[float], *args, **kwars):
        """Glicko rate method

        End to end method to compute a new glicko rating based on a collection of results

        Parameters
        ----------
        rating : GlickoRating
            the rating to update
        ratings : List[GlickoRating]
            list of opponent ratings
        scores : List[float]
            list of score achieved by rating1 against the 'ratings' opponents, in the same order

        Returns
        -------
        GlickoRating
            The new rating.
        """

        # formating
        games = [(r, s) for r, s in zip(ratings, scores)]
        return self.newRating(rating, games)
