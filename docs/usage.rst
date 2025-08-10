.. _usage:

===================
Intuitive Interface
===================


Components options are available at the package top level.
.. code-block:: python
    :linenos:

    from rstt import Player, BasicElo
    from rstt import SingleEliminationBracket, LogSolver


Instaciate large number of players and track them in a ranking.
.. code-block:: python
    :linenos:

    # some player
    population = Player.create(nb=16)

    # a ranking
    elo = BasicElo(name='Elo Ranking', players=population)

    # display the ranking to the standard output
    elo.plot()



Automatic game generation with seedings and probabilistic game outcome in few steps.
.. code-block:: python
    :linenos:

    # create a competition with elo ranking for seedings.
    tournament = SingleEliminationBracket(name='RSTT World Cup 2024',
                                        seeding=elo,
                                        solver=LogSolver())

    # register player - unranked partcipants get assigned lower seeds
    tournament.registration(population)

    # play the tournament
    tournament.run()


Intuitive ranking
.. code-block:: python
    :linenos:

    # update the ranking based on the game played
    elo.update(games=tournament.games())

    # display the updated ranking
    elo.plot()



Compare 'trained' ranking wiht 'model' ranking
.. code-block:: python
    :linenos:
    
    # Using the LogSolver implies a 'Consensus' Ranking based on 'the real level' of players.
    from rstt import BTRanking
    truth = BTRanking(name='Consensus Ranking', players=population)
    truth.plot()



Code Execution Explanation
==========================

When multiple playesr are created at once, each gets a random name and a random level.
In a ranking, player are mapped to a default rating and corresponding rank. The rank of a player is computed with an internal ordinal method that converts rating into float - the value dsiplayed in the standard output.
Ranking in rstt are automaticaly sorted whenever a get/set operation is performed, this include update() calls. You do not need to worry about it.

A competition instanciation needs a seeding, which helps deciding how participants are paired.
The seeding gives no indication about which player should play, there is a dedicated register method for that purpose.

The tournament.run() triggers an entire workflows that involve a matching logic (specific to the class) and  a solver to generate game results.

Once a tournament is completed, its results can be used to update a ranking. For example a Elo ratings use the games results.

The benefit of simulation is that there is a known probabilistic model inherent to the data production. The BTRanking is a special ranking where the rating of the player is their level.
It serves as a practical reference for trained system.