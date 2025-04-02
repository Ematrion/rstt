"""Subpackage for tournaments

RSTT notion of tournament is similar to what `wikipedia <https://en.wikipedia.org/wiki/Tournament>`_ describes:

    - A competition involving at least three competitors
    - One or more competitions held at a single venue and concentrated into a relatively short time interval
    - Tournament winner determined based on the combined results.
    
The abstract class :class:`rstt.scheduler.tournament.competition.Competition` is a general template for tournaments.
    
"""

from .competition import Competition

from .groups import RoundRobin, SwissRound
from .random import RandomRound
from .swissbracket import SwissBracket

from .knockout import SingleEliminationBracket, DoubleEliminationBracket
from .snake import Snake

'''
    TODO: BYE-round
        a way to make the number of partcipant more flexible in practice is to introduce bye-round.
        Certain players who can not face an opponent are given a 'free' win. 
        A simple approach to implement it is to create BYE player(s), always losing, and remove them of the final state of the event.
        To ensure the lose of BYE players, the competition.solver can be wrapped in one that hanle BYE-games and delegate for others.
'''
