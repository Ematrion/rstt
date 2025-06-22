import inspect
from rstt.stypes import SPlayer, SMatch

# --- Observation's Data --- #
PLAYERS = 'players'
TEAMS = 'teams'
RATINGS_GROUPS = 'ratings_groups'
RATINGS_OPPONENTS = 'ratings_opponents'
RATING = 'rating'
RATING1 = 'rating1'
RATING2 = 'rating2'
RANKS = 'ranks'
SCORES = 'scores'
WEIGTS = 'weights'
NEW_RATINGS = 'new_ratings'


# --- Rate Method Calls --- #
def get_function_args(func: callable):
    return inspect.getfullargspec(func).args


def filter_valid_args(args_name: list[str], **kwargs):
    return {key: value for key, value in kwargs.items() if key in args_name}


def call_function_with_args(func: callable, **kwargs):
    func_args = get_function_args(func)
    call_args = filter_valid_args(args_name=func_args, **kwargs)
    return func(**call_args)


# --- temporary loc for utils --- #
def active_players(games: list[SMatch]) -> list[SPlayer]:
    return list(set([player for players in [game.players() for game in games] for player in players]))
