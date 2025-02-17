from rstt import Player, BTRanking
from rstt.scheduler.tournament.knockout import SingleEliminationBracket as SEB


# competitiors
players = [Player(name=f"Player_{i}", level=i*100) for i in range(8)]
ranking = BTRanking(name="Consensus Ranking", players=players)

# snake cup
cup = SEB(name="Snake Cup Example", seeding=ranking)
cup.registration(players)
cup.run()

print("Match results")
for game in cup.games():
    print(game)

print("Standing")
for k, v in cup.standing.items():
    print(k, v)
