from typing import Any, Callable

from dataclasses import dataclass
from collections import defaultdict

import copy

from rstt.player import Player
    
    
class keydefaultdict(dict[Player, Any]):
    ''' a defaultdict accpeting lambda x: func(x)
    source:
    Minor modification from the answer of Paulo Costa in: 
    https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
    '''
    def __init__(self, default_factory: Callable[[Player], Any]):
        super().__init__()
        self.default_factory = default_factory

    def __missing__(self, key: Player) -> Any:
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class KeyModel:
    def __init__(self, default=None, template=None, factory=None, *args, **kwargs):
        self.ratings = self.__init_ratings(default, template, factory, *args, **kwargs)
        self.__rtype = self.__get_rating_type()
        self.__default = self.__get_default_rating()

    # --- setter --- #
    def set(self, key, rating):
        # TODO: test rating type before assignement and thorw TypeError
        self.ratings[key] = rating

    # --- getter --- #
    def get(self, key):
        # QUEST: __getitem__ ?
        return self.ratings[key]

    def items(self):
        # ??? ambiguous behaviour items() sugest a collection of (key, rating)
        return self.ratings
    
    def keys(self):
        return self.ratings.keys()

    # --- general purpose methords --- #
    def rtype(self):
        return self.__rtype
        
    def default(self):
        return self.__default

    def ordinal(self, rating) -> float:
        # REQ: Should not support arg type Player. This is the job of a Ranking/Standing 
        # NOTE: name source: https://fr.wikipedia.org/wiki/Nombre_ordinal
        '''convert a rating object into a floating value'''
        return float(rating)

    def tiebreaker(self, rating):
        try:
            return list(rating)
        except:
            return 0

    # --- internal mechanism --- #     
    def __init_ratings(self, default, template, factory, *args, **kwargs):
        ''' rating initialization
        
        return: defaultdict {key: rating}
            where key are the one contained in the standing
            and rating are object used to compute the associated value. 
        
        REQ:
            - each key as its own rating
            - user can provide a rating object (a) or a type to use as model (b).
            - these to option are imcompatible and an error need to be raised
            - match the default value with the self.__rate_model(rating) method
            (a) We use deepcopy to create a new rating instance with equal value.
            (b) We use a Constructor with params to generate a new rating object.
        
        TODO:
            - check functool.partial
        '''
        ratings = {}
        if default and not template and not factory:
            ratings = self.__default_ratings(value=default)
        elif template and not default and not factory:
            ratings = self.__template_ratings(template, *args, **kwargs)
        elif factory and not default and not template:
            ratings = self.__factory_ratings(factory, *args, **kwargs)
        else:
            # TODO: write incompatible params error msg
            msg = f""
            raise ValueError(msg)
        return ratings
    
    def __default_ratings(self, value):
        return defaultdict(lambda: copy.deepcopy(value))
    
    def __template_ratings(self, template, *args, **kwargs):
        return defaultdict(lambda: template(*args, **kwargs))
    
    def __factory_ratings(self, func: Callable, *args, **kwargs):
        return keydefaultdict(default_factory=func)

    def __get_rating_type(self):
        dummy = Player('dummy', 0.0)
        rtype = type(self.ratings[dummy])
        del self.ratings[dummy]
        return rtype

    def __get_default_rating(self):
        dummy = Player('dummy', 0.0)
        self.ratings[dummy]
        return self.ratings.pop(dummy)
    
    # --- magic methods --- #
    def __delitem__(self, key: Player):
        del self.ratings[key]
    
    # ??? __setitem__
    # ??? __getitem__
    # ??? __contain__
        

class GaussianModel(KeyModel):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        
    def ordinal(self, rating):
        return rating.mu - 2*rating.sigma
        
    def tiebreaker(self, rating):
        return [rating.mu, rating.sigma]

