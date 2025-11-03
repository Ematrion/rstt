from rstt import LogSolver, BTRanking
from rstt.player import BasicPlayer, GaussianPlayer, PlayerTVS
from rstt.stypes import SPlayer, Solver

from project import scene
from project import model
from project.gpr import utils

from dataclasses import dataclass


@dataclass
class SimModel:
    ecosystem: utils.LeagueSystem
    meta: model.MetaData
    solver: Solver
    groundtruth: BTRanking


def baseModel(region: int, nb: int):
    regions = {reg: BasicPlayer.create(nb)
               for reg in [r for r in scene.Region][:region]}
    return SimModel(
        ecosystem=utils.LeagueSystem(regions),
        meta=None,
        solver=LogSolver(),
        groundtruth=BTRanking('basicRegional',
                              players=[p for reg in regions.values() for p in reg])
    )


def regionalSkills(region: int, nb: int, mus: list[float], sigmas: list[float]):
    regions = {reg: BasicPlayer.create(nb, level_params={'mu': m, 'sigma': s})
               for reg, m, s in zip([r for r in scene.Region][:region], mus, sigmas)}
    return SimModel(
        ecosystem=utils.LeagueSystem(regions),
        meta=None,
        solver=LogSolver(),
        groundtruth=BTRanking('regionalSkills',
                              players=[p for reg in regions.values() for p in reg])
    )


def basicMeta(nb):
    regions = {reg: model.LoLTeam.create(nb) for reg in scene.Region}
    return SimModel(
        ecosystem=utils.LeagueSystem(regions),
        meta=model.MetaData(),
        solver=LogSolver(),
        groundtruth=BTRanking('basicMeta',
                              players=[p for reg in regions.values() for p in reg])
    )
