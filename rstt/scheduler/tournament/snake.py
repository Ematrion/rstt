from typing import List, Dict

from rstt import Duel
from rstt.stypes import SPlayer
from . import Competition


class Snake(Competition):
    """The Snake Tournament

    This format is not a standard one. It is a model I detail and justify the interest in my master thesis and should be the subject of a paper
    in an hopefully near future.

    It does have some ressamblances with the `Ladder tournament <https://en.wikipedia.org/wiki/Ladder_tournament>`_.
    I am aware of two practical instances of uses:
        - The bonus round in the fencing challenge of the `modern pentathlon <https://en.wikipedia.org/wiki/Modern_pentathlon>`_ at the Paris Olympics 2024.
        - A cooking show with a `Hidden last chance <https://fr.wikipedia.org/wiki/Saison_14_de_Top_Chef>`_ secret tournament.

    Quick Overview:
        - For n participants it produces n-1 matches.
        - Every participants plays at least one match.
        - The final standing is an untied ranking.
        - Matches are all 'a priori balanced'.
    """

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

    def _standing(self) -> Dict[SPlayer, int]:
        standing = {games[0].loser(): len(self.participants())-r
                    for r, games in enumerate(self.played_matches)}
        standing[self.played_matches[-1][0].winner()] = 1
        return standing

    def generate_games(self) -> List[Duel]:
        return [Duel(self.snake.pop(0), self.snake.pop(0))]
