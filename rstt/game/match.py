from typing import List, Optional
from typeguard import typechecked

from rstt.stypes import SPlayer, Score
import rstt.config as cfg


class Match():
    @typechecked
    def __init__(self, teams: List[List[SPlayer]], tracking: Optional[bool] = None) -> None:
        """Match base Class

        General purpose match class. It can be used to create arbitrary game mode such as Many-versus-Many or Free-For-All games.

        Parameters
        ----------
        teams : List[List[SPlayer]]
            Participants of the match organized in a list of list. Players in the same sublist are part of the same team.
        tracking : bool, optional
            If true, the match will try to add itself to the participants game history, by default None.

        Raises
        ------
        ValueError:
            A Splayer can not be an element of two distinct sublist in the parameter teams.
        """
        self.__teams = teams
        self.__scores = None
        self.__tracking = tracking if tracking is not None else cfg.MATCH_HISTORY

        if len(set(self.players())) != len(self.players()):
            msg = f"Teams must contain different players."
            raise ValueError(msg)

    # --- getter --- #
    def teams(self) -> List[List[SPlayer]]:
        """Getter method for teams

        Returns
        -------
        List[List[SPlayer]]
            All the players participating in the match grouped by teams. 
        """
        return self.__teams

    def players(self) -> List[SPlayer]:
        """Getter method for player

        Unlike :func:`rstt.game.match.Match.teams`, it returns a simple list of SPlayer, without grouping them by teams.

        Returns
        -------
        List[SPlayer]
            All the participants of the match.
        """
        return [player for team in self.__teams for player in team]

    def opponents(self, player: SPlayer) -> List[SPlayer]:
        """Getter method for opponents

        Opponents are participants of the match that or not in the same team as the given player.

        Parameters
        ----------
        player : SPlayer
           A player to get the opponents

        Returns
        -------
        List[SPlayer]
            A list of opponents playing against the player, in a single list, not grouped by teams
        """
        return [p for p in self.players() if p not in self.teammates(player)]

    def teammates(self, player: SPlayer) -> List[SPlayer]:
        """Getter method for teammates

        Teammates of a player are other players in the same teams

        Parameters
        ----------
        player : SPlayer
            A player to get teammates

        Returns
        -------
        List[SPlayer]
            All the player's teammates
        """
        for team in self.players():
            if player in team:
                return [p for p in team if p != player]

    def scores(self) -> Score:
        """Getter method for the match outcome

        The result/outcome of the match. A :class:`rstt.stypes.Score` is a list of float.
        The length of the Score is equal to the number of teams (i.e the length of the return value of :func: `rstt.game.match.Match.teams`).

        Returns
        -------
        Score
            The outcom of the match. None if the match has not been played yet. Ordering of the float value matches the ordering of the teams as return by :func:`rstt.game.match.Match.teams`
        """
        return self.__scores

    def score(self, player: SPlayer) -> float:
        """Getter method for the score of a given player. 

        Unlike the :func:`rstt.game.match.Match.scores`, this function return a single float value representing the success the parameter player had. 

        Parameters
        ----------
        player : SPlayer
            A player to get the score.

        Returns
        -------
        float
            A value representing the score, result of the player.

        Raises
        ------
        RuntimeError
            This method can only be called when the match has been played and assigned a score.
        """
        if self.__scores is None:
            msg = f"Undefined score of player {player} is undefined. The match has not yet been assigned a score."
            raise RuntimeError(msg)

        for team, score in zip(self.__teams, self.__scores):
            if player in team:
                return score

    def ranks(self) -> List[int]:
        """Getter method for the team ranks

        The ranks method is an alternative to the scores method. For a Match between n teams, the return list contains the values 1,...,n.
        The higher the score of a team, the lower the value in the return list.

        Returns
        -------
        List[int]
            The rank of each team. 

        Raises
        ------
        RuntimeError
            This method can only be called when the match has been played and assigned a score.
        """
        if not self.__scores:
            msg = "Undefined ranks. The match has not yet been assigned a score."
            raise RuntimeError(msg)
            # !!! What is the covention when multiple teams have the same score, are tied ?
        return [len([other for other in self.__scores if other > value]) + 1 for value in self.__scores]

    # --- user interface --- #
    def live(self) -> bool:
        """Getter method for the match status

        A live match is a match that has not yet been assigned an outcome/result.

        Returns
        -------
        bool
            True if the match has yet to be played. False if the match has a scores assigned.
        """
        return True if self.__scores is None else False

    # --- internal mechanism --- #
    def __set_result(self, result: Score):
        # bunch of errors to raise
        if self.__scores is not None:
            msg = f'Attempt to assign a score to a game that has already one {self}'
            raise RuntimeError(msg)
        if not isinstance(result, list):
            msg = f"result must be instance of List[float], received {type(result)}"
            raise TypeError(msg)
        if not isinstance(result[0], float):
            msg = f'result must be instance of List[float], received List[{type(result[0])}]'
            raise TypeError(msg)
        if len(result) != len(self._Match__teams):
            msg = f"""result lenght does not match number of teams,
                    len(result) == {len(result)}, excepted: {len(self._Match__teams)}"""
            raise ValueError(msg)

        # actual result assignement
        self.__scores = result

        # player may track match history
        if self.__tracking:
            self.__update_players_history()

    def __update_players_history(self):
        for player in self.players():
            try:
                player.add_game(self)
            except AttributeError:
                pass  # ??? raise warning

    # --- magic methods --- #
    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{type(self)} - teams: {self.__teams}, scores: {self.__scores}"

    def __contains__(self, player: SPlayer) -> bool:
        return player in self.players()


class Duel(Match):
    def __init__(self, player1: SPlayer, player2: SPlayer, tracking: Optional[bool] = None) -> None:
        """Duel class

        Duel is a special type of :class:`rstt.game.match.Match` with only two teams each consisiting of one player.
        In other words, two players facing each others.

        Parameters
        ----------
        player1 : SPlayer
            A player considered at 'home'.
        player2 : SPlayer
            A player considered as 'visitor'
        tracking : bool, optional
            If true, the duel will try to add itself (once it has been assigned a score) to the both player's game history, by default None.
        """
        tracking = tracking if tracking is not None else cfg.DUEL_HISTORY
        super().__init__(teams=[[player1], [player2]], tracking=tracking)

    # --- getter --- #
    def player1(self) -> SPlayer:
        """Getter method for player 1

        Player1 can also be refer has the one playing at 'home'.

        Returns
        -------
        SPlayer
            the first player of the duel.
        """
        return self._Match__teams[0][0]

    def player2(self) -> SPlayer:
        """Getter method for palyer 2

        Player2 - the opponent of player1 - can also be refered as 'visitor' or playing 'away'.

        Returns
        -------
        SPlayer
            the 2nd player of the duel.
        """
        return self._Match__teams[1][0]

    def opponent(self, player: SPlayer) -> SPlayer:
        """Getter method for the opponent of a player in a duel

        Suger method that returns the same value has :func:`rstt.game.match.Match.opponents`, but grammatically more correct has there is only one opponent in a duel.

        Parameters
        ----------
        player : SPlayer
            A player to get the opponent.

        Returns
        -------
        Splayer
            The opponent of the parameter player.

        Raises:
        -------
        KeyError
            When the parameter player is not a participant of the duel.
        """
        players = set(self.players())
        # this can raise a KeyError, which is what we want
        players.remove(player)
        return list(players)[0]

    def winner(self) -> SPlayer:
        """Getter method for the winner of the duel

        In a direct confrontation between two competitors, there is usually a winner (the one with the highest score, lowest rank) and a loser.

        Returns
        -------
        SPlayer
           The winner of the duel. Can be None if the duel has not yet been played or in the case of a draw.
        """
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[0][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[1][0]
        else:
            return None
        # return self._Match__teams[0][0] if self._Match__scores[0] > self._Match__scores[1] else self._Match__teams[1][0]

    def loser(self) -> SPlayer:
        """Getter method for the loser of the duel

        The loser is the player with the lowest score value, highest rank.

        Returns
        -------
        SPlayer
            The loser of the duel. Can be None if the duel has not yet been played or in the case of a draw.
        """
        if not self._Match__scores:
            return None
        if self._Match__scores[0] > self._Match__scores[1]:
            return self._Match__teams[1][0]
        elif self._Match__scores[0] < self._Match__scores[1]:
            return self._Match__teams[0][0]
        else:
            return None
        # return self._Match__teams[0][0] if self._Match__scores[1] > self._Match__scores[0] else self._Match__teams[1][0]

    def isdraw(self) -> bool:
        """Getter method indicating a draw

        A draw is a match where both player have the same scores, ranks.   

        Returns
        -------
        bool
            True if both player have the same score, in that case the :func:`rstt.game.match.Duel.winner` and :func:`rstt.game.match.Match.loser` return None.
            False if the duel has a winner and a loser.
        """
        if not self._Match__scores:
            return False
        return True if self._Match__scores[0] == self._Match__scores[1] else False
