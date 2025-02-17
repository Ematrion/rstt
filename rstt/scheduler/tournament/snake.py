from typing import List

from rstt import Duel
from rstt.scheduler.tournament.competition import Competition


class Snake(Competition):
    def __init(self, *args, **kwars):
        super().__init__(*args, **kwars)
        self.snake = []

    def initialise(self):
        self.snake = [player for player in self.seeding]
        self.snake.reverse()

    def generate_games(self):
        game = Duel(self.snake.pop(0), self.snake.pop(0))
        return [game]

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

        return finished