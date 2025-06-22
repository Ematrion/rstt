from rstt.new_ranking import Ranking, GameByGame
from rstt.new_ranking.observer.utils import *
from rstt.ranking import GaussianModel
from rstt.stypes import SPlayer, SMatch


class BasicOS(Ranking):
    def __init__(self, name: str, model=None, players: list[SPlayer] | None = None):
        super().__init__(name=name,
                         datamodel=GaussianModel(
                             factory=lambda x: model.rating(name=name.x)),
                         backend=model,
                         handler=GameByGame,
                         players=players)

    def quality(self, game: SMatch) -> float:
        # TODO: provide a default implementation in the Ranking or Observer class
        data = self.handler.extractor(game)
        data = self.handler.query(prior=self.self.datamodel, data=data)
        return self.backend.predict_draw(teams=data[TEAMS])
