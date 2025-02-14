from typeguard import typechecked
from typing import List, Dict, Union, Tuple, Any, Optional

from rstt.stypes import Inference, DataModel
from rstt import Match, Player
import rstt.utils.utils as uu

# QUEST: Do Observer realy need to be typechecked ?


@typechecked
def assign_ratings(datamodel: DataModel, ratings: Dict[Player, Any]):
    for key, rating in ratings.items():
        datamodel.set(key, rating)
        
@typechecked
def match_formating(datamodel: DataModel, game: Match) -> Tuple[List[List[Player]], List[List[ Any]], List[int]]:
    teams_as_players = game.teams()
    teams_as_ratings = [[datamodel.get(player) for player in team] for team in teams_as_players]
    
    if game.live():
        scores, ranks = None, None
    else:
        scores = game.scores()
        ranks = game.ranks()
    
    return teams_as_players, teams_as_ratings, scores, ranks

@typechecked
def result_formating(players: List[List[Player]], ratings: List[List[Any]]) -> Dict[Player, Any]:
    return {p: r for p,r in zip(uu.flatten(players), uu.flatten(ratings))}


class GameByGame:
    @typechecked
    def handle_observations(self, infer: Inference,
                            datamodel: DataModel,
                            games: Optional[Union[Match, List[Match]]]=None,
                            event: Optional[Any]=None, # FIXME: when Tournament class is added and type defined
                            *args, **kwargs):
        if event:
            if games:
                msg = f'Incompatible parameters, Only one of games or event must be passed'
                raise ValueError(msg)
            else: 
                self.handle_observations(infer=infer, datamodel=datamodel, games=event.games())
        elif isinstance(games, Match):
            self.single_game(infer, datamodel, games, *args, **kwargs)
        else:
            for game in games:
                self.single_game(infer, datamodel, game, *args, **kwargs)
    
    @typechecked
    def single_game(self, infer: Inference, datamodel: DataModel, game: Match, *args, **kwargs):
        players, ratings, score, ranks = match_formating(datamodel, game)
        try: 
            output = infer.rate(ratings, ranks=ranks, *args, **kwargs)
        except:
            output = infer.rate(ratings, score, *args, **kwargs)
        new_ratings = result_formating(players, output)
        assign_ratings(datamodel, new_ratings)
    

class KeyChecker:
    def handle_observations(self, infer: Inference, datamodel: DataModel, *args, **kwargs):
        new_ratings = {}
        
        for player in datamodel.keys():
            new_ratings.update(infer.rate(player, *args, **kwargs))
        
        assign_ratings(datamodel, new_ratings)

class BatchGame:
    @typechecked
    def handle_observations(self, infer: Inference,
                            datamodel: DataModel,
                            games: Optional[Union[Match, List[Match]]]=None,
                            event: Optional[Any]=None, # FIXME
                            *args, **kwargs):
        
        if event:
            if games:
                msg = f'Incompatible parameters, Only one of games or event must be passed'
                raise ValueError(msg)
            else: 
                self.handle_observations(infer=infer, datamodel=datamodel, games=event.games())
        else:
            games = self.to_list(games)
            players = self.involved_keys(games)
            new_ratings = {}
            for player in players:
                player_games = self.game_of_interest(player, games)
                ratings = [datamodel.get(game.opponent(player)) for game in player_games]
                scores = [self.player_score(player, game) for game in player_games]
                rating = datamodel.get(player)
                new_ratings[player] = infer.rate(rating, ratings, scores)

            assign_ratings(datamodel, new_ratings)
    
    @typechecked      
    def player_score(self, player: Player, game: Match):
        if game.winner() == player:
            return 1.0
        elif game.loser() == player:
            return 0.0
        elif game.isdraw():
            return 0.5
        else:
            msg = f'Player {player} can not be asigned a score value (1.0, 0.5, 0.0) for Game {game}'
            raise ValueError(msg)
    
    @typechecked
    def game_of_interest(self, player: Player, games: List[Match]) -> List[Match]:
        return [game for game in games if player in game]
    
    @typechecked
    def involved_keys(self, games: List[Match]) -> List[Player]:
        winners = [game.winner() for game in games]
        losers = [game.loser() for game in games]
        return list(set(winners+losers))

    @typechecked
    def to_list(self, games: Union[Match, List[Match]]) -> List[Match]:
        if isinstance(games, Match):
            games = [games]
        return games

