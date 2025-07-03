from rstt.stypes import SPlayer


class PlayerLevel:
    def rate(self, player: SPlayer) -> float:
        return player.level()
