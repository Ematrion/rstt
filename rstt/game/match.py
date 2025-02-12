from typing import List

from rstt.player import Player

class Match():
    def __init__(self, teams: List[List[Player]]) -> None:
        self._teams = teams
        self.__scores = None
        
    # --- getter --- #
    def teams(self) -> List[List[Player]]:
        return self._teams
    
    def participants(self) -> List[List[Player]]:
        return [player for team in self.teams for player in team]

    def opponents(self, player: Player) -> List[Player]:
        return [p for p in self.participants() if p not in self.teammates(player)]
    
    def teammates(self, player: Player) -> List[Player]:
        for team in self.participants:
            if player in team:
                return [p for p in team if p != player]
    
    def scores(self) -> List[float]:
        return self.__scores
    
    def ranks(self) -> List[int]:
        ''''''
    
    # --- user interface --- #
    def live(self) -> bool:
        return True if self.__scores is None else False
    
    # --- internal mechanism --- #
    def __set_results(self, result: List[float]):
        # TODO: check value, match lenght with teams etc.
        self.__results = result
        
    # --- magic methods --- #
    def __str__(self) -> str:
        return f"Match - teams: {self._teams}, scores: {self.__scores}"
         
    def __contains__(self, player: Player) -> bool:
        return player in self.participants()