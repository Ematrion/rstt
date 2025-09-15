from rstt.player import PlayerTVS


class LoLTeam(PlayerTVS):
    def __init__(self, name: str | None = None, level: float | None = None) -> None:
        super().__init__(name, level)

    def _update_level(self) -> None:
        ...
