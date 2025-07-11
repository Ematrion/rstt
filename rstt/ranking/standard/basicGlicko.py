from rstt.stypes import SPlayer, RatingSystem
from rstt.ranking.rating import GlickoRating
from rstt.ranking.ranking import Ranking, get_disamb
from rstt.ranking.datamodel import GaussianModel
from rstt.ranking.inferer import Glicko
from rstt.ranking.observer import BatchGame
from rstt.ranking.observer.gameObserver import new_ratings_groups_to_ratings_dict
from rstt.ranking.observer.utils import *

import math


def get_ratings_for_glicko(prior: RatingSystem, data: dict[str, any]) -> None:
    data[RATING] = prior.get(data[TEAMS][0][0])
    data[RATINGS_OPPONENTS] = [prior.get(opponent)
                               for opponent in data[TEAMS][1]]


class BasicGlicko(Ranking):
    def __init__(self, name: str,
                 mu: float = 1500.0, sigma: float = 350.0,
                 minRD: float = 30.0, maxRD: float = 350.0,
                 c: float = 63.2, q: float = math.log(10, math.e)/400,
                 lc: int = 400,
                 players: list[SPlayer] | None = None):
        """Simple Glicko system

        Implement A glicko rating system as originaly `proposed <https://www.glicko.net/glicko/glicko.pdf>`_.

        .. note::
            As recommanded in the source paper, the update() method starts by adjusting each players rating before
            processing any game data (sort of a rating decay)


        Attributes
        ----------
        datamodel: :class:`rstt.ranking.datamodel.GaussianModel` (:class:`rstt.ranking.rating.GlickoRating as rating)
        backend: :class:`rstt.ranking.inferer.Glicko` as backend
        handler :class:`rstt.ranking.observer.BatchGame` as handler


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        handler : _type_, optional
            Backend as parameter, by default BatchGame()
            The original recommendation is to update the ranking by grouping matches within rating period.
            Which is what the BatchGame Observer do, (each update call represent one period). To match other glicko, use A GameByGame observer
        mu : float, optional
            Datamodel parameter, the default mu of the rating, by default 1500.0
        sigma : float, optional
           Datamodel parameter, the default sigma of the rating, by default 350.0
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
        super().__init__(name=name,
                         datamodel=GaussianModel(
                             default=GlickoRating(mu, sigma)),
                         backend=Glicko(minRD, maxRD, c, q, lc),
                         handler=BatchGame(),
                         players=players)
        self.handler.query = get_ratings_for_glicko
        self.handler.output_formater = lambda d, x: new_ratings_groups_to_ratings_dict(d, [
                                                                                       [x]])

    @get_disamb
    def __step1(self):
        # TODO: check which player iterator to use
        for player in self:
            rating = self.datamodel.get(player)
            rating.sigma = self.backend.prePeriod_RD(rating)

    def forward(self, *args, **kwargs):
        self.__step1()
        self.handler.handle_observations(
            infer=self.backend, datamodel=self.datamodel, *args, **kwargs)
