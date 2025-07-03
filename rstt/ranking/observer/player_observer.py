from .obs import ObsTemplate
from .utils import *


class PlayerChecker(ObsTemplate):
    def __init__(self):
        super().__init__()
        self.convertor = to_list_of_players
        self.extractor = lambda players: [
            {PLAYER: player}for player in players]
        self.query = no_query
        self.output_formater = new_player_rating
        self.push = push_new_ratings


class NoHandling(ObsTemplate):
    def __init__(self):
        super().__init__()
        self.extractor = no_extraction
        self.convertor = no_convertion
        self.query = no_query
        self.output_formater = no_formating
        self.push = no_push
