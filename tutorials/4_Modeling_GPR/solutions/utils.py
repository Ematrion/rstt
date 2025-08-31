
from rstt import Player
from rstt.stypes import SPlayer, Event, Inference, RatingSystem

from .scene import (EVENT_NAMING,
                    STAGED_EVENT_NAMING,
                    IMPORTANCE,
                    AUDIENCE_MAPPING,
                    MODES)

from dataclasses import dataclass
import parse


@dataclass
class EventInfos:
    region: str
    split: str
    year: int
    stage: str

    def __str__(self):
        return EVENT_NAMING.format(region=self.region, split=self.split, year=self.year, stage=self.stage)


class GameHistory:
    def __init__(self, mode_range: dict[str: int]):
        self.events: list[Event] = []
        self.ranges: mode_range = mode_range

    def window(self, mode: str) -> list[Event]:
        return self.events[-self.ranges[mode]:]

    def add(self, event: Event):
        self.events.append(event)

    def get_event(self, name: str):
        for event in self.events:
            if event.name() == name:
                return event


class LeagueSystem:
    def __init__(self, region_teams: dict[str: list[SPlayer]]):
        self._leagues: dict[str: SPlayer] = {}
        self._teams: dict[SPlayer: str] = {}

        # initialize both dict
        for region, teams in region_teams.items():
            self._leagues[region] = Player(name=region, level=-1)
            for team in teams:
                self._teams[team] = region

    def teams(self, region: str = None):
        all_teams = list(self._teams.keys())
        if region:
            all_teams = [
                team for team in all_teams if self.region_of(team) == region]
        return all_teams

    def leagues(self):
        return list(self._leagues.values())

    def regions(self):
        if set(self._leagues.keys()) == set(self._teams.values()):
            return list(self._leagues.keys())
        else:
            raise RuntimeError('Regions of leagues and teams do not match')

    def region_of(self, team: SPlayer):
        return self._teams[team]

    def league_of(self, region: str):
        return self._leagues[region]


def get_event_infos(event: Event) -> EventInfos:
    try:
        return EventInfos(**parse.parse(EVENT_NAMING, event.name()).named)
    except AttributeError:
        return EventInfos(**parse.parse(STAGED_EVENT_NAMING, event.name()).named, stage='Staged')


def set_event_importance(backend: Inference, infos: EventInfos):
    '''assuming an 'rstt.ranking.Elo' backend '''
    # get audience
    audience = AUDIENCE_MAPPING[infos.region]
    # get stage
    stage = infos.stage
    # select proper Impact factore
    impact = IMPORTANCE[audience][stage]
    # adjust importance
    backend.K = impact


def reset_ratings(datamodel: RatingSystem):
    '''assuming a RegionalRating datamodel'''
    for mode in MODES:
        keys = list(datamodel.ratings[mode].keys())
        for key in keys:
            # remove ratings
            del datamodel.ratings[mode][key]
