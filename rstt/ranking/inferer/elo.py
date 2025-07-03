import rstt.utils.functions as uf

from typeguard import typechecked
import warnings


class Elo:
    def __init__(self, k: float = 20.0, lc: float = 400.0, base: float = 10.0):
        """Eo Inferer

        Simple implementation based on `wikipedia <https://en.wikipedia.org/wiki/Elo_rating_system#Theory>`_

        Parameters
        ----------
        k : float, optional
            The K-factor, by default 20.0
        lc : float, optional
            The constant dividing the ratings difference in the expected score formula, by default 400.0.
        """
        self.base = base
        self.lc = lc
        self.K = k
        # QUEST: should the base implementation support distribution function as parameters

    @typechecked
    def rate(self, ratings_groups: list[list[float]], scores: list[float], *args, **kwars) -> list[list[float]]:
        """Rate method for elo

        Parameters
        ----------
        ratings_groups : List[List[float]]
            Elo ratings formated by teams, for example [[elo_player1], [elo_player2]].
        scores : List[float]
            corresponding scores of the ratings, for example [[1.0],[0.0]] assuming player1 won the duel.

        Returns
        -------
        List[List[float]]
            updated ratings in the formats [[new_elo1][new_elo2]]
        """

        '''
        !!! NOBUG:
            Take great care when reading the code, both calls are valid:
            - updating ratings based on one game score:
                elo.rate(ratings_groups=[[1500],[1600]], scores=[0.0, 1.0])
                -> output two ratings
            - updating one player rating based on one game score:
                elo.rate(ratings_groups=[[1500], [1600]], scores=[0.0])
                -> output one rating
                
            This can be confusing as hell, however the requierements are:
            - support 1 versus 1 games update game by game
            - support 1 versus 1 games update in on computation
            - match input/output sysntax and type of others rating systems.
        '''

        # Deal with bad function calls
        if len(ratings_groups) != 2:
            msg = f"Expect two ratings groups, got {len(ratings_groups)}"
            raise ValueError(msg)
        if len(ratings_groups[0]) != 1:
            msg = f"Expect only one rating in the first ratings group, got {len(ratings_groups[0])}"
            raise ValueError(msg)
        if len(ratings_groups[1]) == 1 and len(scores) not in [1, 2]:
            msg = f"For 1-versus-1 update, Elo Expect \'scores\' of len 2, received {len(scores)}"
            raise ValueError(msg)
        if len(ratings_groups[1]) != 1 and len(ratings_groups[1]) != len(scores):
            msg = f"Incompatible args call, 2nd ratings group must be of length equal to the scores, received {len(ratings_groups[1])} and {len(scores)}"
            raise ValueError(msg)

        if len(ratings_groups[0]) == len(ratings_groups[1]) == 1 and len(scores) == 2:
            # one 1-versus-1 case
            [[r1], [r2]] = ratings_groups
            [s1, s2] = scores
            new_rating1 = self.post_rating(
                prior_rating=r1, ratings_opponents=[r2], scores=[s1])
            new_rating2 = self.post_rating(
                prior_rating=r2, ratings_opponents=[r1], scores=[s2])
            return [[new_rating1], [new_rating2]]
        else:
            # many 1-versus-1 case
            [[r1], rs] = ratings_groups
            return [[self.post_rating(prior_rating=r1, ratings_opponents=rs, scores=scores)]]

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
        return uf.logistic_elo(base=self.base, diff=rating1-rating2, constant=self.lc)

    def update_rating(self, rating1: float, rating2: float, score: float):
        """Rating update

        .. deprecated:: 1.1
                Use the post_rating method instead
        """
        msg = 'update_rating removed in version 1.0.0, instead use \'post_rating(prior_rating=[\'rating1\'], opponents_ratings=[\'rating2\'], scores=\'score\')\''
        warnings.warn(msg, DeprecationWarning)
        return self.post_rating(prior_rating=rating1, ratings_opponents=[rating2], scores=score)

    def post_rating(self, prior_rating: float, ratings_opponents: list[float], scores: list[float]):
        """post_rating

        Update the rating of a player given a list of opponent's ratings and corresponding scores against.

        Parameters
        ----------
        prior_rating : float
            a rating to update
        ratings_opponents : list[float]
            opponent's ratings
        scores : list[float]
            scores associated to the prior_rating

        Returns
        -------
        float
            post rating
        """
        return prior_rating + self.K * (sum(scores) - sum([self.expectedScore(prior_rating, rating2) for rating2 in ratings_opponents]))
