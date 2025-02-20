from typing import Union, List, Set, Dict, Optional
from typeguard import typechecked
import abc

from rstt import Player, Duel, BetterWin
from rstt.stypes import Solver, Achievement
from rstt.ranking.ranking import Ranking
import rstt.utils.utils as uu

from collections import defaultdict



class Competition(metaclass=abc.ABCMeta):
    '''
        NOTE: In the future the competition class could evolve.
            - inherit from a Scheduler class
            - composition over inheritance:
                * PlayerManager
                * GameManager
                * EventManager
    '''
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver=BetterWin(),
                 cashprize: Optional[Dict[int, float]]=None):
        # a name
        self.name = name
        
        # 'settings'
        self.participants = []
        self.seeding = seeding
        self.solver = solver
        self.cashprize = defaultdict(lambda: 0)
        if cashprize:
            self.cashprize.update(cashprize)
        
        # result related variable
        self.played_matches = []
        self.standing = {}
        
        # control variable
        self.__started = False
        self.__finished = False
        self.__closed = False

    # --- getter --- #
    def started(self):
        return self.__started
    
    def live(self):
        return self.__started and not self.__finished
    
    def over(self):
        return self.__closed
    
    @typechecked
    def games(self, by_rounds=False):
        return self.played_matches if by_rounds else uu.flatten(self.played_matches)
    
    @typechecked
    def top(self, place: Optional[int]=None) -> Union[Dict[int, List[Player]], List[Player]]:
        if place:
            return [key for key, value in self.standing.items() if value == place]
        else:
            return {v: [key for key, value in self.standing.items() if value == place] for v in self.standing.values()}

    # --- general mechanism --- #
    @typechecked
    def registration(self, players: Union[Player, List[Player], Set[Player]]):
        if not self.__started:
            playerset = set(self.participants)
            playerset.update(players)
            self.participants = list(playerset)

    def run(self):
        if self.__started:
            msg = f"Can not run an event that has already started. Did you mean to use play() or perhaps did you wrongly call start()?"
            raise RuntimeError(msg)
        else:
            self.start()
            self.play()
            self.trophies()

    def start(self):
        if not self.__started:
            self.seeding = self.seeding.fit(self.participants)
            self._initialise()
            self.__started = True

    def play(self):
        if not self.__started:
            msg = f"Can not play an event that has not yet started. Did you mean to use .run() or perhaps did you forgot to call .start() first?"
            raise RuntimeError(msg)
        while not self.__finished:
            current_round = self.generate_games()
            results = self.play_games(current_round)
            self.__finished = self.edit(results)

    def play_games(self, games: List[Duel]):
        played = []
        for game in games:
            self.solver.solve(game)
            played.append(game)
        return played

    def edit(self, games: List[Duel]):
            self.played_matches.append(games)
            self._update()
            return self._end_of_stage()

    def trophies(self):
        self.standing = self._standing()
        for player in self.participants:
            try: 
                result = Achievement(self.name, self.standing[player], self.cashprize[self.standing[player]])
                player.collect(result)
            except AttributeError:
                continue
        self.__closed= True

    # --- subclass specificity --- #
    def _initialise(self) -> None:
        '''Function called once, after seedings computation but before any game is played.'''
    
    def _update(self) -> None:
        '''This function is called at the end of every 'rounds', after the game have been stored, but before checking the competition end condition.'''
    
    @abc.abstractmethod
    def _end_of_stage(self) -> bool:
        '''Test if the competition should stop.'''
    
    @abc.abstractmethod
    def _standing(self) -> Dict[Player, int]:
        '''Function called once after every game is played. Builds the final standing of the event'''

    @abc.abstractmethod
    def generate_games(self) -> List[Duel]:
        '''Function called every 'round' to generate games. Should return games WITHOUT scores assigned'''
            
    