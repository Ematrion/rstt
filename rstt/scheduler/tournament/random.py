from .groups import RoundRobin
from rstt.ranking.ranking import Ranking
from rstt import BetterWin
from rstt.stypes import Solver

import random


class RandomRound(RoundRobin):
    def __init__(self, name: str, seeding: Ranking, solver: Solver = BetterWin(), cashprize: dict[int, float] = {}, rounds: int = 1, amount: int = 1):
        """Random tournament

        Class to generate a bunch of arbitrary matches. 

        This is not a real 'competition' as it is not intended to determine a winner. 
        But the class works as a competition and thus produces a final standing the same way a RoundRobin does, by summing matches scores.
        It is however 'fair' in the sense that there is no guarantee that participants play the same amount of games.
        Technicaly it is even possible some registered participant do not even play a single match.

        Parameters
        ----------
        name : str
            A unique name to identify the Event.
        seeding : Ranking
            A ranking used for seeding. 
        solver : Solver, optional
            A Solver to generate match outcomes, by default BetterWin()
        cashprize : Optional[Dict[int, float]], optional
            A 'prizepool' rewarding player with 'money' for their success (placement in the final standing) during the Event, by default None
        rounds : int, optional
            Number of rounds to be played, by default 1.
            Participants play at most one match per rounds.
        amount: int, optional
            Number of game to produce by rounds, by default 1.

        .. note::
            Calling with amount=1 and rounds=n makes it a pure random scheduler that generates n matches.
        """
        # TODO: remove the seeding parameters, it makes 0 sense and is just anoying for the user.
        super().__init__(name, seeding, solver, cashprize)
        self.nb_rounds = rounds
        self.nb_duel = amount

    def _init_future_rounds(self):
        # !!! Bugs when self.nb_duel is to high. When should the error be raised, and how/where should it be documented.
        participants = [p for p in self.participants()]
        for _ in range(self.nb_rounds):
            random.shuffle(participants)
            new_round = participants[:self.nb_duel*2]

        self.future_rounds.append(new_round)
