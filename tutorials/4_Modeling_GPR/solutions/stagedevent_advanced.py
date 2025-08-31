from typing import Dict, List, Set
from rstt import BetterWin, Competition, Duel, SuccessRanking
from rstt.ranking.ranking import Ranking
from rstt.stypes import SPlayer, Solver

from .utils import get_event_infos, EVENT_NAMING
import parse


class StagedEvent(Competition):
    def __init__(self, name: str, seeding: Ranking,
                 tournaments: list[type[Competition]],
                 stage_names: list[str],
                 solver: Solver = BetterWin(),
                 cashprize: dict[int, float] | None = None):
        super().__init__(name, seeding, solver, cashprize)

        self.tournaments = tournaments
        self.stage_names = stage_names

        # basic usage
        self.stages: list[Competition] = None
        self.current: int = None
        self.round_games: list[Duel] = None
        self.live_ranking = SuccessRanking(name=f"self.name() - Ranking",
                                           buffer=len(self.tournaments),
                                           nb=len(self.tournaments))

        # qualif/elim
        self.invited: list[list[SPlayer]] = None
        self.qualified: list[list[int]] = None

    # abstract method override
    def generate_games(self) -> List[Duel]:
        self.round_games = self.stages[self.current].generate_games()
        return self.round_games

    def _end_of_stage(self) -> bool:
        return len(self.stages) == len(self.tournaments) and all([stage.over() for stage in self.stages])

    def _standing(self) -> Dict[SPlayer, int]:
        return {player: self.live_ranking[player]+1 for player in self.participants}

    # optional override
    def _initialise(self) -> None:
        self.stages = []
        self.current = 0
        self._new_stage()

    def _update(self) -> None:
        stage = self.stages[self.current]
        stage.edit(self.round_games)
        self.round_games = None
        if not stage.live():
            stage.trophies()
            self.current += 1

            # update ranking
            self.update_live_ranking(stage)

            # next stage
            if self.current < len(self.tournaments):
                self._new_stage()

    # unusual override
    def registration(self, players: list[SPlayer] = None, invited: list[list[SPlayer]] = None, qualified: list[list[int]] = None):
        participants = []
        if invited and qualified:
            self.invited = invited
            self.qualified = qualified
            for invitation in invited:
                participants += invitation
        else:
            participants = players
            self.invited = [participants for _ in self.tournaments]
            self.qualified = [[] for _ in self.tournaments]

        # make sure all participants are tracked by the ranking
        self.live_ranking.add(participants)

        return super().registration(participants)

    # specific
    def _new_stage(self):
        tournament = self.tournaments[self.current]
        stage_name = f"{self.name()}{self.stage_names[self.current]}"
        stage = tournament(name=stage_name,
                           seeding=self.live_ranking,
                           solver=self.solver)
        stage.registration(self.qualification())
        stage.start()
        self.stages.append(stage)

    def qualification(self) -> list[SPlayer]:
        if self.qualified[self.current]:
            return self.invited[self.current] + self.live_ranking[self.qualified[self.current]]
        else:
            return self.invited[self.current]

    def update_live_ranking(self, stage: Competition) -> Dict[SPlayer, int]:
        tot = len(self.participants())
        points = {i: (100-i) * 10**self.current
                  for i in range(1, tot+1)}
        self.live_ranking.update(event=stage, points=points)
