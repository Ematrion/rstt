from rstt import Duel

from rstt.stypes import Inference, RatingSystem, SPlayer, SMatch, Event
from .obs import ObsTemplate
from rstt.utils.observer import *

from typing import Optional
from typeguard import typechecked

# -------------------#
# ---- convertor --- #
# ------------------ #


@typechecked
def to_list_of_games(game: Optional[SMatch] = None,
                     games: Optional[list[SMatch]] = None,
                     event: Optional[Event] = None,
                     events: Optional[list[Event]] = None):
    observations = []
    if game:
        observations.append(game)
    if games:
        observations += games
    if event:
        observations += event.games()
    if events:
        for ev in events:
            observations += ev.games()
    # NOBUG: user responsability to not pass a given game multiple time (or allow it)
    return observations

# -------------------#
# ---- extractor --- #
# ------------------ #


'''
    TODO:
        - one general extractor
            def extract(key_args = list[str])
        - funcs extracting only key_arg
    
    QUEST:
        - How to specifiy the data_point nature ? 
        - How to build the data as a list of data_point ?
        - Should the convertor 're-design' the observations (and not just 'clean' the input)
        for example: list[SMatch] -> list[(SPlayer, list[SMatch])] for the case of BatchGame obs
        - should we do typing of the 'data', like with typing.TypedDict or namedtuple ?

'''

# @typechecked


def duel_data(duel: Duel) -> dict[str, any]:
    # returned value
    data = {}
    # data_points are game summary
    data[TEAMS] = duel.teams()
    data[SCORES] = duel.scores()
    data[RANKS] = duel.ranks()
    return data


# @typechecked
def players_encounters(duels: list[Duel]) -> list[dict[str, any]]:
    # returned value
    data = {}
    # data_points are player 'performance summary'
    return [{TEAMS: [[player], [duel.opponent(player) for duel in duels if player in duel]],
             SCORES: [duel.score(player) for duel in duels if player in duel]} for player in active_players(duels)]

# -------------------#
# ------ query ----- #
# ------------------ #


# @typechecked
def get_ratings_groups_of_teams_from_datamodel(prior: dict[SPlayer, any], data: dict[str, any]) -> None:
    # inplace data editing
    data[RATINGS_GROUPS] = [
        [prior[player] for player in team]
        for team in data[TEAMS]]

    # --------------------- #
    # -- output_formater -- #
    # --------------------- #

    # @typechecked


def new_ratings_groups_to_ratings_dict(data: dict[str, any], output: list[list[any]]):
    # inplace data editing
    data[NEW_RATINGS] = {}
    for team, team_ratings in zip(data[TEAMS], output):
        for player, rating in zip(team, team_ratings):
            data[NEW_RATINGS][player] = rating


# -------------------#
# ------ push ------ #
# ------------------ #

# @typechecked
def push_new_ratings(data: dict[str, any], posteriori: dict[SPlayer, any]):
    for player, rating in data[NEW_RATINGS].items():
        posteriori[player] = rating


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
        self.extractor = players_encounters
        self.query = get_ratings_groups_of_teams_from_datamodel
        self.output_formater = new_ratings_groups_to_ratings_dict
        self.push = push_new_ratings
