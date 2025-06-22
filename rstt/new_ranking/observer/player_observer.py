from rstt.stypes import Event
from .obs import ObsTemplate
from rstt.new_ranking.observer.utils import *

from typeguard import typechecked
from typing import Optional

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


class PlayerChecker(ObsTemplate):
    def __init__(self):
        super().__init__()
        self.convertor = lambda x: x
        self.extractor = lambda x: x
        self.query = None
        self.output_formater = None
        self.push = None
