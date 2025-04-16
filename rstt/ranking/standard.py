from rstt.ranking.ranking import Ranking, get_disamb
from rstt.ranking.datamodel import KeyModel, GaussianModel
from rstt.ranking.rating import GlickoRating
from rstt.ranking.inferer import Glicko, Elo, PlayerLevel, PlayerWinPRC, EventStanding
from rstt.ranking.observer import GameByGame, BatchGame, KeyChecker


# ------------------------- #
# --- Consensus Ranking --- #
# ------------------------- #
class BTRanking(Ranking):
    def __init__(self, name: str = '', players=None):
        """Consensus Ranking For the Bradley-Terry Model

        Ranking based on the player's level() method.
        This also work for Time varying player, inherited class from :class:`rstt.player.playerTVS.PlayerTVS`,
        But it needs to be updated manually everytime player's level is updated.

        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        players : _type_, optional
            SPlayer to add to the ranking, by default None

        .. warning::
            BTRanking validity is limited to Bradley-Terry like models and is not suited for simulation using 'None-transitive' level.

            Behaver that for player with 'hyper volatile' level (like the :class:`rstt.player.gaussian.GaussianPlayer` which has a level changing at each update),
            the BTRanking uses the level of the player in question during the last update, it does not check for a 'theoretical' or 'statistical' mean. 
        """
        super().__init__(name=name,
                         datamodel=KeyModel(factory=lambda x: x.level()),
                         backend=PlayerLevel(),
                         handler=KeyChecker(),
                         players=players)

    def forward(self, *args, **kwargs):
        """:meta private:"""
        self.handler.handle_observations(
            infer=self.backend, datamodel=self.datamodel)


# ------------------------- #
# --- Empirical Ranking --- #
# ------------------------- #
class WinRate(Ranking):  # !!! need Player (with history) but ranking is not generic
    def __init__(self, name: str = '', default: float = -1.0, players=None):
        """Ranking based on Win rate


        Ranking that tracks the winrate of :class:`rstt.player.player.Player`.
        The winrate his tracked 'automatically'.
        The update function does not take any parameters, win rate is computed directly with the player's game history.

        WinRate uses:

            1. :class:`rstt.ranking.datamodel.KeyModel` as datamodel
            2. :class:`rstt.ranking.inferer.PlayerWinPr`as backend
            3. :class:`rstt.ranking.observer.KeyChecker` as handler


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        default : float, optional
            A default rating value for when player have no game in their history, by default -1.0
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
        backend = PlayerWinPRC(default=default)
        super().__init__(name=name,
                         datamodel=KeyModel(
                             factory=lambda x: backend.win_rate(x)),
                         backend=backend,
                         handler=KeyChecker(),
                         players=players)


class SuccessRanking(Ranking):
    def __init__(self, name: str = ',', buffer: int = 1, nb: int = 1, players=None, default=None):
        """Merit Based Ranking

        Usefull to implement Ranking system like the one in  `tennis <https://en.wikipedia.org/wiki/ATP_rankings>`_ for example.

        SuccessRanking uses:

            1. :class:`rstt.ranking.datamodel.KeyModel` as datamodel
            2. :class:`rstt.ranking.inferer.EventStanding`as backend
            3. :class:`rstt.ranking.observer.KeyChecker` as handler

        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        buffer : int
            Backend parameter. The number of event to consider for the rating, starting from the last.
        nb : int
            Backend parameter. The actual number of event in the buffer to use for the ratings computation.
        default : Optional[Dict[int, float]], optional
            Backend Parameter. Mapping placement in event to points for the rating, by default None
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
        super().__init__(name=name,
                         datamodel=KeyModel(template=int),
                         backend=EventStanding(
                             buffer=buffer, nb=nb, default=default),
                         handler=KeyChecker(),
                         players=players)

    def add_event(self, *args, **kwargs):
        """Wrapper of :func:`rstt.ranking.inferer.EventStanding.add_event`
        """
        self.backend.add_event(*args, **kwargs)

    def remove_event(self, *args, **kwargs):
        """Wrapper of :func:`rstt.ranking.inferer.EventStanding.remove_event"""
        self.backend.remove_event(*args, **kwargs)

    def forward(self, event=None, points=None, *args, **kwargs):
        """:meta private:"""
        if event:
            self.backend.add_event(event, points)
        self.handler.handle_observations(infer=self.backend,
                                         datamodel=self.datamodel,
                                         *args, **kwargs)


# ------------------------- #
# ---- Common Ranking ----- #
# ------------------------- #
class BasicElo(Ranking):
    def __init__(self, name: str = '', default: float = 1500.0, k: float = 20.0, lc: float = 400.0, players=None):
        """Simple Elo System

        Impement a very simple ELo rating system.

        BasicElo uses:

            1. :class:`rstt.ranking.datamodel.KeyModel` as datamodel
            2. :class:`rstt.ranking.inferer.Elo`as backend
            3. :class:`rstt.ranking.observer.GameByGame` as handler

        .. note::
            In this implementation, the K value is a constant.
            In real world application, K can vary based on player's experience, or match's relevance.

        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        default : float, optional
            Datamodel parameter, a default elo rating, by default 1500.0
        k : float, optional
            Backend parameter, the K value, by default 20.0
        lc : float, optional
            Backend parameter, constant dividing the ratings difference in the expected score formula , by default 400.0
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """
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
    def __init__(self, name: str = '', handler=BatchGame(), mu: float = 1500.0, sigma: float = 350.0, players=None):
        """Simple Glicko system

        Implement A glicko rating system as originaly `proposed <https://www.glicko.net/glicko/glicko.pdf>`_.

        BasicGlicko uses:

            1. :class:`rstt.ranking.datamodel.GaussianModel` as datamodel
            2. :class:`rstt.ranking.inferer.Glicko`as backend
            3. :class:`rstt.ranking.observer.BatchGame` as handler

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
        self.handler.handle_observations(
            infer=self.backend, datamodel=self.datamodel, *args, **kwargs)

    '''    
    def predict(self, game):
        _, teams_as_ratings, _, _ = GameByGame().match_formating(datamodel=self.datamodel, game=game)
        r1 = teams_as_ratings[0][0]
        r2 = teams_as_ratings[1][0]
        return self.backend.expectedScore(rating1=r1, rating2=r2)
    '''


class BasicOS(Ranking):
    def __init__(self, name: str = '', model=None, players=None):
        """Simple OpenSkill Integretion

        Ranking to integrate an `openskill <https://openskill.me/en/stable/manual.html>`_ model into the rstt package.

        BasicOS uses:

            1. :class:`rstt.ranking.datamodel.GaussianModel` as datamodel to store model.rating instances.
            2. One of openskill models passed as parameter.
            3. :class:`rstt.ranking.observer.GameByGame` as handler


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        model : openskills.models
            One of openskills.models implementation, by default None
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None


        Example:
        --------
        .. code-block:: python
            :linenos:

            from rstt import Player, BasicOS
            from openskill.models import PlackettLuce

            competitors = Player.create(nb=10)
            pl = BasicOS(name='Plackett-Luce', model= PlackettLuce(), players=competitors)
            pl.plot()
        """
        super().__init__(name=name,
                         datamodel=GaussianModel(
                             factory=lambda x: model.rating(name=x.name)),
                         backend=model,
                         handler=GameByGame(),
                         players=players)

    def quality(self, game) -> float:
        """Wrapper arround openskill model predict_draw function"""
        _, teams_as_ratings, _, _ = self.handler.match_formating(
            datamodel=self.datamodel, game=game)
        return self.backend.predict_draw(teams_as_ratings)

    '''
    def predict(self, game) -> float:
        _, teams_as_ratings, _, _ = self.handler.match_formating(datamodel=self.datamodel, game=game)
        return self.backend.predict_win(teams_as_ratings)[0]
    '''
