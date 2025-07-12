from typing import Dict, Any, Callable, Optional
from typeguard import typechecked
import rstt.config as cfg

import names


class BasicPlayer():
    @typechecked
    def __init__(self, name: Optional[str] = None,
                 level: Optional[float] = None) -> None:
        """Basic Player

        BasicPlayer have a level and a name, that is it. The bare minimum for simulation to run.
        This class is usefull for when your player do not need to track their match history and do not have a time varying level.

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : Optional[float], optional
            The level/skill/strenght of the player. By default None, in this case a level is generated
            using a random distribution :class:`rstt.config.PLAYER_DIST
            with default parameters :class:`rstt.config.PLAYER_DIST_ARGS`
        """
        self.__name = name if name else names.get_full_name()
        self.__level = level if level is not None else cfg.PLAYER_DIST(
            **cfg.PLAYER_DIST_ARGS)

    # --- getter --- #
    def name(self) -> str:
        """Getter method for the name of the player

        Returns
        -------
        str
           The name of the player
        """
        return self.__name

    def level(self) -> float:
        """Getter method for the player's level

        Returns
        -------
        float
            The level of the player.
        """
        return self.__level

    # --- magic methods --- #
    def __repr__(self) -> str:
        return f"Player - name: {self.__name}, level: {self.__level}"

    def __str__(self) -> str:
        return self.__name

    @classmethod
    @typechecked
    def create(cls, nb: int,
               name_gen: Optional[Callable[..., str]] = None,
               name_params: Optional[Dict[str, Any]] = None,
               level_dist: Optional[Callable[..., float]] = None,
               level_params: Optional[Dict] = None):  # -> List[SPlayer]
        """Class method to generate multiple player at once.

        Customizable method to generate a bunch of players with your favorite settings.

        Parameters
        ----------
        nb : int
            The amount of player to create and return.
        name_gen : Callable[..., str], optional
            A name generator. By default None, in this case names are generated using the `names <https://pypi.org/project/names/>`_ package.
        name_params : Dict[str, Any], optional
            Kwargs to pass to the name_gen function, by default None.
        level_dist : Callable[..., float], optional
            A level generator. By default None, in this case it uses a random distribution specifed by :class:`rstt.config.PLAYER_DIST`.
        level_params : Dict, optional
            Kwargs to pass to the level_dist. By default None, in this case it uses default parameters specified by :class:`rstt.config.PLAYER_DIST_ARGS`

        Returns
        -------
        List[BasicPlayer]
            A list of player.
        """
        name_gen = names.get_full_name if name_gen is None else name_gen
        name_params = {} if name_params is None else name_params
        # BUG: When PlayerTVS have their own
        level_dist = level_dist if level_dist else cfg.PLAYER_DIST
        level_params = level_params if level_params else cfg.PLAYER_DIST_ARGS

        # !!! hack due to several PlayerTVS not having level args (Gauss/Exp/Log-Player, which have a start/mu instead)
        if cls.__name__ == 'BasicPlayer':
            return [cls(name=name_gen(**name_params), level=level_dist(**level_params)) for i in range(nb)]
        else:
            return [cls(name=name_gen(**name_params)) for i in range(nb)]

    @classmethod
    @typechecked
    def seeded_players(cls, nb: int, start: int = 0, inc: float = 100):
        """Create 'seeded' players

        Unlike the :func:`rstt.player.basicplayer.BasicPlayer.create` method, players generated have a deterministic name and level.
        Names are of the form f"Seed_{i}", and the lowest i, the higher the level of the player.

        .. warning::
            The rstt package relies on player's name to identify them - there is no ID. This method can result in name clashing which may lead to confusion and unexpected bahaviour accross simulations.
            It is heavly recommanded to be carefull when calling this method multiple times. Either by tuning the 'start' parameter or deleting previously created player.

        Parameters
        ----------
        nb : int
            The amount of player to create and return.
        start : int, optional
            The first 'i' for the name of players, by default 0.
        inc : float, optional
            The difference of level between playery Seed_i and Seed_i+1, by default 100.

        Returns
        -------
        List[BasicPlayer]
            A list of seeded player in desceding order of level.
        """
        end = start + (nb * inc)
        levels = list(range(start, end, inc))
        names = [f"Seed_{i}" for i in range(nb, 0, -1)]
        return [cls(name=name, level=level) for name, level in zip(names, levels)]
