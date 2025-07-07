from typing import Union, List, Set, Dict, Optional
from typeguard import typechecked
import abc

from rstt import Duel, BetterWin
from rstt.stypes import SPlayer, Solver, Achievement
from rstt.ranking.ranking import Ranking
import rstt.utils.utils as uu

from collections import defaultdict


import warnings


class Competition(metaclass=abc.ABCMeta):
    '''
        NOTE: In the future the competition class could evolve.
            - inherit from a Scheduler class
            - composition over inheritance:
                * PlayerManager -> dealing with seedings or ratings
                * GameManager -> dealing with Match types and matching
                * EventManager -> dealing with the event id, achivements of players, final standing
    '''
    @typechecked
    def __init__(self, name: str,
                 seeding: Ranking,
                 solver: Solver = BetterWin(),
                 cashprize: Optional[dict[int, float]] = None):
        """Tournament General Template & Workflow.

        Abstract class handling specificity related to Competition.

        In rstt Competition are 'Scheduler bounded in time and space'.
        Unlike live matchmaking, it has a start, an end and a finite well defined amount of participants.

        Competition generate automatically matches in a coehrent, meaningfull fashion.


        Parameters
        ----------
        name : str
            A unique name to identify the Event.
        seeding : Ranking
            A ranking used for `seeding <https://en.wikipedia.org/wiki/Seeding_(sports)>`_ purposes.
        solver : Solver, optional
            A Solver to generate match outcomes, by default BetterWin()
        cashprize : Optional[Dict[int, float]], optional
            A 'prizepool' rewarding player with 'money' for their success (placement in the final standing) during the Event, by default None

        .. attention:: 0.6.5 [attribute changes]
            the 'participants' attribute has been encapsulated, use the corresponding get method to access it.
            Reminder that to 'set' participants you can use the registration method.
        """

        # 'settings'
        self.__name = name
        self._participants = []
        self.seeding = seeding
        self.solver = solver
        self.cashprize = defaultdict(lambda: 0)
        if cashprize:
            self.cashprize.update(cashprize)

        # result related variable
        self.played_matches = []
        self.__standing = {}

        # control variable
        self.__started = False
        self.__finished = False
        self.__closed = False

        # version 0.6.5 to remove in remove in 0.7
        msg = "Pseudo-encapsulation of participants: '\n'Competition.participants attribute has been moved to ._participants. Competitors.participants() is now a getter method"
        warnings.warn(msg, DeprecationWarning)

    # --- getter --- #

    def name(self) -> str:
        """Getter for the name of the Competition

        Returns
        -------
        str
            the name of the competition (used as identifier in the package)
        """
        return self.__name

    def participants(self) -> list[SPlayer]:
        """Getter for SPlayer taking part in the Competition

        Returns
        -------
        list[SPlayer]
            competitors playing game(s).
        """
        return self._participants

    def started(self) -> bool:
        """Indicate if the competition started

        Once a competition has started, calls on registration() and start() methods will have no effects.

        Returns
        -------
        bool
            wheter the competition has started or not
        """
        return self.__started

    def live(self) -> bool:
        """Indicate if a competition is being played

        It means that games are being played and generated.
        Almost no operations are possible when live.

        Returns
        -------
        bool
            True if competition is curretnly generating and playing matches.
        """
        return self.__started and not self.__finished

    def over(self) -> bool:
        """Indicate that the competition has ended

        When over, it means all games were played and player's have collected their achievements.

        Returns
        -------
        bool
            True if the competition is over, no more game will be played, the standing is final
        """
        return self.__closed

    def standing(self) -> Dict[SPlayer, int]:
        """Getter for the standing

        The standing of a competition indicate where player have finished.

        Returns
        -------
        Dict[SPlayer, int]
            Final standing of the event
        """
        # ??? raise error/warnings if not finished
        return self.__standing

    @typechecked
    def games(self, by_rounds=False) -> Union[List[Duel], List[List[Duel]]]:
        """Getter for all matches played during the event.

        In many Competition, matches are organized in 'rounds' and follow a chronological order.
        This method support two query with a return values respecting or not the round structure
        Parameters
        ----------
        by_rounds : bool, optional
            Wether to return the matches grouped by rounds or not, by default False and a flat list is returned.

        Returns
        -------
        Union[List[Duel], List[List[Duel]]]
            All matches played during the event.
        """
        # ??? raise error/warnings if not finished
        return self.played_matches if by_rounds else uu.flatten(self.played_matches)

    @typechecked
    def top(self, place: Optional[int] = None) -> Union[Dict[int, List[SPlayer]], List[SPlayer]]:
        """Getter for players by their final placement

        Sugar method to access a player by his placement rather than dealing with a the standing.

        Parameters
        ----------
        place : Optional[int], optional
            The place that you want to know which player(s) ended at, by default None.
            If None, the return value is a Dictionary where keys are int and values list of players that finished at the 'key place'.

        Returns
        -------
        Union[Dict[int, List[SPlayer]], List[SPlayer]]
            Either a list of player placed at the 'place' position in the standing, or a full dictionary with all places as key.
        """
        # ??? raise error/warnings if not finshed
        if place:
            return [key for key, value in self.__standing.items() if value == place]
        else:
            return {v: [key for key, value in self.__standing.items() if value == place] for v in self.__standing.values()}

    # --- general mechanism --- #
    @typechecked
    def registration(self, players: Union[SPlayer, List[SPlayer], Set[SPlayer]]):
        """Add player to compete

        The seedings do not define who participate in the event. You need to call registration to specify who plays.
        The method can be called anytime you want before the start of competition, but should not be called afterwards.
        A player can only participate once but multiple registration will have no effect for the said player.
        Unranked player will receive a seed corresponding to the default value - *NOT ALWAYS* lower seed.
        Unseeded player *WILL NOT* be added to the ranking.

        Parameters
        ----------
        players : Union[SPlayer, List[SPlayer], Set[SPlayer]]
            Playrs taking part in the event's matches.
        """
        if not self.__started:
            playerset = set(self._participants)
            playerset.update(players)
            self._participants = list(playerset)

    def run(self):
        """Automated Competition execution

        This is the magic methods that does all the works.

        A Diagram will be added to the doc to illustrate the process better than words.

        Raises
        ------
        RuntimeError
            An error is raised if the competition is not in a suited state, if it has already started.
        """

        # ??? Can we extend .run for competiton that have been 'manually partially runed'
        if self.__started:
            msg = f"Can not run an event that has already started. Did you mean to use play() or perhaps did you wrongly call start()?"
            raise RuntimeError(msg)
        else:
            self.start()
            self.play()
            self.trophies()

    def start(self):
        """Starts the competition

        Do not use if you simply want to run the competition
        """
        if not self.__started:
            self.seeding = self.seeding.fit(self._participants)
            self._initialise()
            self.__started = True

    def play(self):
        """Plays the competition

        Do not use if you simply want to run the competition.

        Raises
        ------
        RuntimeError
            An error is raised if the competition is not in a suited state, if it has not started yet.
        """
        if not self.__started:
            msg = f"Can not play an event that has not yet started. Did you mean to use .run() or perhaps did you forgot to call .start() first?"
            raise RuntimeError(msg)
        while not self.__finished:
            current_round = self.generate_games()
            results = self.play_games(current_round)
            self.edit(results)

    def play_games(self, games: List[Duel]) -> List[Duel]:
        """Assign scores to generated matches

        Do not use if you simply want to run the competition.

        Parameters
        ----------
        games : List[Duel]
            Unplayed/unsolved matches to assign a score to.

        Returns
        -------
        List[Duel]
            the games with a scored.
        """
        played = []
        for game in games:
            self.solver.solve(game)
            played.append(game)
        return played

    def edit(self, games: List[Duel]):
        """Handles competition state after each round

        Do not use if you simply want to run the competition.

        Parameters
        ----------
        games : List[Duel]
            The game splayed during the round.

        Returns
        -------
        bool
            If True the round was the last one, no more game will be played and the competition will end.
        """
        self.played_matches.append(games)
        self._update()
        self.__finished = self._end_of_stage()

    def trophies(self):
        """Closure ceremony

        Establish the final standing and reward players with their respective :class:`rstt.stypes.Achievement`.

        Do not use if you simply want to run the competition.
        """
        self.__standing = self._standing()
        for player in self._participants:
            try:
                result = Achievement(
                    self.__name, self.__standing[player], self.cashprize[self.__standing[player]])
                player.collect(result)
            except AttributeError:
                continue
        self.__closed = True

    # --- subclass specificity --- #
    def _initialise(self) -> None:
        '''Function called once, after seedings computation but before any game is played.'''

    def _update(self) -> None:
        '''This function is called at the end of every 'rounds', after the game have been stored, but before checking the competition end condition.'''

    @abc.abstractmethod
    def _end_of_stage(self) -> bool:
        '''Test if the competition should stop.'''

    @abc.abstractmethod
    def _standing(self) -> Dict[SPlayer, int]:
        '''Function called once after every game is played. Builds the final standing of the event'''

    @abc.abstractmethod
    def generate_games(self) -> List[Duel]:
        '''Function called every 'round' to generate games. Should return games WITHOUT scores assigned'''
