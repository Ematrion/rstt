from typing import Union, List, Dict, Tuple, Optional, Any, Iterable
from typing import Protocol, runtime_checkable
from typeguard import typechecked

from rstt import Player, Duel, BetterWin
from rstt.ranking.ranking import Ranking
from rstt.stypes import Solver
from rstt.scheduler.tournament.competition import Competition

from rstt.utils import utils as uu, matching as um, competition as uc


@runtime_checkable
class Shuffler(Protocol):
    @typechecked
    def rearange(status: List[int]) -> List[int]:
        """reorder elements in a 'meaningfull' fashion

        Parameters
        ----------
        status : List[int]
            A list of integers [e0, e1, e2, ...]

        Returns
        -------
        List[int]
            A list of the same integers, in a different order.
            This new ordering should be deterministic and not random. 
        """
        ...


@runtime_checkable
class Seeder(Protocol):
    @typechecked
    def seed(players: List[Player], initial_seeds: Iterable, results: Any, **kwargs) -> List[Player]:
        """reorder players in a 'meaningfull' fashion

        Parameters
        ----------
        players : List[Player]
            A list of Player to order
        initial_seeds : Iterable
            An original ordering of the players
        results : Any
            Any data structure containing games (type ´Game´) related to the involved players

        Returns
        -------
        List[Player]
            A list of the same players, in a different order
        """
        ...


@runtime_checkable
class Generator(Protocol):
    @typechecked
    def generate(status: Union[List[int], List[Player]]) -> Union[List[int], List[Player]]:
        """Generate different ordering version of a given List
        
        
        the different version produced are refered as 'options'
        For short input, this function could just produce all possible orderings.
        For long inout, this function could implement greedy strategy.
        For this reason the input is a list, and the initial ordering could be meaningfull for the strategy
        
        Parameters
        ----------
        status : Union[List[int], List[Player]]
            A list of element to compute options

        Returns
        -------
        Union[List[int], List[Player]]
            the options, A list of different 'option' which are reordering of the given 'status'
            Idealy the first option is a direct, and 'obvious' transformation of status
        """
        ...

@runtime_checkable
class Evaluator(Protocol):
    @typechecked
    def eval(options: List[List[Player]], initial_seeds: Iterable, results: Any, **kwargs) -> List[List[Player]]:
        """reorder options based on criteria

        The options can be evaluated based on an history of Game(s), or Player(s) appreciation.
        Usuallythe eval function calls somehow somwhere a 'sort'

        Parameters
        ----------
        options : List[List[Player]]
            _description_
        initial_seeds : Iterable
            _description_
        results : Any
            _description_

        Returns
        -------
        List[List[Player]]
            _description_
        """
        ...

# Dummy Parameters
class DummyParam(Shuffler, Seeder, Evaluator):
    def rearange(status: List[int]) -> List[int]:
        #print('Dummy Rearange')
        return status

    def seed(players: List[Player], initial_seeds: Iterable, results: Any, **kwargs) -> List[Player]:
        #print('Dummy seed')
        return players

    def generate(status: Union[List[int], List[Player]]) -> Union[List[int], List[Player]]:
        return um.ruban(status)
        #print('Dummy generate')
    
    def eval(options: List[List[Player]], initial_seeds: Iterable, results: Any, **kwargs) -> List[List[Player]]:
        #print('Dummy eval')
        return options

class TreeRound(Competition):
    @typechecked
    def __init__(self, name: str, seeding: Ranking,
                 matchings: Optional[Dict[Tuple[int, int], Shuffler]]=None,
                 seeders: Optional[Dict[Tuple[int, int], Seeder]]=None,
                 generators: Optional[Dict[Tuple[int, int], Generator]]=None,
                 evaluators: Optional[Dict[Tuple[int, int], Evaluator]]=None,
                 def_matching=DummyParam,
                 def_seeder=DummyParam,
                 def_generator=DummyParam,
                 def_evaluator=DummyParam,
                 solver: Solver = BetterWin(),
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
    def initialise(self):
        self.__init_settings()        
        self.__init_params()
        
    def generate_games(self):
        games = [uc.find_valid_draw(draws=self.draws(group=self.rounds[score]),
                                    old_games=self.games(),
                                    ) for score in self.round_scores()]
        return uu.flatten(games)
        
    @typechecked
    def edit(self, games: List[Duel]) -> bool:
        # move winner and loser
        for game in games:
            p1, p2 = game.player1, game.player2
            self.rounds[self.score(p1)].append(p1)
            self.rounds[self.score(p2)].append(p2)
            
        # move to next round
        self.current_round += 1
        
        # check end condition
        if self.current_round == self.max_round:
            self.__standing()
            finished = True
        else:
            finished = False
        return finished
    
    # --- round mechanism --- #
    @typechecked
    def score(self, player: Player) -> Tuple[int, int]:
        wins = len([game for game in self.games() if game.winner() == player])
        loses = len([game for game in self.games() if game.loser() == player])
        return (wins, loses)

    def round_scores(self) -> List[Tuple[int, int]]:
        # 1) [(0, 0)] 2) [(1,0), (0,1)] 3) [(2,0), (1,1), (0,2)] ...
        return [(self.current_round-i, i) for i in range(self.current_round+1)
                if i < self.max_loses and self.current_round-i < self.max_wins]

    @typechecked
    def draws(self, group: List[Player]) -> List[List[Duel]]:
        # args controls - draw can only be made among player with same score
        scores = [self.score(player) for player in group]
        if len(set(scores)) != 1:
            msg = f'''group must consist of players with same score
            \'group\': {group},
            \'scores\': {scores}
            '''
            raise ValueError(msg)
        else:
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
        
        return[uc.playersToGames(option) for option in options]

    def results(self):
        # fit data to expected format for tiebreaker function
        res = {player: {'opponent': [], 'score': [],} for player in self.seeding}
       
        for game in self.games():
            # update opponent list
            res[game.player1]['opponent'].append(game.player2)
            res[game.player2]['opponent'].append(game.player1)
            
            # update score list !!! Lacks generalisation
            res[game.player1]['score'].append('win' if game.winner() == game.player1 else 'lose')
            res[game.player2]['score'].append('win' if game.winner() == game.player2 else 'lose')
        return res
    
    # --- under the hood mechanism --- #    
    def __standing(self):
        top8 = [(self.max_wins, i) for i in range(self.max_loses)]
        bottom8 = [(i, self.max_loses) for i in range(self.max_wins-1, -1, -1)]
        final_scores = top8 + bottom8
        top = 0
        for score in final_scores:
            players = self.rounds[score]
            top += len(players)
            for p in players: 
                self.standing[p] = top
        
    def __possible_scores(self):
        return [(i,j) for j in range(self.max_loses+1) for i in range(self.max_wins+1) if i+j <= self.max_round]

    def __init_settings(self):
        # !!! Hardcoded setting for 16 participants
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