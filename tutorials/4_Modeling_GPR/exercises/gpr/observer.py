from rstt.stypes import Inference, RatingSystem


class GlobalHandler():
    def __init__(self) -> None:
        ...

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs) -> None:
        ...
