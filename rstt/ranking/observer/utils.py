from rstt.stypes import SPlayer, SMatch, Event, RatingSystem
from rstt import Duel
# from rstt.ranking.ranking import Ranking
# from rstt.ranking.standing import Standing


from typeguard import typechecked
from typing import Optional

import inspect

# --- Observation's Data --- #
PLAYER = 'player'
PLAYERS = 'players'
TEAM = 'team'
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


# --- CONVERTOR --- #
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


@typechecked
def to_list_of_players(player: Optional[SPlayer] = None,
                       players: Optional[list[SPlayer]] = None,
                       team: Optional[SPlayer] = None,
                       teams: Optional[list[SPlayer]] = None,
                       event: Optional[Event] = None,
                       events: Optional[list[Event]] = None
                       # standing: Optional[Standing] = None,
                       # ranking: Optional[Ranking] = None
                       ) -> list[SPlayer]:
    observations = []
    if player:
        observations.append(player)
    if players:
        observations += players
    if team:
        observations.append(team)
    if teams:
        observations += teams
    if event:
        observations += event.participants()
    if events:
        for ev in events:
            observations += ev.participants()
    # if standing:
    #    observations += standing.keys()
    # if ranking:
    #    observations += ranking.players()
    # NOBUG: user responsability to not pass a given player multiple time (or allow it)
    return observations


# --- EXTRACTOR --- #
def duel_data(duel: Duel) -> dict[str, any]:
    # ??? match: Smatch - does it change anything
    # returned value
    data = {}
    # data_points are game summary
    data[TEAMS] = duel.teams()
    data[SCORES] = duel.scores()
    data[RANKS] = duel.ranks()
    return data


def players_records(duels: list[Duel]) -> list[dict[str, any]]:
    # returned value
    datas = []
    for player in active_players(duels):
        # game relevant to the player
        targets = [duel for duel in duels if player in duel]

        # data_points as player 'performance summary'
        data_point = {}
        data_point[TEAMS] = [[player], [
            duel.opponent(player) for duel in targets]]
        data_point[SCORES] = [duel.score(player) for duel in targets]

        datas.append(data_point)
    return datas


# --- QUERY --- #
def get_ratings_groups_of_teams_from_datamodel(prior: RatingSystem, data: dict[str, any]) -> None:
    # inplace data editing
    data[RATINGS_GROUPS] = [[prior.get(player) for player in team]
                            for team in data[TEAMS]]


def get_rating_of_player(prior: RatingSystem, data: dict[str, any]):
    data[RATING] = prior.get(data[PLAYER])


# --- FORMATER --- #
def new_ratings_groups_to_ratings_dict(data: dict[str, any], output: list[list[any]]):
    # inplace data editing
    data[NEW_RATINGS] = {}
    for team, team_ratings in zip(data[TEAMS], output):
        for player, rating in zip(team, team_ratings):
            data[NEW_RATINGS][player] = rating


def new_player_rating(data: dict[str, any], output: any):
    data[NEW_RATINGS] = {data[PLAYER]: output}


# --- PUSH --- #
def push_new_ratings(data: dict[str, any], posteriori: RatingSystem):
    for player, rating in data[NEW_RATINGS].items():
        posteriori.set(player, rating)


# --- Clean Method Calls --- #
def get_function_args(func: callable):
    return inspect.getfullargspec(func).args


def filter_valid_args(args_name: list[str], **kwargs):
    return {key: value for key, value in kwargs.items() if key in args_name}


def call_function_with_args(func: callable, **kwargs):
    func_args = get_function_args(func)
    call_args = filter_valid_args(args_name=func_args, **kwargs)
    return func(**call_args)


# --- Others --- #
def active_players(games: list[SMatch]) -> list[SPlayer]:
    return list(set([player for players in [game.players() for game in games] for player in players]))


# --- no processing --- #
def no_convertion(*args, **kwargs) -> any:
    # !!! probably not what a user expect. BUT what does he expect ?
    return (*args, *kwargs)


def no_extraction(observations: any) -> any:
    return observations


def no_query(prior: RatingSystem, data: any):
    pass


def no_formating(data: any, output: any):
    pass


def no_push(data: any, posteriori: RatingSystem):
    pass
