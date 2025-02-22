from typing import List
from typeguard import typechecked

from rstt.player import Player

class Match():
    @typechecked
    def __init__(self, teams: List[List[Player]]) -> None:
        self.__teams = teams
        self.__scores = None
        
    # --- getter --- #
    def teams(self) -> List[List[Player]]:
        return self.__teams
    
    def players(self) -> List[List[Player]]:
        return [player for team in self.__teams for player in team]

    def opponents(self, player: Player) -> List[Player]:
        return [p for p in self.players() if p not in self.teammates(player)]
    
    def teammates(self, player: Player) -> List[Player]:
        for team in self.players():
            if player in team:
                return [p for p in team if p != player]
    
    def scores(self) -> List[float]:
        return self.__scores
    
    def score(self, player: Player):
        for team, score in zip(self.__teams, self.__scores):
            if player in team:
                return score
            
    def ranks(self) -> List[int]:
        return [len([other for other in self.__scores if other > value]) + 1 for value in self.__scores]
    
    # ??? Game.unpack() -> dict{players, scores, ranks, weight}
    
    # --- user interface --- #
    def live(self) -> bool:
        return True if self.__scores is None else False
    
    # --- internal mechanism --- #
    def __set_result(self, result: List[float]):
        if self.__scores is not None:
            msg = f'Attempt to assign a score to a game that has already one {self}'
            raise RuntimeError(msg) # ??? RuntimeError
        else:
            if not isinstance(result, list):
                msg  = f"result must be instance of List[float], received {type(result)}"
                raise ValueError(msg)
            if not isinstance(result[0], float):
                msg = f'result must be instance of List[float], received List[{type(result[0])}]'
                raise ValueError(msg)
            # TODO: check value, match lenght with teams etc.
            if len(result) != len(self._Match__teams):
                msg = f"""result lenght does not match number of teams,
                        len(result) == {len(result)}, excepted: {len(self._Match__teams)}"""
                raise ValueError(msg)
            self.__scores = result
        
    # --- magic methods --- #
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"{type(self)} - teams: {self.__teams}, scores: {self.__scores}"
         
    def __contains__(self, player: Player) -> bool:
        return player in self.players()
    
    
class Duel(Match):
    def __init__(self, player1: Player, player2: Player) -> None:
        super().__init__(teams=[[player1], [player2]])
        
    # --- getter --- #
    def player1(self) -> Player:
        return self._Match__teams[0][0]
    
    def player2(self) -> Player:
        return self._Match__teams[1][0]
    
    def opponent(self, player: Player):
        players = set(self.players())
        players.remove(player) # this can raise a KeyError, which is what we want
        return list(players)[0]
    
    def winner(self) -> Player:
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[0][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[1][0]
        else:
            return None
        #return self._Match__teams[0][0] if self._Match__scores[0] > self._Match__scores[1] else self._Match__teams[1][0]
    
    def loser(self) -> Player:
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[1][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[0][0]
        else:
            return None
        #return self._Match__teams[0][0] if self._Match__scores[1] > self._Match__scores[0] else self._Match__teams[1][0]
    
    def isdraw(self) -> bool:
        if not self._Match__scores:
            return False
        return True if self._Match__scores[0] == self._Match__scores[1] else False    