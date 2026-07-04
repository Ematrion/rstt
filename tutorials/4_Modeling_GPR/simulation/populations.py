from rstt import Player
from project import LeagueSystem
from project.scene import Region


from collections import defaultdict
import json

import random
import numpy as np
import scipy.stats as stats

region_mapping = {}
region_mapping['NorthAmerica'] = Region.LTAN
region_mapping['Europe'] = Region.LEC
region_mapping['Korea'] = Region.LCK
region_mapping['China'] = Region.LPL
region_mapping['Brazil'] = Region.LTAS
region_mapping['LatinAmerica'] = Region.LTAS
region_mapping['AsiaPacific'] = Region.LCP
region_mapping['Vietnam'] = Region.LCP
region_mapping['Japan'] = Region.LCP


def from_gpr_level() -> LeagueSystem:
    # read data
    with open('data/teams.json', 'r') as file:
        data = json.load(file)

    # create player instance for each teams
    teams = defaultdict(lambda: [])
    for team in data['teams']:
        if team['level'] == None:
            continue
        teams[region_mapping[team['region']]].append(Player(name=team['name'], level=team['level']))
    return LeagueSystem(teams)


def datadriven(dist: str) -> LeagueSystem:
    regional_teams = from_gpr_level()
    return LeagueSystem({region: FACTORIES[dist](levels=[team.level() for team in regional_teams.teams(region)]) for region in Region})
    


def _gaussian_fit(levels: list[float]) -> list[Player]:
    return Player.create(nb=len(levels),
                         level_dist = random.gauss,
                         level_params={'mu': np.mean(levels), 'sigma': np.std(levels)})
    
def _weibull_fit(levels: list[float]) -> list[Player]:
    return Player.create(nb=len(levels), 
                          level_dist=stats.weibull_min,
                          level_params=stats.fit(dist=stats.weibull_min, data=levels, bounds={"c": (1, 50)}).params._asdict() | {'size': 1})
    
FACTORIES = {
    "gaussian": _gaussian_fit,
    "weibull":  _weibull_fit,
}