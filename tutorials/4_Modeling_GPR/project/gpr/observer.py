from rstt import Duel
from rstt.ranking import GameByGame
from rstt.stypes import SMatch, Observer, Inference, RatingSystem

from .utils import GameHistory, LeagueSystem, get_event_infos, set_event_importance, Modes
from .ratingsystem import RegionalRatings


class GlobalHandler(Observer):
    def __init__(self, dataset: GameHistory, league_handler: Observer, team_handler: Observer):
        self.dataset = dataset
        self.handlers = {Modes.League: league_handler,
                         Modes.Team: team_handler}

    def handle_observations(self, infer: Inference, datamodel: RegionalRatings, *args, **kwargs) -> None:
        for mode in Modes:
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

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, games: list[SMatch], *args, **kwargs):
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
