from rstt.ranking import KeyModel
from rstt.stypes import SPlayer, RatingSystem

from .utils import LeagueSystem, Modes


class RegionalRatings(KeyModel):
    def __init__(self,
                 ecosystem: LeagueSystem,
                 ratings: dict[Modes, RatingSystem] = {
                     Modes.League: KeyModel(default=1500),
                     Modes.Team: KeyModel(default=1500)
                 },
                 x: float = 0.8, y: float = 0.2) -> None:
        super().__init__(factory=lambda x: x)

        # ratings storage
        self.ecosystem = ecosystem
        self.ratings = ratings

        # power score parameters
        self.x = x
        self.y = y

    def keys(self):
        return self.ratings[Modes.Team].keys()

    def ordinal(self, rating: SPlayer) -> float:
        # team
        team = rating
        # team rating
        team_elo = self.ratings[Modes.Team].get(team)
        # team region
        region = self.ecosystem.region_of(team)
        # league of the region (SPlayer)
        league = self.ecosystem.league_of(region)
        # rating of league
        league_elo = self.ratings[Modes.League].get(league)
        # Power Score Formula
        return (self.x * team_elo) + (self.y * league_elo)
