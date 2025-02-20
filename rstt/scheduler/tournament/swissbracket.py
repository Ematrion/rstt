from typing import Union, List, Dict, Tuple, Optional, Any, Iterable
from typing import Protocol, runtime_checkable
from typeguard import typechecked

from rstt import Player, Duel, BetterWin
from rstt.ranking.ranking import Ranking
from rstt.stypes import Solver, Shuffler, Seeder, Generator, Evaluator
from rstt.scheduler.tournament.competition import Competition

from rstt.utils import utils as uu, matching as um, competition as uc

import warnings
warnings.filterwarnings("error")


class DummyParam(Shuffler, Seeder, Evaluator):
    def rearange(status: List[int]) -> List[int]:
        return status

    def seed(players: List[Player], *args,  **kwargs) -> List[Player]:
        return players

    def generate(status: Union[List[int], List[Player]]) -> Union[List[int], List[Player]]:
        return um.ruban(status)
    
    def eval(options: List[List[Player]], *args,  **kwargs) -> List[List[Player]]:
        return options

class SwissBracket(Competition):
    @typechecked
    def __init__(self, name: str, seeding: Ranking, solver: Solver = BetterWin(),
                 matchings: Optional[Dict[Tuple[int, int], Shuffler]]=None,
                 seeders: Optional[Dict[Tuple[int, int], Seeder]]=None,
                 generators: Optional[Dict[Tuple[int, int], Generator]]=None,
                 evaluators: Optional[Dict[Tuple[int, int], Evaluator]]=None,
                 def_matching=DummyParam,
                 def_seeder=DummyParam,
                 def_generator=DummyParam,
                 def_evaluator=DummyParam,
                 cashprize: Dict[int, float] = {}):
        super().__init__(name, seeding, solver, cashprize)

        # general settings of the system
        self.current_round = 0
        self.max_round = None
        self.max_wins = None
        self.max_loses = None
    
        # round parameters - map score with data: (int, int) -> data
        self.rounds = {} # List[Player]
        self.matchings = matchings if matchings else {} # Callable
        self.seeders = seeders if seeders else {} # Callable
        self.generators = generators if generators else {} # Callable
        self.evaluators = evaluators if evaluators else {} # Callable
        
        self.def_matching = def_matching
        self.def_seeder = def_seeder
        self.def_generator = def_generator
        self.def_evaluator = def_evaluator
                
    # --- Override ---#
    def _initialise(self):
        # !!! Currently hardcoded setting for 16 participants
        msg = f"Currently SwissBracket is implemented only for 16 players, received {len(self.participants)}"
        assert len(self.participants) == 16, msg
        
        self.__init_settings()        
        self.__init_params()
        
    def _update(self) -> None:
        # ??? clear self.rounds or keep history 
        # move winner and loser
        for game in self.played_matches[-1]:
            p1, p2 = game.player1(), game.player2()
            self.rounds[self.score(p1)].append(p1)
            self.rounds[self.score(p2)].append(p2)
            
        # move to next round
        self.current_round += 1

    def _end_of_stage(self) -> bool:
        return self.current_round == self.max_round
    
    def _standing(self) -> Dict[Player, int]:
        standing = {}
        top8 = [(self.max_wins, i) for i in range(self.max_loses)]
        bottom8 = [(i, self.max_loses) for i in range(self.max_wins-1, -1, -1)]
        final_scores = top8 + bottom8
        top = 0
        for score in final_scores:
            players = self.rounds[score]
            top += len(players)
            for p in players: 
                standing[p] = top
        return standing

    def generate_games(self):
        # TODO: better warning msg than uc.find_valid_draw
        games = [uc.find_valid_draw(draws=self.draws(group=self.rounds[score]),
                                    games=self.games()) 
                                    for score in self.round_scores()]
        return uu.flatten(games)
    
    # --- round mechanism --- #
    @typechecked
    def score(self, player: Player) -> Tuple[int, int]:
        wins = len([game for game in self.games() if game.winner() == player])
        loses = len([game for game in self.games() if game.loser() == player])
        return (wins, loses)

    def round_scores(self) -> List[Tuple[int, int]]:
        # Round1 [(0, 0)]; Round2 [(1,0), (0,1)]; Round3 [(2,0), (1,1), (0,2)] ...
        return [(self.current_round-i, i) for i in range(self.current_round+1)
                if i < self.max_loses and self.current_round-i < self.max_wins]

    @typechecked
    def draws(self, group: List[Player]) -> List[List[Duel]]:
        scores = [self.score(player) for player in group]
        assert len(set(scores)) == 1 # !!! debugging - SwissBracket will change to support different amount of players
        score = scores[0]        
        
        # sellect correct round parameters
        matching = self.matchings[score].rearange
        seeder = self.seeders[score].seed
        generator = self.generators[score].generate
        evaluator = self.evaluators[score].eval

        # how do seeds face each other by default
        paired_list = matching(list(range(len(group))))
        
        # who has which seeds - replace 'int' by 'Player'
        paired_player = seeder(players=[group[i] for i in paired_list],
                               initial_seeds=self.seeding,
                               results=self.results())
        
        # what are all the options we want to check
        options = generator(paired_player)
       
        # in which order should we consider them
        options = evaluator(options,
                            initial_seeds=self.seeding,
                            results=self.results())
        
        return[uc.playersToDuel(option) for option in options]

    def results(self):
        # fit data to expected format for tiebreaker function
        res = {player: {'opponent': [], 'score': [],} for player in self.seeding}
       
        for game in self.games():
            # update opponent list
            res[game.player1()]['opponent'].append(game.player2())
            res[game.player2()]['opponent'].append(game.player1())
            
            # update score list !!! Lacks generalisation
            res[game.player1()]['score'].append('win' if game.winner() == game.player1() else 'lose')
            res[game.player2()]['score'].append('win' if game.winner() == game.player2() else 'lose')
        return res
    
    # --- under the hood mechanism --- #    
    def __possible_scores(self):
        return [(i,j) for j in range(self.max_loses+1) for i in range(self.max_wins+1) if i+j <= self.max_round]

    def __init_settings(self):
        self.max_round = 5
        self.max_wins = 3
        self.max_loses = 3
        
    def __init_params(self):
        scores = self.__possible_scores()
        
        self.rounds[(0, 0)] = [player for player in self.seeding]
        self.rounds = {score: self.rounds[score] if score in self.rounds.keys()
                       else [] for score in scores}
        
        self.matchings = {score: self.matchings[score] if score in self.matchings.keys()
                                  else self.def_matching for score in scores}
        
        self.seeders = {score: self.seeders[score] if score in self.seeders.keys()
                                  else self.def_seeder for score in scores}
        
        self.generators = {score: self.generators[score] if score in self.generators.keys()
                                  else self.def_generator for score in scores}
        
        self.evaluators = {score: self.evaluators[score] if score in self.evaluators.keys()
                                  else self.def_evaluator for score in scores}