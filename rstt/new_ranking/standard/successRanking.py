from rstt import Ranking
from rstt.ranking import KeyModel
from rstt.ranking.datamodel import keydefaultdict
from rstt.stypes import SPlayer, Event, Achievement
import rstt.utils.utils as uu

from typing import Optional
from rstt.new_ranking.standard.consensus import KeyChecker


'''
    TODO: Redesign the ranking concepts
        - ratings as list of achievements
        - KeyModel.ordinal to compute the points (currently EventStanding.rate)
        - backend extracting the relevant achievements of players
        - where goes the  'EventDataSet' component ?
'''


import warnings


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


class SuccessRanking(Ranking):
    def __init__(self, name: str,
                 window_range: int = 1, tops: int = 1,
                 buffer: int | None = None, nb: int | None = None,
                 players: list[SPlayer] | None = None,
                 default: dict[int, float] | None = None):

        if buffer or nb:
            window_range = buffer, tops = nb
            msg = f"buffer and nb will be removed in version 1.0.0, use instead window_range and tops."
            warnings.warn(msg, DeprecationWarning)

        super().__init__(name=name,
                         datamodel=KeyModel(template=int),
                         backend=EventScoring(window_range=window_range,
                                              tops=tops,
                                              default=default),
                         handler=KeyChecker(),
                         players=players)

    def forward(self, event: Event | None = None, events: list[Event] | None = None):
        new_events = []
        if event:
            new_events.append(event)
        if events:
            new_events += events

        for new_event in new_events:
            self.backend.add_event(new_event)

        self.handler.handle_observations(infer=self.backend,
                                         datamodel=self.datamodel,
                                         players=self.players())
