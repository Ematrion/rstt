from .obs import ObsTemplate
from .utils import *


class GameByGame(ObsTemplate):
    def __init__(self):
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
        super().__init__()
        self.convertor = to_list_of_games
        self.extractor = players_records
        self.query = get_ratings_groups_of_teams_from_datamodel
        self.output_formater = new_ratings_groups_to_ratings_dict
        self.push = push_new_ratings
