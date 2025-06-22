from rstt.utils import observer as uo
from rstt.stypes import Inference, Observer, RatingSystem
from rstt.stypes import SPlayer


class ObsTemplate(Observer):
    def __init__(self):
        self.prior = None
        self.posteriori = None

        self.convertor: callable = None
        self.extractor: callable = None
        self.query: callable = None
        self.output_formater: callable = None
        self.push: callable = None

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs) -> None:
        # observer initialization
        self._handling_start(datamodel)

        # data transformation
        observations = self.convertor(*args, **kwargs)
        data = self.extractor(observations)
        # process each 'rate-trigger'
        for data_point in data:
            # get corresponding priors
            self.query(self.prior, data_point)

            # perofrm rating evaluation
            self.output_formater(
                data_point, uo.call_function_with_args(infer.rate, **data_point))

            # store posteriori
            self.push(data_point, self.posteriori)

        # terminate the process
        self._handling_end(datamodel)

    def _set_prior(self, datamodel: RatingSystem) -> None:
        # !!! bug when player not pre-register in datamodel
        self.prior = {player: datamodel.get(
            player) for player in datamodel.keys()}

    def _set_posteriori(self, datamodel: RatingSystem) -> None:
        self.posteriori = {}

    def _handling_start(self, datamodel: RatingSystem):
        self._set_prior(datamodel)
        self._set_posteriori(datamodel)

    def _handling_end(self, datamodel: RatingSystem):
        for player, post_rating in self.posteriori.items():
            datamodel.set(key=player, rating=post_rating)
        self.prior = None
        self.posteriori = None
