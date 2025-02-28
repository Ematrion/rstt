from typing import List, Dict

from rstt import Duel, Player
from . import Competition


class Snake(Competition):
    def __init__(self, *args, **kwars):
        super().__init__(*args, **kwars)
        self.snake = []

    def _initialise(self) -> None:
        self.snake = [player for player in self.seeding]
        self.snake.reverse()
    
    def _update(self) -> None:
        self.snake.insert(0, self.played_matches[-1][0].winner())

    def _end_of_stage(self) -> bool:
        return len(self.snake) == 1
    
    def _standing(self) -> Dict[Player, int]:
        standing = {games[0].loser(): len(self.participants)-r
                         for r, games in enumerate(self.played_matches)}
        standing[self.played_matches[-1][0].winner()] = 1
        return standing
        
    def generate_games(self) -> List[Duel]:
        return [Duel(self.snake.pop(0), self.snake.pop(0))]


        
    '''
    def edit(self, games: List[Duel]):
        for game in games:
            # winner can will play another game
            self.snake.insert(0, game.winner())
            # loser journey ends
            self.standing[game.loser()] = len(self.snake) + 1

        # check stop condition
        if len(self.snake) == 1:
            self.standing[self.snake[0]] = 1
            finished = True
        else:
            finished = False

        return finished'''