from typing import Union, List, Set, Dict, Callable
from typeguard import typechecked
import abc

import random

import numpy as np
import math
#import networkx as nx

from rstt import Player, Duel, BetterWin
from rstt.ranking import Standing
from rstt.ranking.ranking import Ranking
from rstt.stypes import Solver




class Competition(metaclass=abc.ABCMeta):
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),
                 cashprize: Dict[int, float] = {}):
        # a name
        self.name = name
        # 'settings'
        self.participants = []
        self.seeding = seeding
        self.solver = solver
        self.cashprize = cashprize
        # result related variable
        self.played_matches = []
        self.standing = {}
        # control variable
        self.__started__ = False
        self.__finished__ = False
        self.__closed__ = False

    def games(self):
        return self.played_matches

    @typechecked
    def registration(self, players: Union[Player, List[Player], Set[Player]]):
        if not self.__started__:
            playerset = set(self.participants)
            playerset.update(players)
            self.participants = list(playerset)

    def run(self):
        if not self.__started__:
            self.start()
            self.play()
            self.trophies()

    def start(self):
        if not self.__started__:
            self.seeding = self.seeding.fit(self.participants)
            self.initialise()
            self.__started__ = True

    def play(self):
        while not self.__finished__:
            current_round = self.generate_games()
            results = self.play_games(current_round)
            self.__finished__ = self.edit(results)

    @typechecked
    def play_games(self, games: List[Duel]):
        played = []
        for game in games:
            game.play(self.solver)
            played.append(game)
        self.played_matches += played
        return played

    def trophies(self):
        payed = self.cashprize.keys()
        for player in self.participants:
            placement = self.standing[player]
            earnings = self.cashprize[placement] if placement in payed else 0.0
            result = (self.name, placement)
            player.collect(achievement=result, money=earnings)
        self.__closed__ = True

    def initialise(self):
        pass

    @abc.abstractmethod
    def generate_games(self):
        pass

    @abc.abstractmethod
    def edit(self, games: List[Duel]):
        return True
    