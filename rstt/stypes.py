from typing import Any, Protocol, runtime_checkable

from rstt import Player, Match


# TODO: define 'Event', 'Tournament', 'MatchMaking'


@runtime_checkable
class Solver(Protocol):
    def solve(match: Match, *agrs, **kwargs) -> None:
        ...


@runtime_checkable
class Inference(Protocol):
    # NOTE: name source: https://en.wikipedia.org/wiki/Statistical_inference
    def rate(self, *args, **kwargs) -> Any:
        ...


@runtime_checkable        
class DataModel(Protocol):
    def get(key: Player) -> Any:
        ...
        
    def set(key: Player, value: Any) -> None:
        ...
        
    def ordinal(rating: Any) -> float:
        ...


@runtime_checkable
class Observer(Protocol):
    def handle_observations(self, infer: Inference, datamodel: DataModel, *args, **kwargs) -> None:
        ...
