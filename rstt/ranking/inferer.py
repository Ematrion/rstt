from typing import  List, Dict, Tuple, Any
from typeguard import typechecked

from rstt.player import Player

import math
import copy


class PlayerLevel:
    @typechecked
    def rate(self, player: Player, *args, **kwars) -> Dict[Player, float]:
        return {player: player.level()} # FIXME: standardize rate() output

    
class Elo:
    def __init__(self, k: float = 20.0, lc: float = 400.0):
        self.LC = lc
        self.K = k
        # TODO self.distribution = dist & change expectedScore

    @typechecked
    def rate(self, groups: List[List[float]], scores: List[float]) -> List[List[float]]:        
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
            
        try:
            # d2 formula 
            return 1 / (self.Q*self.Q*bigSum)
        except ZeroDivisionError:
            
            # !!! BUG: ZeroDivisionError observed with extreme rating differences
            # !!! this will now print variable of interest
            # !!! but code will run assuming maximal and mininal expected value possible between 0 and 1
            # TODO: use warning instead of print
            print('----------------------------------------------')
            print(f'Glicko d2 ERROR: {rating1}, {games}')
            print(f'{bigSum}, {all_EJ}, {all_GJ}')
            print('----------------------------------------------')
            # just assume a very low 'bigSum'
            bigSum = 0.00000000001
            return 1 / (self.Q*self.Q*bigSum)

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
        
        # create new rating object to avoid'side effect'
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


