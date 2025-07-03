from rstt.stypes import SPlayer, RatingSystem
from rstt.ranking.rating import GlickoRating
from rstt.ranking.ranking import Ranking, get_disamb
from rstt.ranking.datamodel import GaussianModel
from rstt.ranking.inferer import Glicko
from rstt.ranking.observer import BatchGame
from rstt.ranking.observer.game_observer import new_ratings_groups_to_ratings_dict
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
