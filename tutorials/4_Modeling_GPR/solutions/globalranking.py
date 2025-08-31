from typing import Any, List
from rstt import Ranking, Duel
# from rstt.old_ranking import Standing, KeyModel, Elo, GameByGame
from rstt.ranking import Standing, KeyModel, Elo, GameByGame
from rstt.stypes import RatingSystem, Inference, Observer, SMatch, SPlayer, Event

from .utils import LeagueSystem, GameHistory, get_event_infos, set_event_importance, reset_ratings
from .scene import MODES, TEAM, LEAGUE


class RegionalRatings(KeyModel):
    def __init__(self, x: int, y: int,
                 ecosystem: LeagueSystem,
                 ratings: dict[str, RatingSystem]) -> None:
        super().__init__(factory=lambda x: x)
        self.x = x
        self.y = y

        self.ratings = ratings
        self.ecosystem = ecosystem

    def keys(self):
        return self.ratings[TEAM].keys()

    def ordinal(self, rating: SPlayer) -> float:
        # team
        team = rating
        # team rating
        team_elo = self.ratings[TEAM].get(team)
        # team region
        region = self.ecosystem.region_of(team)
        # league of the region (SPlayer)
        league = self.ecosystem.league_of(region)
        # rating of league
        league_elo = self.ratings[LEAGUE].get(league)
        # Power Score Formula
        return (self.x * team_elo) + (self.y * league_elo)


'''
Using an Elo Inference, and modify the .K attribute

class PowerRater(Inference):
    def __init__(self):
        ...

    def rate(self, *args, **kwargs) -> Any:
        ...
'''


'''
Using a simple GameByGame Observer

class GlobalHandler(Observer):
    def __init__(self):
        ...

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs) -> None:
        ...
'''


class GlobalHandler(Observer):
    def __init__(self, dataset: GameHistory, league_handler: Observer, team_handler: Observer):
        self.dataset = dataset
        self.handlers = {LEAGUE: league_handler, TEAM: team_handler}

    def handle_observations(self, infer: Inference, datamodel: RegionalRatings, *args, **kwargs) -> None:
        for mode in MODES:
            for event in self.dataset.window(mode):
                # get event importance
                infos = get_event_infos(event)
                # set event importance
                set_event_importance(infer, infos)
                # Game based update
                games = event.games()
                self.handlers[mode].handle_observations(
                    infer=infer, datamodel=datamodel.ratings[mode], games=games, *args, **kwargs)


class LeagueGBG(GameByGame):
    def __init__(self, ecosystem: LeagueSystem) -> None:
        super().__init__()
        self.ecosystem = ecosystem

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, games: List[SMatch], *args, **kwargs):
        league_games = [self.team_to_league_game(game) for game in games]
        league_games = [game for game in league_games if game]
        return super().handle_observations(infer=infer, datamodel=datamodel, games=league_games, *args, **kwargs)

    def team_to_league_game(self, game: Duel):
        # returned value
        league_duel = None

        team1, team2 = game.teams()
        region1 = self.ecosystem.region_of(*team1)
        region2 = self.ecosystem.region_of(*team2)

        if region1 != region2:
            league_duel = Duel(player1=self.ecosystem.league_of(region1),
                               player2=self.ecosystem.league_of(region2))
            league_duel._Match__set_result(game.scores())

        return league_duel


class GlobalRanking(Ranking):
    def __init__(self, name: str, ecosystem: LeagueSystem,
                 x: float = 0.8, y: float = 0.2,
                 team_elo: any = 1300, league_elo: any = 1300,
                 lc: float = 600.0,
                 mode_range: dict[str, int] = {TEAM: 2, LEAGUE: 3}):

        self.ecosystem = ecosystem
        self.dataset = GameHistory(mode_range=mode_range)

        super().__init__(name=name,
                         datamodel=RegionalRatings(x=x, y=y,
                                                   ecosystem=ecosystem,
                                                   ratings={TEAM: KeyModel(default=team_elo),
                                                            LEAGUE: KeyModel(default=league_elo)}),
                         backend=Elo(k=0, lc=lc),
                         handler=GlobalHandler(dataset=self.dataset, league_handler=LeagueGBG(ecosystem=self.ecosystem), team_handler=GameByGame()))

    def forward(self, event: Event, *args, **kwargs):
        # store event
        if event:
            self.dataset.add(event)

        # reset ratings
        self.standing = Standing()
        reset_ratings(self.datamodel)

        # ratings update
        self.handler.handle_observations(
            infer=self.backend, datamodel=self.datamodel, *args, **kwargs)

    '''
        # update leagues and teams ratings
        for mode in MODES:
            # different window size
            for event in self.dataset.window(mode):
                # get event importance
                infos = get_event_infos(event)
                # set event importance
                set_event_importance(self.backend, infos)
                # update performed by the observer - 'game based'
                games = event.games()
                self.handler.handle_observations(
                    infer=self.backend, datamodel=self.datamodel.ratings[mode], games=games, *args, **kwargs)
                # TODO: observer for league mode
    '''
