from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from rstt import Player, Match


# TODO: define 'Event', 'Tournament', 'MatchMaking'




@dataclass
class Achievement:
    event_name: str
    place: int
    prize: float
    # ??? categorie (world event, domestic league, playoffs etc.)
    # ??? event type (SEB, Snake, MM etc)
    # ??? teamates
    
    
@runtime_checkable
class Solver(Protocol):
    def solve(self, match: Match, *agrs, **kwargs) -> None:
        ...


@runtime_checkable
class Inference(Protocol):
    # NOTE: name source: https://en.wikipedia.org/wiki/Statistical_inference
    def rate(self, *args, **kwargs) -> Any:
        ...


@runtime_checkable        
class RatingSystem(Protocol):
    def get(self, key: Player) -> Any:
        ...
        
    def set(self, key: Player, rating: Any) -> None:
        ...
        
    def ordinal(self, rating: Any) -> float:
        ...


@runtime_checkable
class Observer(Protocol):
    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs) -> None:
        ...
