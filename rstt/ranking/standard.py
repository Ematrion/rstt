from rstt.ranking import Standing
from rstt.ranking.ranking import Ranking, get_disamb
from rstt.ranking.datamodel import KeyModel, GaussianModel
from rstt.ranking.rating import GlickoRating
from rstt.ranking.inferer import Glicko, Elo, PlayerLevel, PlayerWinPRC
from rstt.ranking.observer import  GameByGame, BatchGame, KeyChecker



# ------------------------- #
# --- Consensus Ranking --- #
# ------------------------- #
class BTRanking(Ranking):
    def __init__(self, name: str='', players=None):
        super().__init__(name=name,
                        datamodel=KeyModel(factory=lambda x: x.level()),
                        backend=PlayerLevel(),
                        handler=KeyChecker(),
                        players=players)
        
    def forward(self, *args, **kwargs):
        self.handler.handle_observations(infer=self.backend, datamodel=self.datamodel)
        
     
# ------------------------- #
# --- Empirical Ranking --- #
# ------------------------- #   
class WinRate(Ranking):
    def __init__(self, name: str='', default: float=-1.0, players=None):
        backend = PlayerWinPRC(default=default)
        super().__init__(name=name,
                         standing=Standing(),
                         datamodel=KeyModel(factory = lambda x: backend.win_rate(x)),
                         backend=backend,
                         handler=KeyChecker(),
                         players=players)


# ------------------------- #
# ---- Common Ranking ----- #
# ------------------------- #
class BasicElo(Ranking):
    def __init__(self, name: str='', default: float=1500.0, k: float=20.0, lc: float=400.0, players=None):
        super().__init__(name=name,
                        datamodel=KeyModel(default=default),
                        backend=Elo(k=k, lc=lc),
                        handler=GameByGame(),
                        players=players)
    
    '''
    def predict(self, game):
        _, teams_as_ratings, _, _ = self.handler.match_formating(datamodel=self.datamodel, game=game)
        r1 = teams_as_ratings[0][0]
        r2 = teams_as_ratings[1][0]
        return self.backend.expectedScore(rating1=r1, rating2=r2)
    '''


class BasicGlicko(Ranking):
    def __init__(self, name: str='', handler=BatchGame(), mu: float=1500.0, sigma: float=350.0, players=None):
        super().__init__(name= name,
                        datamodel=GaussianModel(default=GlickoRating(mu, sigma)),
                        backend=Glicko(),
                        handler=handler,
                        players=players)

    @get_disamb
    def __step1(self):
        # TODO: check which player iterator to use
        for player in self:
            rating = self.datamodel.get(player)
            rating.sigma = self.backend.prePeriod_RD(rating)

    def forward(self, *args, **kwargs):
        self.__step1()
        self.handler.handle_observations(infer=self.backend, datamodel=self.datamodel, *args, **kwargs)
    
    '''    
    def predict(self, game):
        _, teams_as_ratings, _, _ = GameByGame().match_formating(datamodel=self.datamodel, game=game)
        r1 = teams_as_ratings[0][0]
        r2 = teams_as_ratings[1][0]
        return self.backend.expectedScore(rating1=r1, rating2=r2)
    '''


class BasicOS(Ranking):
    def __init__(self, name: str='', model=None, players=None):
        super().__init__(name=name,
                        datamodel=GaussianModel(factory=lambda x: model.rating(name=x.name)),
                        backend=model,
                        handler=GameByGame(),
                        players=players)
    
    def quality(self, game) -> float:
        _, teams_as_ratings, _, _ = self.handler.match_formating(datamodel=self.datamodel, game=game)
        return self.backend.predict_draw(teams_as_ratings)

    '''
    def predict(self, game) -> float:
        _, teams_as_ratings, _, _ = self.handler.match_formating(datamodel=self.datamodel, game=game)
        return self.backend.predict_win(teams_as_ratings)[0]
    '''