from typeguard import typechecked
from typing import Any, Union, List, Callable, Optional

from rstt import BasicPlayer
from rstt.ranking import Standing
from rstt.stypes import Inference, RatingSystem, Observer



def set_equi(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper_set(self, *args: Any, **kwargs: Any) -> Any:
        set_action = func(self, *args, **kwargs)
        if self._Ranking__maintain_equivalence:
            self._Ranking__ContainerEquivalence()
        return set_action
    return wrapper_set

def get_equi(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper_get(self, *args: Any, **kwars: Any) -> Any:
        if self._Ranking__maintain_equivalence:
            self._Ranking__ContainerEquivalence()
        return func(self, *args, **kwars)
    return wrapper_get
    
def get_disamb(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper_get(self, *args: Any, **kwars: Any) -> Any:
        if self._Ranking__maintain_disambiguity:
            self._Ranking__RankDisambiguity()
        return func(self, *args, **kwars)
    return wrapper_get
    
def set_disamb(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper_set(self, *args: Any, **kwargs: Any) -> Any:
        set_action = func(self, *args, **kwargs)
        if self._Ranking__maintain_disambiguity:
            self._Ranking__RankDisambiguity()
        return set_action
    return wrapper_set


class Ranking():
    '''   
    NOTE:
        - The Ranking class has two dict[Player, ...], (RatingSystem, Standing) - which induce redundancy and ambiguity.
        The 'Container Equivalence' and 'Rank Disambiguity' (SEE GLOSSARY) are two properties that needs to be enforced
        to guarantee a well defined behaviour for the Ranking class. Hopefully it is also sufficient.
        - The RatingSystem act like a defaultdict. Get operations can induce set operations.
        This is tricky as a player could be inserted in the ranking using 'read' methods of the interface.
        
    GLOSSARY:
        - Container Equivalence (Union == Intersection):
        (key in self.datamodel.ratings) <=> (key in self.standing).
        In the code we refer to 'equivalence'
        - Rank Disambiguity (point '=' rating):
        self.datamodel.ordinal(key) == self.standing.value(key) for all keys.
        In the code we refer to 'disambiguity'

    # !!!
        - self.__disambiguity == True && self._Standing__sorted == False
        This means that the players have the correct points but are not correctly ranked.
        It can happen when 'self.standing._keep_sorted_ == False' which is triggered by the user outside of the Ranking methods.
    
    # ??? 
        - Can this state be reached from the intended Ranking usage ?
        How to detect it and what to do ?
    '''
    @typechecked
    def __init__(self, name: str, 
                 datamodel: RatingSystem, 
                 backend: Inference,
                 handler: Observer,
                 players: Optional[List[BasicPlayer]] = None):
        
        # name/identifier - usefull for plot
        self.name = name
        
        # fundamental notion of the Ranking Class
        self.standing = Standing()
        self.backend = backend
        self.datamodel = datamodel
        self.handler = handler

        # state control variable
        self.__equivalence = True
        self.__disambiguity = True

        # protocol control variable
        self.__maintain_equivalence = True
        self.__maintain_disambiguity = True
        
        if players:
            self.add(keys=players)
        
    # --- Containers standard methods --- #
    @set_disamb
    @set_equi
    @typechecked
    def add(self, keys: List[BasicPlayer]):
        # turn maintainance for optimization
        should_maintain = self.__maintain_equivalence
        self.__maintain_equivalence = False
        
        # perform iteratively addition
        for key in keys:
            self.__add(key)
        
        # restaure Ranking status
        self.__maintain_equivalence = should_maintain
             
    def __add(self, key: BasicPlayer):
        if key in self:
            msg = f'Can not add a key already present in the Ranking, {key}'
            raise ValueError(msg)
        # default dict get operator for missing key
        self.datamodel.get(key)
        
        # self.datamodel do not match self.standing
        self.__equivalence = False
    
    # --- magic methods --- #
    def __getitem__(self, *args, **kwargs) -> Union[BasicPlayer, List[BasicPlayer], int, List[int]]:
        ''' get item based on a rank or a key
        
        NOBUG:
            - sorting is handled by the Standing itself
            - so is typechecked
        '''
        return self.standing.__getitem__(*args, **kwargs)
    
    def __delitem__(self, key: BasicPlayer):
        ''' delete element from the Ranking
        
        REQ:
            - element needs to be remove both from the standing and the RatingSystem
            
        NOBUG:
            - del standing[key] is typechecked. CALL MUST BE BEFORE RatingSystem
        
        # ???:
            - could del succeed on standing but fail on RatingSystem.
            This would otentialy lead to an invalid ranking state because __delitem__ is not decorated.
            A ranking invalid state can exactly be the reason why this scenario happens.
            What is the best approach to this situation ?
        '''
        del self.standing[key]
        del self.datamodel[key]
            
    def __contains__(self, key: BasicPlayer):
        '''
        NOTE:
            - it does match standing behavior as specified but
            depending on the choices, 'p in self' can be slower than
            'p in self.standing' / 'p in self.datamodel'
        '''
        return key in self.standing
    
    def __len__(self):
        return len(self.standing)
    
    def __iter__(self):
        return self.standing.__iter__()
                
    # --- getter --- #
    def rank(self, player: BasicPlayer) -> int:
        return self[player]
        
    def ranks(self, players: List[BasicPlayer]) -> List[int]:
        return [self.rank(player) for player in players]
        
    def rating(self, player: BasicPlayer) -> Any:
        """Get method for rating

        Rating object is the internal model associated to a key.
        Ratings are used to automaticly compute values for the sorting feature of a Standing.

        Parameters
        ----------
        player : Player
            A key in the Ranking

        Returns
        -------
        _type_
            The associated model to the provided key. The type is defined by Ranking.RatingSystem.rtype
            
        Raises
        ------
        KeyError
        """
        if player in self: # NOBUG RatingSystem is a defaultdict
            return self.datamodel.get(player)
        else:
            msg = f"{player} is not present in {self.standing}"
            raise KeyError

    def ratings(self) -> List[Any]:
        """Get method for all ratings

        Returns
        -------
        list[_type_]
            A list of all rating object present in the Ranking, in order of the Standing.
        """
        return [self.rating(player) for player in self]
    
    def players(self) -> List[BasicPlayer]:
        """Get method of all keys

        Alias for Ranking.standing.keys()

        Returns
        -------
        List[Player]
            A list of all player in descending order of their associated values.
        """
        return self.standing.keys()

    def point(self, player: BasicPlayer) -> float:
        """Get the point associated to a key

        Alias for Ranking.standing.value(player)

        Returns
        -------
        float
            the associated value.
        """
        return self.standing.value(player)

    def points(self) -> List[float]:
        """Get method of all values

        Alias for Ranking.standing.values()

        Returns
        -------
        List[float]
            A list of all associated values in descending order.
        """
        return self.standing.values()

    def status(self):
        return  {'equivalence': self.__equivalence,
        'disambiguity': self.__disambiguity,
        'maintain_equivalence': self.__maintain_equivalence,
        'm_disambanbiguity': self.__maintain_disambiguity}
        
    # ??? items() -> List[(rank, player, ratings)]
    # ??? item(key) -> (rank, player, ratings)
    # --- setter --- #
    @set_disamb
    @set_equi
    def set_rating(self, key: BasicPlayer, rating: Any):
        """A method to assign a rating to a Player

        
        The Ranking delegate this task to a 'RatingSystem' instance stored as attribute 'rankink.datamodel'.
        The RatingSystem define what rating type is accepted and wether a set operation is authorized for the provided key.
        
        Parameters
        ----------
        key : Player
            A Player
        rating : Any
            A rating object associated to the key
        """
        self.datamodel.set(key, rating)
        self.__equivalence = False
        
    # ??? remove()
    # ??? pop()
            
    # --- general purpose methods --- #
    @get_disamb
    @get_equi   
    def plot(self):
        self.standing.plot(standing_name=self.name)
    
    @set_disamb
    @set_equi
    def update(self, *args, **kwargs):
        """Update the Ranking


        Parameters
        ----------
        observations : _type_
            _description_
        """
        
        self.forward(*args, **kwargs)
      
        # NOTE: How do we know if the ranking state changed ?
        # HACK: always assume it did
        self.__disambiguity = False
        self.__equivalence = False
    
    def forward(self, *args, **kwargs):
        '''
        '''
        self.handler.handle_observations(infer=self.backend,
                            datamodel=self.datamodel,
                            *args, **kwargs)

    @get_disamb
    @get_equi
    def rerank(self, permutation: List[int], name: str = None, direct: bool = True):
        # TODO: write doc
        # check permutation validity
        if not (set(permutation) == set(i for i,_ in enumerate(self))):
            # TODO: write good msg error
            msg = ''
            raise ValueError(msg)
        
        # TODO: deal with direct=False
        
        pairs = []
        for current_rank, future_rank in enumerate(permutation):
            player = self[current_rank]
            ratings = self.datamodel.get(self[future_rank])
            pairs.append((player, ratings))
        for p, r in pairs:
            self.datamodel.set(p, r)
    
    @get_disamb
    @get_equi
    def fit(self, players: List[BasicPlayer], name: str = ''):
        seeding= Standing()
        points = []
        for player in players:
            if player in self:
                points.append(self.point(player))
            else:
                points.append(self.standing._default_)
        seeding.add(players, points)
        return seeding
    
    # --- internal mechanism --- #
    def __ContainerEquivalence(self):
        ''' property checker
        
        '''
        # get keys
        standing_keys = set(self.standing.keys())
        RatingSystem_keys = set(self.datamodel.keys())
        
        if standing_keys == RatingSystem_keys:
            self.__equivalence = True
        elif standing_keys <= RatingSystem_keys: # a <= b means 'a.issubset(b)
            not_ranked_players = list(RatingSystem_keys - standing_keys) # a - b means a.difference(b)
            new_points = []
            for player in not_ranked_players:
                # NOBUG: player is in the RatingSystem. 'get()' is safe to perform.
                new_points.append(self.datamodel.ordinal(self.datamodel.get(player)))
            # NOBUG: no ambiguity is introduce this way
            self.standing.add(keys=not_ranked_players, values=new_points)
            self.__equivalence = True
        else:
            # TODO: write a good error message
            msg = f''
            raise RuntimeError(msg)
        
    def __RankDisambiguity(self):
        for player in self.standing:
            # TODO: performance check (a) assign only if needed (b) assign always
            # ??? (a / b) as user options ?
            rating = self.datamodel.get(player)
            point = self.datamodel.ordinal(rating)
            if self.standing.value(player) != point:
                self.standing[player] = point
        
        self.__disambiguity = True

