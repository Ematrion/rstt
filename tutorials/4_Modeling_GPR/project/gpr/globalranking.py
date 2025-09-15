from typing import Any

from rstt import Ranking, Standing
from rstt.ranking import KeyModel, GameByGame, Elo
from rstt.stypes import Event

# from .ratingsystem import RegionalRatings
# from .observer import GlobalHandler, LeagueGBG

from project.gpr import RegionalRatings, GlobalHandler, LeagueGBG

from .utils import LeagueSystem, GameHistory, reset_ratings, Modes


RANGES = {Modes.Team: 2,
          Modes.League: 3}


class GlobalRanking(Ranking):
    def __init__(self, name: str, ecosystem: LeagueSystem,
                 x: float = 0.8, y: float = 0.2,
                 team_elo: Any = 1300, league_elo: Any = 1300,
                 lc: float = 600.0,
                 mode_range: dict[str, int] = {Modes.Team: 2, Modes.League: 3}):

        self.ecosystem = ecosystem
        self.dataset = GameHistory(mode_range=mode_range)

        super().__init__(name=name,
                         datamodel=RegionalRatings(x=x, y=y,
                                                   ecosystem=ecosystem,
                                                   ratings={Modes.Team: KeyModel(default=team_elo),
                                                            Modes.League: KeyModel(default=league_elo)}),
                         backend=Elo(k=0, lc=lc),
                         handler=GlobalHandler(dataset=self.dataset, league_handler=LeagueGBG(ecosystem=self.ecosystem), team_handler=GameByGame()))

    def forward(self, event: Event, *args, **kwargs):
        # store event
        if event:
            self.dataset.add(event)

        # reset ratings
        self.standing = Standing()
        reset_ratings(self.datamodel.ratings[Modes.Team])
        reset_ratings(self.datamodel.ratings[Modes.League])

        # ratings update
        self.handler.handle_observations(
            infer=self.backend, datamodel=self.datamodel, *args, **kwargs)
