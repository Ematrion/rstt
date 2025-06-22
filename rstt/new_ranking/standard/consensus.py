from new_ranking import Ranking, Standing
from new_ranking.observer import ObsTemplate
from new_ranking.observer.game_observer import push_new_ratings
from new_ranking.observer.utils import *
from rstt.ranking import KeyModel
from rstt.stypes import SPlayer, Event, Achievement

from typeguard import typechecked
from typing import Optional

import numpy as np


@typechecked
def to_list_of_players(self, player: SPlayer, players: list[SPlayer], team: SPlayer, teams: list[SPlayer],
                       standing: Standing, ranking: Ranking) -> list[SPlayer]:
    observations = []
    if player:
        observations.append(player)
    if players:
        observations += players
    if team:
        observations.append(team)
    if teams:
        observations += teams
    if standing:
        observations += standing.keys()
    if ranking:
        observations += ranking.players()
    # NOBUG: user responsability to not pass a given game multiple time (or allow it)
    return observations


def get_rating_of_player(prior, data):
    data[RATING] = prior.get(data[PLAYER])


def new_player_rating(data, output):
    data[NEW_RATINGS] = {data[PLAYER]: output}


class PlayerLevel:
    def rate(self, player: SPlayer) -> float:
        return player.level()


class KeyChecker(ObsTemplate):
    def __init__(self):
        super().__init__()

        self.convertor: callable = to_list_of_players
        self.extractor: callable = lambda players: [
            {PLAYER: player} for player in players]
        self.query: callable = get_rating_of_player
        self.output_formater: callable = new_player_rating
        self.push: callable = push_new_ratings


class BTRanking(Ranking):
    def __init__(self, name: str, players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(factory=lambda x: x.level()),
                         backend=PlayerLevel(),
                         handler=KeyChecker(),
                         players=players)


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
    def rate(self, player: SPlayer, *args, **kwargs) -> dict[SPlayer, float]:
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
        return self._win_rate(player)

    def _win_rate(self, player: SPlayer):
        games = player.games()
        if games:
            games = games[-self.scope:]
            nb_wins = sum([1 for game in games if player is game.winner()])
            # QUEST: How to support arbitrary game outcomes
            # ??? sum([game.score(player) for game in games])
            total = len(games)
            winrate = nb_wins / total * 100
        else:
            winrate = self.default
        return winrate


class WinRate(Ranking):
    def __init__(self, name: str,
                 default: float = -1.0,
                 scope: float = np.iinfo(np.int32).max,
                 players: list[SPlayer] | None = None):
        super().__init__(name,
                         datamodel=KeyModel(default=default),
                         backend=PlayerWinPRC(default=default, scope=scope),
                         handler=KeyChecker(),
                         players=players)


class EventSocring():
    def __init__(self, window_range: int = 1, tops: int = 1) -> None:
        self.dataset = EventDataSet(window_range=window_range)
        self.tops = tops
        self.relevance: dict[str, dict[int, float]]

    def rate(self, player: SPlayer) -> list[Achievement]:
        # TODO: implement  Competition.achievement(player: SPlayer)
        # + Update stypes.Event protocol
        return [event.achievement(player) for event in self.dataset.window()
                if player in event.participants()]


class EventDataSet():
    def __init__(self, window_range: int = 1):
        self.events = []
        self.window_range = window_range

    def add(self, event: Event):
        if event.name() in [ev.name() for ev in self.events]:
            msg = f"Event {event.name()} already in the dataset"
            raise ValueError(msg)
        else:
            self.events.append(event)

    def window(self, window: Optional[int] = None):
        nb = window if window else self.window_range
        return self.events[-nb:]


class EventSummary(Ranking):
    def __init__(self, name: str,
                 window_range: int = 1, tops: int = 1,
                 players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(template=int),
                         backend=EventSocring(
                             window_range=window_range, tops=tops),
                         handler=KeyChecker(),
                         players=players)

        self.events = EventDataSet(window_range=window_range)
