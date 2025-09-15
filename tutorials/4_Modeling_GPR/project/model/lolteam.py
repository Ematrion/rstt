from rstt.stypes import SPlayer
from rstt.player import Player, PlayerTVS
from project.scene import Role

from statistics import mean


class LoLTeam(PlayerTVS):
    def __init__(self, name: str, players: dict[Role, SPlayer] = {r: Player() for r in Role}) -> None:
        self._players = players.values()
        self._players_by_roles = players

        super().__init__(name, level=mean(
            [player.level() for player in self._players]))

    def level(self, weights: dict[Role, float] | None = None) -> float:
        if weights:
            levels_sum = sum([self._players_by_roles[role].level(
            )*weight for role, weight in weights.items()])
            weights_sum = sum(weights.values())
            return levels_sum/weights_sum
        else:
            return mean([player.level() for player in self._players])

    def player(self, role: Role) -> SPlayer:
        return self._players_by_roles[role]

    # --- override --- #
    def _update_level(self) -> None:
        for player in self._players:
            if isinstance(player, PlayerTVS):
                player._update_level()
