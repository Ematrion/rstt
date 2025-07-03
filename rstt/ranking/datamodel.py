"""Module dedictated to RatingSystem

RatingSystem are ranking component acting as defaultdictionary to store rating for player.
It provide get(), set() and ordinal() methods.
"""

from typing import List, Any, Callable, Optional
from collections import defaultdict
from typeguard import typechecked

from rstt.stypes import SPlayer
from rstt import BasicPlayer

import copy


class keydefaultdict(defaultdict[SPlayer, Any]):
    def __init__(self, default_factory: Callable[[SPlayer], Any]):
        """Defaultdict with default values as function of the missing key.

        This allows rating system to have a default rating based on some data available in a Player instance, such has the level
        or a win rate ratio.

        Parameters
        ----------
        default_factory : Callable[[Player], Any]
            A function computing a default value for a missing key.
        """
        super().__init__()
        self.default_factory = default_factory

    def __missing__(self, key: SPlayer) -> Any:
        # Source: https://stackoverflow.com/a/73975965
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class KeyModel:
    @typechecked
    def __init__(self, default: Optional[Any] = None, template: Optional[Callable] = None, factory: Optional[Callable] = None, *args, **kwargs):
        r"""Basic Rating system

        The KeyModel is a intuitive implementation of :class:`rstt.stypes.RatingSystem` that strores ratings of player in a defauldict.
        The default rating value can be specified in three different fashions.

        Parameters
        ----------
        default : Any, optional
            A default rating value, by default None.
        template : Callable, optional
            A lambda function to generate default ratings, by default None
        factory : _type_, optional
            A Callable of the form lambda x: ..., where x is the SPlayer with no rating, by default None. If you pass a factory,
            the KeyModel stores ratings in  a :class:`rstt.ranking.datamodel.keydefauldict`.

        .. note::
            If you are using the \'template\' you can additionaly specify \*args and \**kwargs to be passed to the template every time it is called to generate a new rating.
            In the case of the \'factory\', only \**kwargs can be specified. And for the \'default\', no additonal parameters are allowed.

        Raises
        ------
        ValueError
            Error are raised in the case of incompatible parameters. Examples of valid calls are:
            KeyModel(default=1500)
            KeyModel(template=GaussianRating, 1500, 250)
            KeyModel(factory=GaussianRating, mu=1500, sigma=250)
        """
        self.__ratings = self.__init_ratings(
            default, template, factory, *args, **kwargs)
        self.__rtype = self.__get_rating_type()
        self.__default = self.__get_default_rating()

    # --- setter --- #
    @typechecked
    def set(self, key: SPlayer, rating):
        """Set method to manualy assign a rating to a player.

        Parameters
        ----------
        key : SPlayer
            A Player to modify the rating
        rating : Any
            a new rating.

        .. warning::
            The KeyModel class is a 'Generic' container in the sense that it can store any sort of rating, however, all values must be of the same type.
            With the current implementation it is unclear how to enforce it. So it is the responsability of the user to be consistent.

            The set operation will not throw any error. Yet, following calls to :func:`rstt.ranking.datamodel.KeyModel.ordinal` ordinal method could fail without proper error traceback.

            Hopefull future version will fix this issue.
        """
        # TODO: test rating type before assignement and thorw TypeError
        # !!! the problem is how the type is defined? built-in, class, protocol 'attribute protocol' ? isinstance does not work for all cases.
        self.__ratings[key] = rating

    # --- getter --- #
    @typechecked
    def get(self, key: SPlayer) -> Any:
        """getter method for the rating of a player

        Parameters
        ----------
        key : SPlayer
            A player to get the rating

        Returns
        -------
        Any
            The rating of the player
        """
        # QUEST: __getitem__ ?
        return self.__ratings[key]

    def items(self):
        """Dict like items() method

        return the view object returned by the underlying dict.items method

        Returns
        -------
        view object
            items stored in the KeyModel
        """
        return self.__ratings.items()

    def keys(self):
        """Dict like keys() method

        return the view object returned by the underlying dict.keys method

        Returns
        -------
        view object
            keys, i.e. SPlayer.
        """
        return self.__ratings.keys()

    # --- general purpose methords --- #
    def rtype(self) -> type:
        """Getter for the rating type

        .. warning::
            The type of ratings is infered at instanciation of the KeyModel using the type() built-in functions.
            However this can be inconsistant with the user's intention. 

        Returns
        -------
        type
            The rating type.
        """
        return self.__rtype

    def default(self) -> Any:
        """Getter for default rating

        When instanciated, a default rating is generated. In the case of a 'factory' instanciation, the default rating is built with the help of a 'Dummy' :class:`rstt.player.basicplayer.BasicPlayer`

        Returns
        -------
        Any
            The default rating an unrank player gets.
        """
        return self.__default

    def ordinal(self, rating: Any) -> float:
        """Convert a rating into a float value

        The returned value is used to compare players to each other. An higher value is understood as a 'better' player

        .. note::
            This method assume the existence of a magic __float__ method for the ratings.
            If one uses custom ratings object, it is good to either write such method, override the ordinal methods, or design an associated
            :class:`rstt.stypes.RatingSystem`.

        Parameters
        ----------
        rating : Any
            A rating compatible with the KeyModel.rtypes()

        Returns
        -------
        float
            The corresponding value used to compare players in an ordered fashion.
        """

        # REQ: Should not support arg type Player. This is the job of a Ranking/Standing
        # NOTE: name source -> https://fr.wikipedia.org/wiki/Nombre_ordinal
        return float(rating)

    def tiebreaker(self, rating: Any) -> List[Any]:
        """
        .. warning:: 
            DO NOT USE.

            Boilerplate code for future features.

        """
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
            - check functool.partial to improve code quaity and readabiltiy.
        '''
        if default != None and not template and not factory:
            if args or kwargs:
                msg = "Can not pass additional argument when using the 'default' parameter."
                raise ValueError(msg)
            ratings = self.__default_ratings(value=default)
        elif template and not default and not factory:
            ratings = self.__template_ratings(template, *args, **kwargs)
        elif factory and not default and not template:
            if args:
                msg = "Can not pass additional positional arguments with the 'factory' parameter specified. Did you mean to use template? Or did you want to pass keyword arguments instead?'"
                raise ValueError(msg)
            ratings = self.__factory_ratings(factory, **kwargs)
        else:
            msg = "Exactly one parameter among 'default', 'template' and 'factory' should be passed."
            raise ValueError(msg)
        return ratings

    def __default_ratings(self, value):
        return defaultdict(lambda: copy.deepcopy(value))

    def __template_ratings(self, template, *args, **kwargs):
        return defaultdict(lambda: template(*args, **kwargs))

    def __factory_ratings(self, func: Callable, **kwargs):
        return keydefaultdict(default_factory=func)

    def __get_rating_type(self):
        dummy = BasicPlayer('dummy', 0.0)
        # !!! This may not always work as intended
        rtype = type(self.__ratings[dummy])
        del self.__ratings[dummy]
        return rtype

    def __get_default_rating(self):
        dummy = BasicPlayer('dummy', 0.0)
        self.__ratings[dummy]
        return self.__ratings.pop(dummy)

    # --- magic methods --- #
    def __delitem__(self, key: SPlayer):
        del self.__ratings[key]

    # ??? __setitem__
    # ??? __getitem__
    # ??? __contain__


class GaussianModel(KeyModel):
    def __init__(self, *arg, **kwargs):
        """Gaussian Rating Systems

        Associated ratings must have a mu and a sigma attributes. 
        """
        super().__init__(*arg, **kwargs)

        '''
        TODO: type check the ratings, something like:
        if not hasattr(self.default(), 'mu') or not hasattr(self.default(), 'sigma'):
            # raise some kind of error
        Or maybe use Protocol with attributes
            
        '''

    # ??? How to typecheck: must at least support trueskill/openskill ratings and rstt GlickoRating
    def ordinal(self, rating) -> float:
        # TODO: cite a good source for the used policy
        """Ordinal method for gaussian values

        The methods implements the mean - 2 * standard deviation policy 

        Parameters
        ----------
        rating : Gaussian like object
            A floating value

        Returns
        -------
        float
            The corresponding value used to compare players in an ordered fashion
        """
        return rating.mu - 2*rating.sigma

    def tiebreaker(self, rating):
        return [rating.mu, rating.sigma]
