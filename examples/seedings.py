from rstt import Player, LogSolver, BTRanking, SingleEliminationBracket


pop = Player.create(nb=16)
pop = Player.seeded_players(16)
gt = BTRanking('Consensus', pop)

# RSTT Matching Implementation
cup1 = SingleEliminationBracket('Default Matching', gt, LogSolver())
cup1.registration(pop)
cup1.run()

for game in cup1.games():
    print(game)

for i, round in enumerate(cup1.games(by_rounds=True)):
    print(f"\n--- Round {i} ---")
    for game in round:
        print(f"{game.player1().name()} versus {game.player2().name()}")


# RSTT Accelerated Matching
top = list(range(len(pop)//2))
bottom = list(range(len(top), len(pop)))
seeds = BTRanking('ReSeeded', pop)
seeds.rerank(top+bottom[::-1])

seeds.plot()


cup2 = SingleEliminationBracket('Accelerated Matching', seeds, LogSolver())
cup2.registration(pop)
cup2.run()

for i, round in enumerate(cup2.games(by_rounds=True)):
    print(f"\n--- Round {i} ---")
    for game in round:
        print(f"{game.player1().name()} versus {game.player2().name()}")
