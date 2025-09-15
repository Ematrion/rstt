from rstt import BetterWin, Competition, Duel
from rstt.ranking.ranking import Ranking
from rstt.stypes import SPlayer, Solver


class StagedEvent(Competition):
    def __init__(self, name: str, seeding: Ranking, solver: Solver = BetterWin()):
        super().__init__(name, seeding, solver)

    # --- abstract method --- #
    def generate_games(self) -> list[Duel]:
        ...

    def _standing(self) -> dict[SPlayer, int]:
        ...

    def _end_of_stage(self) -> bool:
        ...

    # --- empty method --- #
    def _initialise(self) -> None:
        return super()._initialise()

    def _update(self) -> None:
        return super()._update()
