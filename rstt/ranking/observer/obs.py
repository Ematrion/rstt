from rstt.stypes import Inference, Observer, RatingSystem
from ..datamodel import KeyModel
from . import utils as uo


class ObsTemplate(Observer):
    def __init__(self):
        self.prior: RatingSystem = None
        self.posteriori: RatingSystem = None

    # --- Observer 'Parameters' --- #
    def convertor(self, *args, **kwargs) -> any:
        raise NotImplementedError

    def extractor(self, observations: any) -> list[any]:
        raise NotImplementedError

    def query(self, prior: RatingSystem, data: any):
        raise NotImplementedError

    def output_formater(self, data: any, output: any):
        raise NotImplementedError

    def push(self, data: any, posteriori: RatingSystem):
        raise NotImplementedError

    # --- Observer Main Function --- #
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

    # --- internal mechanism --- #
    def _set_prior(self, datamodel: RatingSystem) -> None:
        self.prior = datamodel

    def _set_posteriori(self, datamodel: RatingSystem) -> None:
        self.posteriori = KeyModel(default=0)

    def _handling_start(self, datamodel: RatingSystem):
        self._set_prior(datamodel)
        self._set_posteriori(datamodel)

    def _handling_end(self, datamodel: RatingSystem):
        for player, post_rating in self.posteriori.items():
            datamodel.set(key=player, rating=post_rating)
        self.prior = None
        self.posteriori = None


class NoHandling(ObsTemplate):
    def __init__(self):
        """
        :exclude-members:
        """
        super().__init__()
        self.extractor = uo.no_extraction
        self.convertor = uo.no_convertion
        self.query = uo.no_query
        self.output_formater = uo.no_formating
        self.push = uo.no_push
