from rstt import Ranking
from rstt.ranking import KeyModel
from rstt.stypes import SPlayer, Event, Achievement

from typing import Optional
from rstt.new_ranking.standard.consensus import KeyChecker


'''
    TODO: Redesign the ranking concepts
        - ratings as list of achievements
        - KeyModel.ordinal to compute the points (currently EventStanding.rate)
        - backend extracting the relevant achievements of players
        - does it need/should it use an 'EventDataSet' component ?
'''


class EventSocring():
    def __init__(self, window_range: int = 1, tops: int = 1) -> None:
        self.dataset = EventDataSet(window_range=window_range)
        self.tops = tops
        self.relevance: dict[str, dict[int, float]]

    def rate(self, player: SPlayer) -> list[Achievement]:
        # TODO: implement  Competition.achievement(player: SPlayer)
        # + Update stypes.Event protocol
        return [event.achievement(player) for event in self.dataset.window()
                if player in event.participants()]


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


class EventSummary(Ranking):
    def __init__(self, name: str,
                 window_range: int = 1, tops: int = 1,
                 players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=KeyModel(template=int),
                         backend=EventSocring(
                             window_range=window_range, tops=tops),
                         handler=KeyChecker(),
                         players=players)

        self.events = EventDataSet(window_range=window_range)
