from rstt import Player, BTRanking


population = [Player(name=f'Player_{i}', level=i*100) for i in range(20)]
ranking = BTRanking(name='Consensus Ranking', players=population)
ranking.plot()