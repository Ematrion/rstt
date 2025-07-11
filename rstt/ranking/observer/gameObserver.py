"""Game based Observers
"""

from .obs import ObsTemplate
from .utils import *


class GameByGame(ObsTemplate):
    def __init__(self):
        """Game by Game updating Procedure

        Implementing an iterative approach where each observations triggers the entire updating workflows.
        In particular, new ratings are stored inbetween of each iterations, and the prior ones are lost.

        Observations
        ------------
        game : SMatch, optional
            a game justifying a ranking update, by default None
        games : list[SMatch], optional
            a list of games, by default None
        event : Event, optional
            the observer uses Event.games() to extract the observations, by defualt None
        events: list[Event], optional
            a list of Event, by default None

        Datamodel
        ---------
        Rating: any
            Game based observers make no assumption on ratings type.

        Inferer.rate
        ------------
        teams : list[list[SPlayer]]
        scores : list[float]
        ranks : list[float]
        ratings_groups : list[list[any]]
        """
        super().__init__()
        self.convertor = to_list_of_games
        self.extractor = lambda duels: [duel_data(duel) for duel in duels]
        self.query = get_ratings_groups_of_teams_from_datamodel
        self.output_formater = new_ratings_groups_to_ratings_dict
        self.push = push_new_ratings

    def _set_posteriori(self, *args, **kwargs) -> None:
        # trick: time <=>
        self.posteriori = self.prior


class BatchGame(ObsTemplate):
    def __init__(self):
        """All Matches at once updating procedure

        Alternative to the :class:`rstt.ranking.observer.GamebyGame` observer. Some rating system, like Elo and Glicko
        support updates where all matches are considered at once for the rating update.

        In this workflows, ratings are stored after all matches have been processed. Every computation is performed using the prior ratings
        (i.e the one stored in the datamodel before the method call)

        Observations
        ------------
        game : SMatch, optional
            a game justifying a ranking update, by default None
        games : list[SMatch], optional
            a list of games, by default None
        event : Event, optional
            the observer uses Event.games() to extract the observations, by defualt None
        events: list[Event], optional
            a list of Event, by default None

        Datamodel
        ---------
        Rating: any
            Game based observers make no assumption on ratings type.

        Inferer.rate
        ------------
        teams : list[list[SPlayer]]
        scores : list[float]
        ratings_groups : list[list[any]]
        """
        super().__init__()
        self.convertor = to_list_of_games
        self.extractor = players_records
        self.query = get_ratings_groups_of_teams_from_datamodel
        self.output_formater = new_ratings_groups_to_ratings_dict
        self.push = push_new_ratings
