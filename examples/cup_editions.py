from rstt import Player, BTRanking
from rstt import SingleEliminationBracket as SEB
from rstt import DoubleEliminationBracket as DEB
from rstt import Snake, SwissBracket, RoundRobin, SwissRound


# competitiors
players = [Player(name=f"Player_{i}", level=i*100) for i in range(16)]
ranking = BTRanking(name="Consensus Ranking", players=players)

for cup in [Snake, SEB, DEB, SwissBracket, RoundRobin, SwissRound]:
    event = cup(name=f"{cup.__name__}", seeding=ranking)
    print(event.name())
    
    event.registration(players)
    event.run()

    print("Match results")
    for game in event.games():
        print(game)

    print("Standing")
    for k, v in event.standing().items():
        print(k, v)
        
    print('-------------\n')
