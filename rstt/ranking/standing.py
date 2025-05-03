"""Standing Ranking

Standing is a sorted container class implementing a triplet relationship between player, rank and points.
"""

from typing import Union, List, Dict, Tuple, Callable, Any, Optional

from typeguard import typechecked
import numpy as np

from rstt.stypes import SPlayer
import rstt.utils.utils as uu


GET_SORT = 'get'
SET_SORT = 'set'
NEVER = 'never'
ALWAYS = 'always'


def get_sort(func: Callable[..., Any]) -> Callable[..., Any]:
    """Sorting Get Decorator

    Decorator for Standing methods.
    It ensures that contained element (Players) are sorted in descending order of their associated values.

    Parameters
    ----------
    func : Callable[..., Any]
        A standing that needs 'a-priori' correct ordering of the standing.

    Returns
    -------
    Callable[..., Any]
        A function with the expected behaviour.
    """

    def wrapper_get(self: Any, *args, **kwars) -> Any:
        """:meta private:"""
        if self._Standing__protocol in [GET_SORT, ALWAYS]:
            self._Standing__sort()
        return func(self, *args, **kwars)
    return wrapper_get


def set_sort(func: Callable[..., Any]) -> Callable[..., Any]:
    """Sorting Set Decorator

    Decorator for Standing methods.
    It ensures that contained element (Players) are sorted in descending order of their associated values.

    Parameters
    ----------
    func : Callable[..., Any]
        A standing method that can alter the sorting order

    Returns
    -------
    Callable[..., Any]
        A function that enforces the correct standing ordering.
    """

    # FIXME:
    #   - 'lazy' sorting. Some set/edit operations are performing iteratively modifications.
    #   The sorting should only be called after the last operation, when the 'user call' is done.
    #   Example: add() and __add()

    def wrapper_set(self: Any, *args, **kwargs) -> Any:
        """:meta private:"""
        set_action = func(self, *args, **kwargs)
        if self._Standing__protocol in [SET_SORT, ALWAYS]:
            self._Standing__sort()
        return set_action
    return wrapper_set

# TODO: ADD
# def not_sorted_error(func: Callable[..., Any]) -> Callable[..., Any]:
#    def wrapper_check(self: Any, *args, **kwargs) -> Any:
#        if not self._Standing__sorted:
#            msg = f"Can not call {func.__name__} on unsorted Standing"
#            raise RuntimeError(msg)
#        return func(self, *args, **kwargs)
#    return wrapper_check


class Standing:
    def __init__(self, default: float = 0.0,
                 lower: float = np.iinfo(np.int32).min,
                 upper: float = np.iinfo(np.int32).max,
                 step: float = 1.0,
                 protocol: str = SET_SORT):
        """A Standing object emulate a value-based ordered dictionary.

        The Standing also act as a <list> and a <dict> and the following relationship exist:
            - Index -> Key
            - Key -> Index

        Keys oredring is descedning and based on the associated value of the key, i.e Standing.point(key).

        The key ordering is maintain by internal mechanism as long as the Standing is manipulate with
        the provided methods and functionnalities.

        Examples
        --------

        .. note::
            Ordering is computationaly demanding, which means that repeated operations on a large Standing could result
            in performances issues. It is possible to turn off the ordering features.
            This break the whole point of the class. Do it only if needed and if you know what your are doing

            In its current form Key are intended to be of Type <Player> and Value of type <float>.
            This may change in the future to support a more general case such as:
            Key of type <Hasable> -> Value of type <Comarapble>.

        Parameters
        ----------
        default : float, optional
            A key added to the standing without an associated value will be assign this default value, by default 0.0
        min : float, optional
            The minimal boundary for values, by default np.iinfo(np.int32).min
        max : float, optional
            The maximal boundary for values, by default np.iinfo(np.int32).max
        step : float, optional
            An interval used for insertion operation , by default 1.0
            NOTE: not completely supported, could disapear in futur version.
        """

        # data
        self.ranks = []  # [(key: Player, value: float)]
        self.__default = default  # default value

        # sorting controls
        self.__sorted = True
        self.__maintain = True
        self.__protocol = protocol  # used by decorators

        # NOTE:  Untested feature. Delete ?
        self.__min = lower
        self.__max = upper
        self.__step = step

    # --- sorting algorithm --- #
    def __sort(self):
        ''' Sorting method

        Sort self.ranks [(key, value)] based on values
        NOTE: (conceptual)
            - __sort is never called 'as-it', _Standing__sort is called by get/set_sort decorator
        '''
        if self.__maintain and not self.__sorted:
            # NOTE: the general idea is: (1) sort on value, (2) on key
            # TODO: use functool lib to define the 'cmp' policy
            self.ranks.sort(key=lambda x: (x[1], x[0].name()), reverse=True)
            self.__sorted = True

    # --- general purpose methords --- #
    @get_sort
    def plot(self, standing_name: Optional[str] = "Standing"):
        """Plot method

        Print the Standing in a text form as Index-Key-Value.

        Parameters
        ----------
        standing_name : Optional[str], optional
            A name has standing header, by default "Standing"
    """
        print(f"----------- {standing_name} -----------")
        for i, (k, v) in enumerate(self.ranks):
            print("{:>5} {:>20} {:>10}".format('%d.' % i, '%s' % k, '%d' % v))

    @typechecked
    def fit(self, keys: List[SPlayer]):
        """Create a new Standing instance containing only the given Keys

        The Keys will have the same value as in the current Standing if present
        otherwise the default value will be assigned.

        Parameters
        ----------
        keys : List[Player]
            list of <Player> to be present in the new Standing

        Returns
        -------
        Standing
        """
        seeding = Standing(self.__default, self.__min, self.__max, self.__step)
        points = [self.value(key) if key in self else None for key in keys]
        seeding.add(keys, points)
        return seeding

    @set_sort  # ??? does not make any sense. No set operation on the standing instance. get_sort?
    @typechecked
    def rerank(self, permutation: List[int], inverse: bool = False):
        """Create a new Standing with a different ordering of its keys.

        Create a new Standing where key have different value associated.
        Key at index 'i' will have the value of the Key at index permutation[i].

        Parameters
        ----------
        permutation : List[int]
            a permutation
        inverse : bool, optional
            Wether permutation should be interpreted directly,
            or as its inverse funtion. If inverse is True then Key at index permutation[i]
            will have the value of Key at index i , by default False.

        Returns
        -------
        Standing
            A rearranged ordering of the keys.
        """

        # create new Standing instance
        new_standing = Standing(
            self.__default, self.__min, self.__max, self.__step)

        # compute key-value pairs
        if inverse:
            keys_values = [(self[p_i], self.value(i))
                           for i, p_i in enumerate(permutation)]
        else:
            keys_values = [(self[i], self.value(p_i))
                           for i, p_i in enumerate(permutation)]

        keys, values = [item[0] for item in keys_values], [item[1]
                                                           for item in keys_values]

        # add items to the new Standing
        new_standing.add(keys, values)
        return new_standing

    # --- getter --- #
    @get_sort
    @typechecked
    def percentile(self, key: SPlayer) -> float:
        """Getter funtion for the percentile of a player

        Informatin about the relative position of a player in the standing

        Parameters
        ----------
        key : SPlayer
            A player to get his relative postiion

        Returns
        -------
        float
            The percentile of the player as his relative position in the ranking
        """
        return (self[key]+1)/len(self) * 100.00

    @get_sort
    def ties(self) -> bool:
        """Quick overview wether the Standing contains keys with equal value.

        Standing implement an 'Ordinal Ranking' which means that two key if equal values will have a different rank.

        Note
        ----
        Currently the assignement of disctinct rank uses the Player.name() returned value.
        This could change in future version to support customized policy.

        Returns
        -------
        bool
            If True, the Standing contains at least a two keys with equal value.
        """
        points = set([entry[1] for entry in self.ranks])
        return len(points) != len(self)

    # TODO: define clearly output format
    @get_sort
    def tied_items(self) -> Dict[float, List[SPlayer]]:
        """Getter method for tied items in the Standing

        Returns
        -------
        Dict[Tuple[int, int], List[Player]]
            return a dictionary where keys are a tuple indicating the ranks range and values are the tied keys (player)
        """
        ties = {}
        values = uu.multiples([entry[1] for entry in self.ranks])
        for val in values:
            ties[val] = []
            for player in self:
                if self.value(player) == val:
                    ties[val].append(player)
        for val in values:
            top = (min(self[ties[val]]), max(self[ties[val]]))
            ties[top] = ties[val]
            del ties[val]
        return ties

    # --- setter --- #
    @set_sort
    @typechecked
    # TODO: investigate redundancy between sorting=False and protocol='never'
    # TODO: define protocol type (enum ?)
    def set_sorting(self, sorting: bool = None, protocol: str = None):
        """Set the ordering properties of the Standing

        Control the internal mechanism. How/When the Standing handle the data and the sorting calls. 

        Parameters
        ----------
        sorting : bool, optional
            Define wether the Standing should be sorted or not, by default None.

            - True: the Standing will sorts itself automaticly upon future method calls.
            - False: the Standing will not sorts itself.
            - None: the current behaviour is maintained.

        protocol : str, optional
            Define which sorting stategy is used, by default None

            - 'get': An unsorted Standing will be 'updated' upon a query on its state (keys(), values(), plot(), ...).
            - 'set': An unsorted Standing will be 'updated' upon a modification of its state (add(), insert(), ...)
            - 'always': An unsorted Standing will be updated at every opportunity.
            - None: the current strategy is maintained.


        .. warning::
            This method should only be used to optimize code performance when needed and by user aware of the consequences.
            Here some advice:

                - protocol='get' when a portion of code is slow and performs a lot of 'set-operations'.
                - protocol='set' when a portion of code is slow and performs a lot of 'get-operations'.
                - protocol='always' anytime performances are not an issue.
                - protocol='never' the standing stops ordering itself automaticaly.
                - sorting=False when the order of the keys in the Standing do not matter.
        """

        self.__maintain = sorting
        self.__protocol = protocol

    @typechecked
    @set_sort
    def insert(self, index: int, key: SPlayer):
        """List like insertion

        insert a key at a given position in the list.
        It will automaticly compute an appropriate value to assign.

        Parameters
        ----------
        index : int
            Position in the list 'rank' of the given key 
        key : Player
            The element to insert in the Standing
        """
        self.__setitem_index_key(index, key)

    # TODO: support other signature such as list of tuples and dictionaries - typecheck
    @set_sort
    def add(self, keys: List[SPlayer], values: Optional[List[float]] = None):
        """Add key-value pairs to the Standing

        Method to add items to the Standing.
        The values are optional as Standing has a default value specified.

        Note
        ----
        The current implementation only supports list of keys and list of values as parameters.
        Futur version could include parameters such as dict[key, value] and iterable of tuples.

        Parameters
        ----------
        keys : List[Player]
            Element to insert in the Standing
        values : List[float], optional
            Associated values of the keys, by default None.
            If len(values) < len(keys) the method will add as many items (key, value)
            to the standing before using the Standing default value for the remaining keys, 
        """

        # FIXME:
        #    - turning off sorting seems unecessary since __add() is not a @set_sort decorated method
        #    - test performances & requirements without it

        # turn off sorting for optimisation
        should_sort = self.__maintain
        self.__maintain = False

        if values is None:
            values = []

        # perform iteratively addition
        for i, key in enumerate(keys):
            try:
                self.__add(key, values[i])
            except IndexError:
                self.__add(key, self.__default)

        # restaure Standing status
        self.__maintain = should_sort

    # --- Containers standard methods --- #
    @get_sort
    def keys(self) -> List[SPlayer]:
        """Get method for keys

        Similar to dict.keys() but it returns a list, not a view.

        Returns
        -------
        List[Player]
            A list with all the item registered in the Stadning
        """
        return [item[0] for item in self.ranks]

    @get_sort
    def values(self) -> List[float]:
        """Get method for values

        Similar to dict.values() but it returns a list, not view.

        Returns
        -------
        List[float]
            A list with all the values in the Standing
        """
        return [item[1] for item in self.items()]

    @get_sort
    @typechecked
    # !!! value() is a user level method. yet it is used in many places and triggers a lot of unecessary get_sort
    def value(self, key: Union[SPlayer, int]) -> float:
        """Get value for a single key

        Return the value associated to the key in the Standing.
        The key can be a index/rank or an element of the Standing

        Parameters
        ----------
        key : Union[Player, int]
            A key to get the value, either the index or the actual element contained in the Standing

        Returns
        -------
        float
            The associated value to the key.
        """
        if isinstance(key, int):
            return self.ranks[key][1]
        elif isinstance(key, SPlayer):
            return self.ranks[self.index(key)][1]

    @get_sort
    @typechecked
    def items(self) -> List[Tuple[SPlayer, float]]:
        """Get method for key value pairs

        Similar to dict.items(). It returns a list of tuples (key, value).

        Returns
        -------
        List[Tuple[Player, float]]
            List of items as tuple (key, value).
        """
        return self.ranks

    @get_sort
    @typechecked
    def index(self, key: SPlayer) -> int:
        """Get index for key

        Similar to list.index(). Standing implements an 'Ordinal Ranking' upon the set of keys based on associtaed values.

        Parameters
        ----------
        key : Player
            The key to find in the Standing.

        Returns
        -------
        int
            The rank of the key in the Standing. 
        """
        return self.keys().index(key)

    @get_sort
    @typechecked
    def pop(self, key: Union[int, List[int], SPlayer, List[SPlayer]]) -> Union[SPlayer, List[SPlayer], int, List[int]]:
        """Get and remove method for element.

        Similar list.pop() and dict.pop() with some notable distinction. It deletes the corresponding items but:
        - If key(s) are index(es)then it returns the keys present at those ranks.
        - If key(s) are to Player(s) then it and returns the corresponding index(es)/rank(s).

        Parameters
        ----------
        key : Union[int, List[int], Player, List[Player]]
            Accessor to the Elements to delete.

        Returns
        -------
        Union[Player, List[Player], int, List[int]]
            The corresping alternative keys. 
        """
        item = self.__getitem__(key)
        self.__delitem__(key)
        return item

    @get_sort
    @typechecked
    def remove(self, key: Union[int, List[int], SPlayer, List[SPlayer]]) -> Union[SPlayer, List[SPlayer], int, List[int]]:
        """Remove item method

        Works as Standing.pop() but without return values.

        Parameters
        ----------
        key : Union[int, List[int], Player, List[Player]]
            Accessor of items to delete
        """
        self.__delitem__(key)

    # --- internal mechanism --- #
    def __add(self, key: SPlayer, value: float = None):
        '''
        method responsible of the inclusion of new item inside the Standing

        REQ:
            - no typechecking because it is called internaly,
            i.e. when type should already been approved
            - this is the only funtion that should use the self.__default
            i.e. self.__add(key, self.__default) should never be called
        '''
        if key not in self:
            if value is not None:
                value = min(max(value, self.__min), self.__max)
            else:
                value = self.__default
            self.ranks.append((key, value))
            self.__sorted = False
        else:
            msg = f"Attempt to add a key ({key}) already present in the Standing {self})"
            raise KeyError(msg)

    def __delitem_index(self, index: Union[int, slice, List[int]]):
        '''
        Method responsible to delete items based on ranks/index

        Implements one of the __delitem__ behaviour, namely a 'list like del'

        REQ:
            - support int, slice, list
            - no typechecking because it is called internaly

        FIXME:
            - raise error/warnings based on __sorted, __maintain
        '''
        if isinstance(index, int):
            del self.ranks[index]
        elif isinstance(index, slice):
            keys = self[index]
            self.__delitem_key(keys)
        else:
            # QUEST: is it better to use the same approach as for slice, than sorting the indexes ?
            for i in sorted(index, reverse=True):
                del self.ranks[i]

    def __delitem_key(self, key: Union[SPlayer, List[SPlayer]]):
        '''
        Method responsible to delete items based on keys

        Implements one of the __delitem__ behaviour, namely a 'dict like del'

        REQ:
            - support Player and List
            - no typechecking because it is called internaly
            - Is not sorting dependant.
        '''
        if isinstance(key, SPlayer):
            self.__delitem_index(self.index(key))
        else:
            for k in key:
                # QUEST: use self.__delitem_key(k) ?
                self.__delitem_index(self.index(k))

    def __setitem_key_value(self, key: SPlayer, value: float):
        '''
        Method responsible to set an item value based on the key

        Implements one of the __setitem__ behaviour, namely a 'dict like set'

        REQ:
            - support set operation for key
            - no typechecking because it is called internaly
            - Is not sorting dependant.

        '''
        if key not in self:
            self.__add(key, value)
        else:
            self.__change_key_value(key, value)

    def __setitem_index_key(self, index: int, key: SPlayer):
        '''
        Method responsible to set an item value based on the key

        Implements one of the __setitem__ behaviour.
        Conceptualy is a 'dict-like set' but for (key, index) and not (key, value).
        technically works and do the job of a list.insert() by computating a suitable value for the key.

        REQ:
            - no typechecking because it is called internaly
            - Is sorting dependant

        FIXME:
            - raise/error for operation when not sorted

        # BUG: 
            - does not have the expected behaviour for an-already contained key. check __add()
        '''
        if index == 0:
            point = min(self.ranks[0][1] + self.__step, self.__max)
        elif index == len(self):
            point = max(self.ranks[-1][1] - self.__step, self.__min)
        else:
            point = (self.ranks[index-1][1] + self.ranks[index][1]) / 2
        self.__add(key, point)

    def __change_key_value(self, key: SPlayer, value: float):
        '''Method responsible to change the value of a key.

        This Method assign to an already present key a new value in adict-like fashion

        NOTE:
        In Standing a key should be present at most once (like in a dictionary, unlike in a list).
        This challenges some design concept. What does it means to insert an already existing key, 
        but at a different index, or with a different value?

        This method aims to match the syntax 'my_Standing_insnatce[already_existing_key] = different_value'
        with its intuitive behaviour - the one of dictionaries. 
        '''
        if key in self:
            self.__delitem_key(key)
            self.__add(key, value)
        else:
            msg = f"Attempt to change the value of a key ({key}) not present in the Standing {self}"
            raise KeyError(msg)

    # --- magic methods --- #
    @get_sort
    @typechecked
    def __getitem__(self, key: Union[int, slice, List[int], SPlayer, List[SPlayer]]
                    ) -> Union[SPlayer, List[SPlayer], int, List[int]]:
        '''
        Method responsible to get an item

        It implements a symetrical like relation between index and key
        for a given pair (key, index) the following line should always be True.
            Standing[key] == index && Standing[index] == key 

        REQ:
            - typecheking because it is at the user interface layer.
            - symetrical key, index relationship
            - support int, list and slice for Index
            - support Player and list for Key

        ALERT: This function implements at the user level many different behaviours. 
        No Operation should directly be perofrmed in it.
        Rather, calls are filtered and directed to more specific internal methods.

        # QUEST:
            - is the use of isinstance() appropriate
            - is it the good ordering of type control ?

        # NOTE:
            Coding can look confusing because it uses the [] syntax inside the __getitem__() method.
            The internal mechanism used here, are the one offered by python list and tuple class.

        '''
        if isinstance(key, slice):
            return [player[0] for player in self.ranks][key]
        elif isinstance(key, SPlayer):
            return self.index(key)
        elif isinstance(key, int):
            return self.ranks[key][0]
        elif isinstance(key, list) and isinstance(key[0], SPlayer):
            return [self.index(player) for player in key]
        elif isinstance(key, list) and isinstance(key[0], int):
            players = [player[0] for player in self.ranks]
            return [players[index] for index in key]

    @set_sort
    @typechecked
    def __setitem__(self, key: Union[int, SPlayer], value: Union[SPlayer, float]):
        '''
        Method responsible set an item in the Standing

        It offers the interfaces
            - list-like where a key can be assigned to an index.
            works like an insert() operation
            - dict-like where a value can be assigned to a key

        REQ:
            - typecheking because it is at the user interface layer.
            - dict & list like __setitem__

        QUEST: What about Standing[key] = index
        The assignement of an index to a key is ambiguous.
        Is the parameter value to be interpreted as an index or as the value of the key-value pair.
        This issue can be adressed once The typing problematic is solved. 

        ALERT: This function implements at the user level many different behaviours. 
        No Operation should directly be perofrmed in it.
        Rather, calls are filtered and directed to more specific internal methods.

        BUG: 
            - There are major concern regarding set for key already present, see the sub method called.
            - The set index for already present key is a challenging concept in itself. It Should
            at least raise a warning

        '''
        if isinstance(key, int) and isinstance(value, SPlayer):
            self.__setitem_index_key(key, value)
        elif isinstance(key, SPlayer) and isinstance(value, float):
            self.__setitem_key_value(key, value)
        elif isinstance(key, SPlayer) and isinstance(value, int):
            self.__setitem_index_key(value, key)

    @typechecked
    def __delitem__(self, elem: Union[slice, int, List[int], SPlayer, List[SPlayer]]):
        '''
        Method responsible to delete item

        REQ:
            - typecheking because it is at the user interface layer.
            - support int, list and slice for Index
            - support Player and list for Key

        ALERT: This function implements at the user level many different behaviours. 
        No operation should directly be perofrmed in it.
        Rather, calls are filtered and directed to more specific internal methods.

        FIXME:
            - deleting by index when the Standing is not sorted should raise error.
            - When keep_sorting is false it should raise a warning at least.
        '''

        if isinstance(elem, SPlayer) or (isinstance(elem, list) and isinstance(elem[0], SPlayer)):
            self.__delitem_key(elem)
        else:
            self.__delitem_index(elem)

    @typechecked
    def __contains__(self, key: SPlayer):
        return key in [item[0] for item in self.ranks]

    def __len__(self):
        return len(self.ranks)

    @get_sort
    def __iter__(self):
        ''' 
        Iterator magic method

        REQ:
            - provide an iterator on the contained keys
            - should iterate in 'order'

        NOTE: 
            - Not sure to understand exactly what is going on here.
        It is possible to iterate on Standing without, however Standing
        would not be instance of Iterable/Collection.
        This implementation seems to maintain the proper iteration behaviour
        and it make isinstance(Standing, Iterable/Collection) True - WHICH IS GOOD
        '''
        return [entry[0] for entry in self.ranks].__iter__()

    def __str__(self):
        return str(self.ranks)

    def __repr__(self):
        return f"Standing({self.ranks})"
