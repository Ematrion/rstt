from rstt import Player, BTRanking, LogSolver, BasicElo
from rstt import SingleEliminationBracket

# some player
population = Player.create(nb=16)

# a ranking
elo = BasicElo(name='Elo Ranking', players=population)

# display the ranking to the standard output
elo.plot()

# create a competition with elo ranking for seedings.
tournament = SingleEliminationBracket(name='RSTT World Cup 2024',
                                      seeding=elo,
                                      solver=LogSolver())

# register player - unranked partcipants get assigned lower seeds
tournament.registration(population)

# play the tournament
tournament.run()

# update the ranking based on the game played
elo.update(games=tournament.games())

# display the updated ranking
elo.plot()

# Using the LogSolver implies a 'Consensus' Ranking based on 'the real level' of players.
truth = BTRanking(name='Consensus Ranking', players=population)
truth.plot()