from rstt.new_ranking import Ranking
from rstt.ranking import KeyModel
from rstt.stypes import SPlayer


'''
    TODO: Redesign the ranking concepts
        - ratings as list of achievements
        - KeyModel.ordinal to compute the points (currently EventStanding.rate)
        - backend extracting the relevant achievements of players
        - does it need/should it use an 'EventDataSet' component ?
'''


class SuccessRanking(Ranking):
    def __init__(self, name: str,
                 players: list[SPlayer] | None = None):
        super().__init__(name,
                         datamodel=KeyModel(template=int),
                         backend=None,
                         handler=None,
                         players=players)
