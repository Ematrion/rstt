from rstt.stypes import SPlayer, Event
from rstt.ranking import Ranking
from rstt.ranking.datamodel import KeyModel
from rstt.ranking.inferer import EventScoring
from rstt.ranking.observer import PlayerChecker


'''
    TODO: Redesign the ranking concepts
        - ratings as list of achievements
        - KeyModel.ordinal to compute the points (currently EventStanding.rate)
        - backend extracting the relevant achievements of players
        - where goes the  'EventDataSet' component ?
'''


import warnings


class SuccessRanking(Ranking):
    def __init__(self, name: str,
                 window_range: int = 1, tops: int = 1,
                 buffer: int | None = None, nb: int | None = None,
                 players: list[SPlayer] | None = None,
                 default: dict[int, float] | None = None):
        """Merit Based Ranking

        Usefull to implement Ranking system like the one in  `tennis <https://en.wikipedia.org/wiki/ATP_rankings>`_ for example.

        Attributes
        ----------
        datamodel: :class:`rstt.ranking.datamodel.KeyModel` (int as rating)
        backend: :class:`rstt.ranking.inferer.EventScoring`
        handler: :class:`rstt.ranking.observer.PlayerChecker`

        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        buffer : int
            Backend parameter. The number of event to consider for the rating, starting from the last.
        nb : int
            Backend parameter. The actual number of event in the buffer to use for the ratings computation.
        default : Optional[Dict[int, float]], optional
            Backend Parameter. Mapping placement in event to points for the rating, by default None
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """

        if buffer or nb:
            window_range = buffer, tops = nb
            msg = f"buffer and nb will be removed in version 1.0.0, use instead window_range and tops."
            warnings.warn(msg, DeprecationWarning)

        super().__init__(name=name,
                         datamodel=KeyModel(template=int),
                         backend=EventScoring(window_range=window_range,
                                              tops=tops,
                                              default=default),
                         handler=PlayerChecker(),
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
