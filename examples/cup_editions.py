from rstt import Player, BTRanking
from rstt.scheduler.tournament.knockout import SingleEliminationBracket as SEB
from rstt.scheduler.tournament.knockout import DoubleEliminationBracket as DEB
from rstt.scheduler.tournament.snake import Snake
from rstt.scheduler.tournament.swissbracket import SwissBracket



# competitiors
players = [Player(name=f"Player_{i}", level=i*100) for i in range(16)]
ranking = BTRanking(name="Consensus Ranking", players=players)

for cup in [Snake, SEB, DEB, SwissBracket]:
    event = cup(name=f"{cup.__name__}", seeding=ranking)
    event.registration(players)
    event.run()

    print(event.name)
    print("Match results")
    for game in event.games():
        print(game)

    print("Standing")
    for k, v in event.standing.items():
        print(k, v)
        
    print('-------------\n')
