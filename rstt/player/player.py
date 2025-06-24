from typing import List, Union, Optional
from typeguard import typechecked

from rstt.player.basicplayer import BasicPlayer
from rstt.game import Match
from rstt.stypes import SMatch, Achievement


class Player(BasicPlayer):
    @typechecked
    def __init__(self, name: Optional[str] = None, level: Optional[float] = None) -> None:
        """Player with match history.

        Player extends :class:`rstt.player.basicPlayer.BasicPlayer` with the possibility to track games it played in and
        by collecting results achieved in :class:`rstt.stypes.Achievement`. 

        Parameters
        ----------
        name : str, optional
            A unique name to identify the player. By default None, in this case a name is randomly generated.
        level : float, optional
            The level/skill/strenght of the player. By default None, in this case a level is randomly generated.
            using a random distribution :class:`rstt.config.PLAYER_DIST
            with default parameters :class:`rstt.config.PLAYER_DIST_ARGS`
        """
        super().__init__(name=name, level=level)
        self.__achievements: list[Achievement] = []
        self.__games: list[SMatch] = []

    # --- getter --- #
    def achievements(self) -> List[Achievement]:
        """Getter method for achievement

        :class:`rstt.stypes.Achievement` represent tournament result of the player. 

        Returns
        -------
        List[Achievement]
            All past success of the player in chronological order, from the oldest to the most recent.
        """
        return self.__achievements

    def earnings(self) -> float:
        """Getter method for the earnings

        Sugar method that returns the sum of earnings specified by the player achievements.

        Returns
        -------
        float
            All the money earned in competitif event.
        """
        return sum([achievement.prize for achievement in self.__achievements])

    def games(self) -> List[Match]:
        """Getter method for match the player participated in

        Returns
        -------
        List[Match]
            All the matches the player played in chronolgical order, from oldest to the most recent.
        """
        return self.__games

    # --- setter --- #
    @typechecked
    def collect(self, achievement: Union[Achievement, List[Achievement]]):
        """Adds achivement(s) to the player history.

        Parameters
        ----------
        achievement : Union[Achievement, List[Achievement]]
            Achievement(s) passed must have a different event_name attribute that the one already stored.

        Raises
        ------
        ValueError
            Raised when attempting to collect an event with an event_name already present in the player history. 
        """
        if isinstance(achievement, Achievement):
            achievements = [achievement]
        else:
            achievements = achievement

        previous_event = [
            past_event.event_name for past_event in self.__achievements]
        for achievement in achievements:
            if achievement.event_name not in previous_event:
                self.__achievements.append(achievement)
            else:
                msg = f"Can not collect {achievement}. {self} already participated in an event called {achievement.event_name}"
                raise ValueError(msg)

    @typechecked
    def add_game(self, match: Match) -> None:
        """Adds match to the player history

        Parameters
        ----------
        match : Match
            A match to track.

        Raises
        ------
        ValueError
            The match needs to be a game in which the player partipiated in and not already tracked. Either condition violated will raise an Error.
        """
        if match in self.__games:
            msg = f"{match} already present in game history of player {self}"
            raise ValueError(msg)
        if self not in match.players():  # !!! Untested Feature
            msg = f"Can not collect a match {match} that player {self} has not been part of."
            raise ValueError
        self.__add_game(match)

    @typechecked
    def reset(self, games: bool = True, achievement: bool = True) -> None:
        """Clean the player history

        Removes all matchs and achievements from the players history. 

        Parameters
        ----------
        games : bool, optional
            Wether matchs should be removed, by default True. 
        achievement : bool, optional
            Wether achievements should be removed, by default True.
        """
        if achievement:
            self.__achievements = []
        if games:
            self.__games = []

    # --- internal mechanism --- #
    def __add_game(self, match: Match) -> None:
        self.__games.append(match)
