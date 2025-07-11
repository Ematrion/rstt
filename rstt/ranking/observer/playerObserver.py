"""Player based Observers
"""

from .obs import ObsTemplate
from .utils import *


class PlayerChecker(ObsTemplate):
    def __init__(self):
        """Update Procedure based on Player's data

        Iterate over a list of SPlayer, each triggering a inferer.rate()
        call and the new ratings are instantly pushed in the datamodel.
        The assumption is that the player instance itself contains all
        the necessary informations to compute a rating.

        .. caution::
            Prior ratings, stored in the datamodel, are ignored and not passed to the inferer.
            The output of the inferer.rate defines the post ratings,
            which can introduce inconsistency in rating type for the datamodel.

        Observations
        ------------
        player : SMatch, optional
            a game justifying a ranking update, by default None
        players : list[SMatch], optional
            a list of games, by default None
        team : Event, optional
            the observer uses Event.games() to extract the observations, by defualt None
        teams : list[Event], optional
            a list of Event, by default None
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
        player: SPlayer
        """
        super().__init__()
        self.convertor = to_list_of_players
        self.extractor = lambda players: [
            {PLAYER: player}for player in players]
        self.query = no_query
        self.output_formater = new_player_rating
        self.push = push_new_ratings
