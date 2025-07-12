import copy
import math


from typeguard import typechecked
import warnings


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

    def d2(self, rating1, games: list[tuple[any, float]]) -> float:
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
    def prePeriod_RD(self, rating: any) -> float:
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

    def newRating(self, rating1, games: list[tuple[any, float]]):
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

    def rate(self, rating, ratings_opponents: list[any], scores: list[float], *args, **kwars):
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
        games = [(r, s) for r, s in zip(ratings_opponents, scores)]
        return self.newRating(rating, games)
