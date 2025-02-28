from typing import  List, Dict, Tuple, Any
from typeguard import typechecked

from rstt.player import Player
from rstt.stypes import SPlayer

import numpy as np
import math
import copy

import warnings


'''
    FIXME:
    - There is no consensus on the return type of the rate() functions
    - It is fine regarding the Protocol, but realy anoying when combine with Observer
'''


# ------------------------ #
# --- Player as Rating --- #
# ------------------------ #    
class PlayerLevel:
    @typechecked
    def rate(self, player: SPlayer, *args, **kwars) -> Dict[Player, float]:
        return {player: player.level()}
    
class PlayerWinPRC:
    def __init__(self, default: float=-1.0, scope: int=np.iinfo(np.int32).max):
        self.default = default
        self.scope = scope
    
    @typechecked
    def rate(self, player: Player, *args, **kwargs):
        return {player: self.win_rate(player)}
    
    def win_rate(self, player: Player):
        games = player.games()
        if games:
            if self.scope:
                games = games[-self.scope:]
            nb_wins = sum([1 for game in games if player is game.winner()])
            total = len(games)
            winrate = nb_wins / total * 100
        else:
            winrate = self.default
        return winrate


# ------------------------ #
# --- Game Score Based --- #
# ------------------------ #
class Elo:
    def __init__(self, k: float = 20.0, lc: float = 400.0):
        self.LC = lc
        self.K = k
        # TODO self.distribution = dist & change expectedScore

    @typechecked
    def rate(self, groups: List[List[float]], scores: List[float], *args, **kwars) -> List[List[float]]:        
        # NOTE: groups: [[winner_elo][loser_elo]], scores [[1.0][0.0]]
        
        # unpack args
        r1, r2 = groups[0][0], groups[1][0]
        s1, s2 = scores
        # cumpute new ratings
        new_r1 = self.update_rating(r1, r2, s1)
        new_r2 = self.update_rating(r2, r1, s2)
        return [[new_r1], [new_r2]]

    def expectedScore(self, rating1, rating2):
        return 1.0 / (1.0 + math.pow(10, (rating2-rating1)/self.LC))
    
    def update_rating(self, rating1: float, rating2:float, score:float):
        expected_result = self.expectedScore(rating1, rating2)
        return rating1 + (self.K * (score-expected_result))


class Glicko:
    def __init__(self, minRD: float = 30.0,
                maxRD: float = 350.0,
                c: float = 63.2,
                q: float = math.log(10, math.e)/400,
                lc: int = 400):
        
        # model constant
        self.__maxRD = maxRD # maximal value of RD
        self.__minRD = minRD # minimal value of RD
        self.lc = lc # constant in function E
        self.C = c # constant used for 'inactivity decay'
        self.Q = q # no idea how to interpret this value
        
    def G(self, rd: float):
        return 1 / math.sqrt( 1 + 3*self.Q*self.Q*(rd*rd)/(math.pi*math.pi))
    
    def expectedScore(self, rating1, rating2, mode='update'):
        RDi = 0 if mode == 'update' else rating1.sigma
        RDj = rating2.sigma
        ri, rj = rating1.mu, rating2.mu
        return 1 / (1 + math.pow(10, -self.G(math.sqrt(RDi*RDi + RDj*RDj)) * (ri-rj)/400))

    def d2(self, rating1, games: List[Tuple[Any, float]]):
        ''' NOTE:
        rating have mu sigma attributes, 
        games are dict of ratings:score,
        '''
        all_EJ = []
        all_GJ = []
        for rating2, score in games:
            # get needed variables
            Ej = self.expectedScore(rating1, rating2, mode='update')
            RDj = rating2.sigma
            Gj = self.G(RDj)
            
            # store vairables
            all_EJ.append(Ej)
            all_GJ.append(Gj)
        
        # big sum
        bigSum = 0
        for Gj, Ej, in zip(all_GJ, all_EJ):
            bigSum += Gj*Gj*Ej*(1-Ej)
        
        '''
        NOTE:
        Try/Expect is not part of the Glicko official algorith  presentation.
        But I have encountered Unexpected ZeroDivisionError
        
        The try/except ZeroDivErr/warn an be easly simplified by:
        return 1 / min( self.Q*self.Q*bigSum, lower_bound)
        
        However I could note find any specfic details about the choice of the boundary.
        Analytically, the term can not be equal to 0.0, it is always >0.
        Nnumercialy, it happens in extreme situation i.e does not arise in standard 'intended' Glicko usage.
        
        The package is for scientifical experimentation,
        It allows extreme case exploration and can not hide arbitrary choices.

        # !!! Do not fix unless it is possible to link a scientifical source justifying the implementation
        '''
        try:
            # d2 formula 
            return 1 / (self.Q*self.Q*bigSum)
        except ZeroDivisionError:
            # !!! BUG: ZeroDivisionError observed with extreme rating differences
            # !!! this will now print variable of interest
            # !!! but code will run assuming maximal and mininal expected value possible between 0 and 1

            # HACK: just assume a very low 'bigSum'
            bigSum = 0.00000000001
            correction = 1 / (self.Q*self.Q*bigSum)
            
            msg = f"Glicko d2 ERROR: {rating1}, {games}\n {bigSum}, {all_EJ}, {all_GJ}\n d2 return value as been adjusted to 1/0.00000000001 "
            warnings.warn(msg, RuntimeWarning)
            return correction

    def prePeriod_RD(self, rating):
        '''
        implement formula presented at step1 caee (b) p.3
        '''
        new_RD = math.sqrt(rating.sigma*rating.sigma + self.C*self.C)
        # check boundaries on sigma - ??? move max() elsewhere
        return max(min(new_RD, self.__maxRD), self.__minRD)
    
    def newRating(self, rating1, games: List[Tuple[Any, float]]):
        ''' NOTE:
        rating have mu sigma attributes, 
        games are dict of ratings:score,
        '''
            
        # compute term 'a'
        d2 = self.d2(rating1, games)
        a = self.Q / ((1/(rating1.sigma*rating1.sigma)) + (1/d2))
        
        # lcompute term 'b'
        b = 0
        for rating2, score in games:
            b += self.G(rating2.sigma)*(score - self.expectedScore(rating1, rating2, mode='update'))
        
        # create new rating object to avoid 'side effect'
        rating = copy.copy(rating1)
        # post Period R
        rating.mu += a*b
        # post Period RD
        rating.sigma = math.sqrt(1/( (1/rating1.sigma**2) + (1/d2) ))
        
        return rating

    def rate(self, rating, ratings: List[Any], scores: List[float]):
        # formating
        games = [(r, s) for r, s in zip(ratings, scores)]
        return self.newRating(rating, games)


