from .scene import AUDIENCE_MAPPING, REGIONAL, INTERNATIONAL
from .utils import LeagueSystem, EventInfos, GameHistory
from .scene import REGIONS, SPLITS, STAGES, FINALS
from .scene import FIRSTSTAND, MSI, WORLDS
from .stagedevent import StagedEventV2

from rstt import Ranking, Competition
from rstt import RoundRobin, SingleEliminationBracket, DoubleEliminationBracket, SwissBracket
from rstt.stypes import Solver


import json
import rstt


class calendar:
    def __init__(self, start: int, end: int, solver: Solver, seeding: Ranking, source: str):
        self.start = start
        self.end = end

        self.future_events = []
        self.past_events = []

        self.solver = solver
        self.seeding = seeding

        self.source = source

    def __iter__(self):
        self.future_events = year_schedule(start=self.start, end=self.end)
        self.past_events = []
        return self

    def __next__(self):
        if self.future_events:
            infos = self.future_events.pop(0)
            event = StagedEventV2(
                name=str(infos), seeding=self.seeding, solver=self.solver,
                tournaments=tournaments_types(infos, self.source), stage_names=STAGES)
            return event
        else:
            raise StopIteration


def year_schedule(start: int, end: int):
    events = []
    for year in range(start, end, 1):
        for split, final in zip(SPLITS, FINALS):
            # A split for every leagues
            for region in REGIONS:
                infos = EventInfos(
                    region=region, split=split, year=year, stage='')
                events.append(infos)
            # Then, international invitational
            infos = EventInfos(region=final, split=split,
                               year=year, stage='')
            events.append(infos)
    return events


def tournaments_types(infos: EventInfos, source: str) -> list[Competition]:
    if AUDIENCE_MAPPING[infos.region] == REGIONAL:
        return [RoundRobin, SingleEliminationBracket, DoubleEliminationBracket]
    elif AUDIENCE_MAPPING[infos.region] == INTERNATIONAL:
        with open(source, 'r') as file:
            qualif_data = json.load(file)
        return [getattr(rstt, qualif_data[infos.region][stage]['tournament'])
                for stage in STAGES]
    else:
        raise ValueError(f'Event \'{infos.region}\' not part of the calendar')


def event_qualification(infos: EventInfos, ecosystem: LeagueSystem, dataset: GameHistory, source: str):
    invitations = []
    qualifications = []

    with open(source, 'r') as file:
        qualif_data = json.load(file)

    # domestic split
    if AUDIENCE_MAPPING[infos.region] == REGIONAL:
        invitations = [ecosystem.teams(region=infos.region),
                       [],
                       []]
        qualifications = [[], list(range(8)), list(range(4))]

    # international finals
    elif AUDIENCE_MAPPING[infos.region] == INTERNATIONAL:
        qualifications = [qualif_data[infos.region][stage]['qualified']
                          for stage in STAGES]
        for stage in STAGES:
            stage_invites = []
            for invitational in qualif_data[infos.region][stage]['invitation']:
                invitational['infos']['year'] = infos.year
                target = EventInfos(**invitational['infos'])
                target = dataset.get_event(name=str(target))
                for place in invitational['top']:
                    stage_invites += target.top(place)
            invitations.append(stage_invites)

    else:
        raise ValueError(f'Event \'{infos.region}\' not part of the calendar')

    return invitations, qualifications
