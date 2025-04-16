"""Module for Observer

Observer are protocol providing a handle_observations() method for ranking.
This method is responsible:

    - to proprocess observations - parameters passed to :func:`rstt.ranking.ranking.Raning.update` justifying ratings changes.
    - properly call the ranking.backend :func:`rstt.stypes.Infere.rate`
    - store new ratings in the ranking.datamodel :class:`rstt.stypes.RatingSystem`
    
.. warning::
    Reminder, currently RSTT support SMatch format is limited to the Duel class.
    This is also true for 'Game based' Observer even. Due to modularity, type checkers look for SMatch and not for Duel
    This may cause unexpected errors in your simulations.

"""

from typeguard import typechecked
from typing import List, Dict, Union, Tuple, Any, Optional

from rstt.stypes import SMatch, SPlayer, Inference, RatingSystem, Score
import rstt.utils.utils as uu

# QUEST: Do Observer realy need to be typechecked ?


@typechecked
def assign_ratings(datamodel: RatingSystem, ratings: Dict[SPlayer, Any]):
    """Push updated ratings in the RatingSystem

    Utility function to 'push' updated ratings into the raking's datamodel.

    Parameters
    ----------
    datamodel : RatingSystem
        The datamodel of a ranking.
    ratings : Dict[SPlayer, Any]
        Updated ratings to store, usually returned values of a Inferer.rate method.

    :meta private:
    """
    for key, rating in ratings.items():
        datamodel.set(key, rating)


@typechecked
def match_data(game: SMatch, datamodel: RatingSystem) -> Tuple[List[List[SPlayer]], List[List[Any]], Score, List[int]]:
    """Extract Match infos

    Utility function to format match into suitable data.
    Return is suitable for any RSTT Game Score Based Inferer, but also for some external systems.

    Parameters
    ----------
    game : SMatch
        A match to extract information from
    datamodel : RatingSystem
        A datamodel to extract players rating's.

    Returns
    -------
    Tuple[List[List[SPlayer]], List[List[Any]], Score, List[int]]
        Collection of data as foloow:
        1. Participants: List[List[SPlayer]]
        2. Partitipants ratings in the same order: List[List[Any]]
        3. Team scores: Score
        4. Teams ranks. List[int]

    :meta private:
    """
    teams_as_players = game.teams()
    teams_as_ratings = [
        [datamodel.get(player) for player in team] for team in teams_as_players]

    if game.live():
        scores, ranks = None, None
    else:
        scores = game.scores()
        ranks = game.ranks()

    return teams_as_players, teams_as_ratings, scores, ranks


@typechecked
def players_ratings_to_dict(players: List[List[SPlayer]], ratings: List[List[Any]]) -> Dict[SPlayer, Any]:
    return {p: r for p, r in zip(uu.flatten(players), uu.flatten(ratings))}


class GameByGame:
    """Match based Observer"""
    @typechecked
    def handle_observations(self, infer: Inference,
                            datamodel: RatingSystem,
                            games: Optional[Union[SMatch,
                                                  List[SMatch]]] = None,
                            # FIXME: proper typing with Scheduler class WIP
                            event: Optional[Any] = None, *args, **kwargs):
        """Game by Game updating Procedure

        Implementing an iterative approach where each observations triggers the entire updating workflows.
        In particular, new ratings are stored inbetween of each iterations, and the prior ones are lost.

        Parameters
        ----------
        infer : Inference
            A system to compute new rating
        datamodel : RatingSystem
            A container of ratings
        games : Optional[Union[SMatch, List[SMatch]]], optional
            Observations justifying a ranking update, by default None
        event : Optional[Any], optional
            Alternative for the games parameter, must provide a games() method, by default None

        Raises
        ------
        ValueError
            Indicate an incompatible arg call, either provide 'event' or 'games' not both.
        """
        if event:
            if games:
                msg = f'Incompatible parameters, Only one of games or event must be passed'
                raise ValueError(msg)
            else:
                self.handle_observations(
                    infer=infer, datamodel=datamodel, games=event.games())
        elif isinstance(games, SMatch):
            self.single_game(infer, datamodel, games, *args, **kwargs)
        else:
            for game in games:
                self.single_game(infer, datamodel, game, *args, **kwargs)

    @typechecked
    def single_game(self, infer: Inference, datamodel: RatingSystem, game: SMatch, *args, **kwargs):
        """Implement to update workflow for a single match

        Parameters
        ----------
        infer : Inference
            A system to compute new rating
        datamodel : RatingSystem
            A container of ratings
        games : Optional[Union[SMatch, List[SMatch]]], optional
            An Observation justifying a ranking update, by default None

        :meta private:
        """
        players, ratings, score, ranks = match_data(game, datamodel)
        try:
            output = infer.rate(ratings, ranks=ranks, *args, **kwargs)
        except:
            output = infer.rate(ratings, score, *args, **kwargs)
        new_ratings = players_ratings_to_dict(players, output)
        assign_ratings(datamodel, new_ratings)


class KeyChecker:
    """Player based Observer"""

    def handle_observations(self, infer: Inference, datamodel: RatingSystem, *args, **kwargs):
        """No observation Observer

        Helps implementing Ranking in cases where an update can be justify even in the absence of tracebable triggers.
        For example, A consensus ranking for player with an evolving level.

        Additionnaly can help build Ranking based on player history:
            - Win rate based.
            - Career earnings leaderboard
            - ...

        Parameters
        ----------
        infer : Inference
            A system to compute new rating
        datamodel : RatingSystem
            A container of ratings
        """
        new_ratings = {}

        for player in datamodel.keys():
            new_ratings.update(infer.rate(player, *args, **kwargs))

        assign_ratings(datamodel, new_ratings)


class BatchGame:
    """Match Based Observer"""
    @typechecked
    def handle_observations(self, infer: Inference,
                            datamodel: RatingSystem,
                            games: Optional[Union[SMatch,
                                                  List[SMatch]]] = None,
                            # FIXME: proper typing with Scheduler class WIP
                            event: Optional[Any] = None, *args, **kwargs):
        """All Matches at once updating procedure

        Alternative to the :class:`rstt.ranking.observer.GamebyGame` observer. Some rating system, like Elo and Glicko
        support updates where all matches are considered at once for the rating update.

        In this workflows, ratings are stored after all matches have been processed. Every computation is performed using the prior ratings
        (i.e the one stored in the datamodel before the method call)

        Parameters
        ----------
        infer : Inference
            A system to compute new rating
        datamodel : RatingSystem
            A container of ratings
        games : Optional[Union[SMatch, List[SMatch]]], optional
            Observations justifying a ranking update, by default None
        event : Optional[Any], optional
            Alternative for the games parameter, must provide a games() method, by default None

        Raises
        ------
        ValueError
            Indicate an incompatible arg call, either provide 'event' or 'games' not both.
        """
        if event:
            if games:
                msg = f'Incompatible parameters, Only one of games or event must be passed'
                raise ValueError(msg)
            else:
                self.handle_observations(
                    infer=infer, datamodel=datamodel, games=event.games())
        else:
            games = self.to_list(games)
            players = self.involved_keys(games)
            new_ratings = {}
            for player in players:
                player_games = self.game_of_interest(player, games)
                ratings = [datamodel.get(game.opponent(player))
                           for game in player_games]
                scores = [self.player_score(player, game)
                          for game in player_games]
                rating = datamodel.get(player)
                new_ratings[player] = infer.rate(rating, ratings, scores)

            assign_ratings(datamodel, new_ratings)

    @typechecked
    def player_score(self, player: SPlayer, game: SMatch):
        """Exctact player score in a gievn macth

        :meta private:
        """
        if game.winner() == player:
            return 1.0
        elif game.loser() == player:
            return 0.0
        elif game.isdraw():
            return 0.5
        else:
            msg = f'Player {player} can not be asigned a score value (1.0, 0.5, 0.0) for Game {game}'
            raise ValueError(msg)

    @typechecked
    def game_of_interest(self, player: SPlayer, games: List[SMatch]) -> List[SMatch]:
        """Find all game where a given player participated in the batch

        :meta private:
        """
        return [game for game in games if player in game]

    @typechecked
    def involved_keys(self, games: List[SMatch]) -> List[SPlayer]:
        """Find all opponents of a gien player in the batch

        :meta private:
        """
        winners = [game.winner() for game in games]
        losers = [game.loser() for game in games]
        return list(set(winners+losers))

    @typechecked
    def to_list(self, games: Union[SMatch, List[SMatch]]) -> List[SMatch]:
        """input formater for the inferer.rate

        :meta private:
        """
        if not isinstance(games, list):
            games = [games]
        return games
