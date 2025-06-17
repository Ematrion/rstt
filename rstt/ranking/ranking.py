"""Ranking Module

This module implements utility decorator and a general ranking class.


Glossary
--------

    1. Container Equivalence (Union = Intersection):
    
        - (key in self.datamodel.ratings) <=> (key in self.standing).
        - In the code we refer to 'equivalence'

    2. Rank Disambiguity (point '=' rating):
    
        - self.datamodel.ordinal(key) == self.standing.value(key) for all keys.
        - In the code we refer to 'disambiguity'
    
"""

from typeguard import typechecked
from typing import Any, Union, List, Dict, Callable, Optional

from rstt.ranking import Standing
from rstt.stypes import Inference, RatingSystem, Observer, SPlayer


def set_equi(func: Callable[..., Any]) -> Callable[..., Any]:
    """Equivalence Set Decorator

    Decorator for Ranking methods.
    It enforces the equivalence property after the decorated methods execution

    Parameters
    ----------
    func : Callable[..., Any]
        A method that could alter the equivalence property

    Returns
    -------
    Callable[..., Any]
        A function enforcing the equivalence property
    """

    def wrapper_set(self, *args: Any, **kwargs: Any) -> Any:
        set_action = func(self, *args, **kwargs)
        if self._Ranking__maintain_equivalence:
            self._Ranking__ContainerEquivalence()
        return set_action
    return wrapper_set


def get_equi(func: Callable[..., Any]) -> Callable[..., Any]:
    """Equivalence Get Decorator

    Decorator for Ranking methods.
    It enforces the equivalence property before the decorated methods execution.

    Parameters
    ----------
    func : Callable[..., Any]
        A method that needs 'a-priori' the equivalence property to be satisfied

    Returns
    -------
    Callable[..., Any]
        A function with the expected behaviour.
    """

    def wrapper_get(self, *args: Any, **kwars: Any) -> Any:
        if self._Ranking__maintain_equivalence:
            self._Ranking__ContainerEquivalence()
        return func(self, *args, **kwars)
    return wrapper_get


def get_disamb(func: Callable[..., Any]) -> Callable[..., Any]:
    """Disambiguity Get Decorator

    Decorator for ranking methods.
    It enforces the disambuguity property before the decorated method execution.

    Parameters
    ----------
    func : Callable[..., Any]
        A method that needs 'a-priori' the disambuguity property to be satisfied.

    Returns
    -------
    Callable[..., Any]
        A function with the expected behaviour.
    """

    def wrapper_get(self, *args: Any, **kwars: Any) -> Any:
        if self._Ranking__maintain_disambiguity:
            self._Ranking__RankDisambiguity()
        return func(self, *args, **kwars)
    return wrapper_get


def set_disamb(func: Callable[..., Any]) -> Callable[..., Any]:
    """Disambiguity Set Decorator

    Decorator for ranking methods.
    It enforces the disambuguity property after the decorated method execution.

    Parameters
    ----------
    func : Callable[..., Any]
        A method that could alter the disambuguity property.

    Returns
    -------
    Callable[..., Any]
        A function enforcing the disambiguity property
    """

    def wrapper_set(self, *args: Any, **kwargs: Any) -> Any:
        set_action = func(self, *args, **kwargs)
        if self._Ranking__maintain_disambiguity:
            self._Ranking__RankDisambiguity()
        return set_action
    return wrapper_set


class Ranking():
    @typechecked
    def __init__(self, name: str,
                 datamodel: RatingSystem,
                 backend: Inference,
                 handler: Observer,
                 players: Optional[List[SPlayer]] = None):
        """Ranking for players

        The rstt package implements its own definition of a ranking.

        Formally an rstt ranking consist of a

            - A standing: An ordered sequence of players associated with an indication of their skills.
            - A rating system - storing player's rating.
            - A statistical inference system - set of equations.
            - An update procedure

        And two 'hidden' notions:

            - Observables: the set of 'update triggers' justifying a change of ratings. (what can be processed by the handler)
            - An ordinal function converting rating into float values (provided by the rating system)

        Parameters
        ----------
        name : str
            A name to identify the ranking
        datamodel : RatingSystem
            A container storing rating of players and providing an orinal() funtion to convert rating into floating values.
        backend : Inference
            The 'math' behind the ranking system.
        handler : Observer
            A workflow handling the ranking update procedure
        players : Optional[List[SPlayer]], optional
            Players to register in the ranking, by default None
        """

        # name/identifier - usefull for plot
        self.name = name

        # fundamental notions of the Ranking Class
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
    def add(self, keys: List[SPlayer]):
        """Add players to the ranking

        Each Player receive a default rating by the datamodel.
        It is possible to manipulate it using the set_rating() method.

        Parameters
        ----------
        keys : List[SPlayer]
            Players to be ranked.
        """
        # turn off maintainance for optimization
        should_maintain = self.__maintain_equivalence
        self.__maintain_equivalence = False

        # perform iteratively addition
        for key in keys:
            self.__add(key)

        # restaure Ranking status
        self.__maintain_equivalence = should_maintain

    def __add(self, key: SPlayer):
        if key in self:
            msg = f'Can not add a key already present in the Ranking, {key}'
            raise ValueError(msg)
        # default dict get operator for missing key
        self.datamodel.get(key)

        # self.datamodel do not match self.standing
        self.__equivalence = False

    # --- magic methods --- #
    def __getitem__(self, *args, **kwargs) -> Union[SPlayer, List[SPlayer], int, List[int]]:
        ''' get item based on a rank or a key

        NOBUG:
            - sorting is handled by the Standing itself
            - so is typechecking
        '''

        return self.standing.__getitem__(*args, **kwargs)

    def __delitem__(self, key: SPlayer):
        ''' delete element from the Ranking

        REQ:
            - element needs to be remove both from the standing and the RatingSystem

        NOBUG:
            - del standing[key] is typechecked. CALL MUST BE BEFORE RatingSystem

        # ???:
            - could del succeed on standing but fail on RatingSystem.
            This would potentialy lead to an invalid ranking state because __delitem__ is not decorated.
            A ranking invalid state can exactly be the reason why this scenario happens.
            What is the best approach to this situation ?
        '''
        del self.standing[key]
        del self.datamodel[key]

    def __contains__(self, key: SPlayer):
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
    def rank(self, player: SPlayer) -> int:
        """Getter for player Rank

        Equivalent to ranking.standing[player].


        Parameters
        ----------
        player : SPlayer
            A player to get his rank.

        Returns
        -------
        int
            The rank of the player
        """
        return self[player]

    def ranks(self, players: List[SPlayer]) -> List[int]:
        """Getter for players Rank

        Equivalent to ranking.standing[players].


        Parameters
        ----------
        players : SPlayer
            Player to get their ranks.

        Returns
        -------
        List[int]
            The corresponding ranks of the players
        """
        return [self.rank(player) for player in players]

    def rating(self, player: SPlayer) -> Any:
        """Get method for rating

        Rating object is the internal model associated to a key.
        Ratings are used to automaticly compute values for the sorting feature of a Standing.

        Parameters
        ----------
        player : Player
            A key in the Ranking

        Returns
        -------
        Any
            The associated model to the provided key. The type is defined by Ranking.RatingSystem.rtype

        Raises
        ------
        KeyError
        """
        if player in self:  # NOBUG RatingSystem is a defaultdict
            return self.datamodel.get(player)
        else:
            msg = f"{player} is not present in {self.standing}"
            raise KeyError

    def ratings(self) -> List[Any]:
        """Get method for all ratings

        Returns
        -------
        list[Any]
            A list of all rating object present in the Ranking, in order of the Standing.
        """
        return [self.rating(player) for player in self]

    def players(self) -> List[SPlayer]:
        """Get method of all keys

        Alias for Ranking.standing.keys()

        Returns
        -------
        List[Player]
            A list of all player in descending order of their associated values.
        """
        return self.standing.keys()

    def point(self, player: SPlayer) -> float:
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

    def status(self) -> Dict[str, Union[bool, str]]:
        """Get ranking's control variables

        This method can be usefull for debugging purposes.
        However, there should be no reason to use it unless a user intentionnaly manipulate the ranking internal mechanism.


        Returns
        -------
        Dict
            name of control variables with their current values.

        :meta private:
        """
        return {'equivalence': self.__equivalence,
                'disambiguity': self.__disambiguity,
                'maintain_equivalence': self.__maintain_equivalence,
                'm_disambanbiguity': self.__maintain_disambiguity}

    # ??? items() -> List[(rank, player, ratings)]
    # ??? item(key) -> (rank, player, ratings)
    # --- setter --- #
    @set_disamb
    @set_equi
    def set_rating(self, key: SPlayer, rating: Any):
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
        """Plot method

        Display the ranking to the standard output
        """
        self.standing.plot(standing_name=self.name)

    @set_disamb
    @set_equi
    def update(self, *args, **kwargs):
        """Update method

        Core functionality of the ranking class allowing player's rating to change and ranks to change.
        It accept aribitrary parameters.

        .. nwarning::
            This method in itself does not do anything. It is a wrapper ensuring any update do not alterate the internal state of the ranking.
            In no cases should this be overriden. Instead refer to :func:`rstt.ranking.ranking.Ranking.forward`
        """
        self.forward(*args, **kwargs)

        # NOTE: How do we know if the ranking state changed ?
        # HACK: always assume it did
        self.__disambiguity = False
        self.__equivalence = False

    def forward(self, *args, **kwargs):
        """Internal 'update' function

        This method calls the handler :func:`rstt.stypes.handle_observations` with the parameters of the update function.

        .. note::
            FOR RANKING DESIGNER ONLY
            method designed for devellopers who wants to modify the ranking.update function's behavivous.
            In most cases, it is sufficient to write an apropriate observer as the ranking.handler.

            However, sometimes it is relevant to do some ranking preprocessing before any rating updates.
            This would not always be possible to do inside the handle_observations method as the observer do not have access to all ranking attributes.
        """
        self.handler.handle_observations(infer=self.backend,
                                         datamodel=self.datamodel,
                                         *args, **kwargs)

    @set_equi
    @set_disamb
    @get_disamb
    @get_equi
    @typechecked
    def rerank(self, permutation: List[int], name: str = None, direct: bool = True):
        """Reorder the ranking.

        Inplace modification of the ranking state by reordering the players while maintaining a coherent state.
        This means that each player will be re assigned a new rating corresponding to the desired permuatation

        Parameters
        ----------
        permutation : List[int]
            A permutation of the ranking indices.
        name : str, optional
            A name, by default None
        direct : bool, optional
            Wether to apply the permutation directly, or its inverse, by default True

        Raises
        ------
        ValueError
            When the permutation is not a permutation over the ranking indices.
        """

        # check permutation validity
        if len(self) != len(permutation):
            # NOTE: without this check, the code will raise an IndexError and could be harder for the user to understand what went wrong.
            msg = f"permutation must be a list of len {len(self)}"
            raise ValueError
        if not (set(permutation) == set(list(range(len(self))))):
            msg = f"permutation must contain each value from 0 to {len(self)-1} exactly once"
            raise ValueError(msg)

        # rename the ranking:
        if name is not None:
            self.name = name

        pairs = []
        for current_rank, future_rank in enumerate(permutation):
            if not direct:
                current_rank, future_rank = future_rank, current_rank
            player = self[current_rank]
            ratings = self.datamodel.get(self[future_rank])
            pairs.append((player, ratings))
        for p, r in pairs:
            self.datamodel.set(p, r)

    @get_disamb
    @get_equi
    def fit(self, players: List[SPlayer]) -> Standing:
        seeding = Standing(default=self.standing._Standing__default,  # ??? lower instead of default
                           lower=self.standing._Standing__min,
                           upper=self.standing._Standing__max,
                           protocol=self.standing._Standing__protocol)  # Optimize
        points = [self.point(
            player) if player in self else None for player in players]
        seeding.add(players, points)
        return seeding

    # --- internal mechanism --- #

    def __ContainerEquivalence(self):
        ''' property checker'''

        # get keys
        standing_keys = set(self.standing.keys())
        RatingSystem_keys = set(self.datamodel.keys())

        if standing_keys == RatingSystem_keys:
            self.__equivalence = True
        elif standing_keys <= RatingSystem_keys:  # a <= b means a.issubset(b)
            # a - b means a.difference(b)
            not_ranked_players = list(RatingSystem_keys - standing_keys)
            new_points = []
            for player in not_ranked_players:
                # NOBUG: player is in the RatingSystem. 'get()' is safe to perform.
                new_points.append(self.datamodel.ordinal(
                    self.datamodel.get(player)))
            # NOBUG: no ambiguity is introduce this way
            self.standing.add(keys=not_ranked_players, values=new_points)
            self.__equivalence = True
        else:
            # TODO: write a good error message
            msg = f''
            raise RuntimeError(msg)

    def __RankDisambiguity(self):
        ''' property checker'''
        for player in self.standing:
            # TODO: performance check (a) assign only if needed (b) assign always
            # ??? (a / b) as user options ?
            rating = self.datamodel.get(player)
            point = self.datamodel.ordinal(rating)
            if self.standing.value(player) != point:
                self.standing[player] = point

        self.__disambiguity = True
