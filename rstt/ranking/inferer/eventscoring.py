from rstt.stypes import SPlayer, Event
from rstt.ranking.datamodel import keydefaultdict
from rstt.utils import utils as uu

from typing import Optional


class EventDataSet():
    def __init__(self, window_range: int = 1):
        self.events = []
        self.window_range = window_range

    def add(self, event: Event):
        if event.name() in [ev.name() for ev in self.events]:
            msg = f"Event {event.name()} already in the dataset"
            raise ValueError(msg)
        else:
            self.events.append(event)

    def window(self, window: Optional[int] = None):
        nb = window if window else self.window_range
        return self.events[-nb:]


class EventScoring():
    def __init__(self, window_range: int = 1, tops: int = 1, default: dict[int, float] = keydefaultdict(lambda x: 1/x * 100.0)) -> None:
        self.dataset = EventDataSet(window_range=window_range)
        self.tops = tops
        self.relevance = {}
        self.default = default

    def add_event(self, event: Event, relevance: Optional[dict[int, float]] = None):
        self.dataset.add(event)
        self.relevance[event.name()] = relevance if relevance else self.default

    def rate(self, player: SPlayer) -> float:
        points = [self.relevance[event.name()][event.standing()[player]]
                  for event in self.dataset.window()]
        if points == []:
            return 0
        else:
            return sum(uu.nmax(points, self.tops))
