"""Types in RSTT

This modules defines different componnents types for the package. RSTT user level functions and class methods are typehecked.
It helps raising meaningfull errors at runtime, write understandable functions.
The module purpose is also to help develloper to extent and integrate their own component that fit in the RSTT framework.

When a type name clashes with an existing class, the type name is prefixed by a capital `S`.
For example: :class:`rstt.stypes.SPlayer` should only be used for typehint in functions signatures, while :class:`rstt.player.player.Player` is a class representing competitors.
RSTT relies on typeguard 3.0.0 and `Duck-Typing`.
Which means that Protocol are defined by the existence of attributes/methods, and not their type signatures.
"""



from dataclasses import dataclass
from typing import List, Dict, Union,  Any, Iterable, Protocol, runtime_checkable


# TODO: work on Scheduler typing and differences between 'Tournament' & 'MatchMaking'



@runtime_checkable
class SPlayer(Protocol):
    def name(self) -> str:
        ...
    
    def level(self) -> float:
        ...


Score = list[float]


@runtime_checkable
class SMatch(Protocol):
    def players(self) -> List[SPlayer]:
        ...
    
    def scores(self) -> Score:
        ...


@runtime_checkable
class Event(Protocol):
    '''    participants: List[Player]
    standing = Dict[Player, int]'''
    
    def name(self) -> str:
        ...
        
    def games(self, by_rounds) -> List[SMatch]:
        ...
    
    def standing(self) -> Dict[SPlayer, int]:
        ...


@dataclass
class Achievement:
    event_name: str
    place: int
    prize: float
    # ??? categorie/label(s) (world event, domestic league, playoffs etc.)
    # ??? event_type (SEB, Snake, MM etc)
    # ??? teammates

    
@runtime_checkable
class Solver(Protocol):
    def solve(self, match: SMatch, *agrs, **kwargs) -> None:
        ...


# -------------------------- #
# --- Typing for Ranking --- #
# -------------------------- #
@runtime_checkable
class Inference(Protocol):
    # NOTE: name source: https://en.wikipedia.org/wiki/Statistical_inference
    def rate(self, *args, **kwargs) -> Any:
        ...


@runtime_checkable        
class RatingSystem(Protocol):
    def get(self, key: SPlayer) -> Any:
        ...
        
    def set(self, key: SPlayer, rating: Any) -> None:
        ...
        
    def ordinal(self, rating: Any) -> float:
        ...


@runtime_checkable
class Observer(Protocol):
    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs) -> None:
        ...


# ---------------------------- #
# --- Typing for Shceduler --- #
# ---------------------------- #
@runtime_checkable
class Shuffler(Protocol):
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
    def seed(players: List[SPlayer], initial_seeds: Iterable, results: Any, **kwargs) -> List[SPlayer]:
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
    def generate(status: Union[List[int], List[SPlayer]]) -> Union[List[int], List[SPlayer]]:
        """Generate different ordering version of a given List
        
        
        the different version produced are refered as 'options'
        For short input, this function could just produce all possible orderings.
        For long inout, this function could implement greedy strategy.
        Thus the input is a list, and the initial ordering is meaningfull for the strategy
        
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
    def eval(options: List[List[SPlayer]], initial_seeds: Iterable, results: Any, **kwargs) -> List[List[SPlayer]]:
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

