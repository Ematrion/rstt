from rstt.stypes import SPlayer, SMatch, RatingSystem
from rstt.ranking import Ranking
from rstt.ranking.observer import ObsTemplate
import rstt.utils.observer as rou
# from rstt.ranking.observer.gameObserver import TEAMS, to_list_of_games, push_new_ratings
from rstt.ranking.datamodel import GaussianModel

from typing import Any


class OSGBG(ObsTemplate):
    def __init__(self):
        """Observer for the BasicOS ranking class

        Similar to :class:`rstt.ranking.observer.GameByGame`, but dealing with 'kwargs' ambiguity
        """

        # NOBUG: do not call super().__init__()
        # openskill.model.rate as a 'teams' parameter for the 'rating_groups'
        # HACK: switch args roles at the right moment
        # TODO: make the rate input a tunable user choice (ranks / scores)

        self.convertor = rou.to_list_of_games
        self.push = rou.push_new_ratings

    def extractor(self, matches: list[SMatch]):
        data = []
        for match in matches:
            # !!! future bug: duel_data expect a Duel but is not (yet) typechecked
            data_point = rou.duel_data(match)
            data_point[rou.PLAYERS] = data_point[rou.TEAMS]
            data_point[rou.RANKS] = None
            data.append(data_point)
        return data

    def query(self, prior: RatingSystem, data: dict[str, Any]):
        rou.get_ratings_groups_of_teams_from_datamodel(prior, data)
        data[rou.TEAMS] = data[rou.RATINGS_GROUPS]

    def output_formater(self, data: dict[str, Any], output: list[list[Any]]):
        data[rou.TEAMS] = data[rou.PLAYERS]
        rou.new_ratings_groups_to_ratings_dict(data, output)


class BasicOS(Ranking):
    def __init__(self, name: str, model=None, players: list[SPlayer] | None = None):
        """Simple OpenSkill Integretion

        Ranking to integrate an `openskill <https://openskill.me/en/stable/manual.html>`_ model into the rstt package.


        Attributes
        ----------
        datamodel: :class:`rstt.ranking.datamodel.GaussianModel` (openskill.models.rating as rating type)
        backend: an openskill model instance
        handler: :class:`rstt.ranking.standard.BasicOs.OSGBG`, which behaves as a GameByGame observer


        Parameters
        ----------
        name : str, optional
            A name to identify the ranking, by default ''
        model : openskills.models
            One of openskills.models implementation, by default None
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None


        Example:
        --------
        .. code-block:: python
            :linenos:

            from rstt import Player, BasicOS
            from openskill.models import PlackettLuce

            competitors = Player.create(nb=10)
            pl = BasicOS(name='Plackett-Luce', model= PlackettLuce(), players=competitors)
            pl.plot()
        """
        super().__init__(name=name,
                         datamodel=GaussianModel(
                             factory=lambda x: model.rating(name=x.name())),
                         backend=model,
                         handler=OSGBG(),
                         players=players)

    def quality(self, game: SMatch) -> float:
        # TODO: provide a default implementation at the Ranking class level
        data = self.handler.extractor(game)
        data = self.handler.query(prior=self.datamodel, data=data)
        return self.backend.predict_draw(teams=data[rou.TEAMS])
