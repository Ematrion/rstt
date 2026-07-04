from rstt import BetterWin, Competition, Duel
from rstt.ranking.ranking import Ranking
from rstt.stypes import SPlayer, Solver


class StagedEvent(Competition):
    def __init__(self, name: str, seeding: Ranking,
                 stages: list[type[Competition]],
                 stage_names: list[str],
                 solver: Solver = BetterWin(),
                 cashprize: dict[int, float] | None = None):
        super().__init__(name, seeding, solver, cashprize)
        
        self.stages = stages
        self.stage_names = stage_names

    # --- abstract method --- #
    def generate_games(self) -> list[Duel]:
        ...

    def _standing(self) -> dict[SPlayer, int]:
        ...

    def _end_of_stage(self) -> bool:
        ...

    # --- optional  --- #
    def _initialise(self) -> None:
        return super()._initialise()

    def _update(self) -> None:
        return super()._update()
