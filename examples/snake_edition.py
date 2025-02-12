from rstt import Player
from rstt.scheduler.tournament import Snake


# competitiors
players = [Player(name=f"Player_{i}", level=i*100) for i in range(25)]
print(players)

# snake cup
cup = Snake(name="Snake Cup Example", seeding=players)
cup.registration(players)
cup.run()

print("Match results")
for game in cup.games():
    print(game)

print("Standing")
for k, v in cup.standing.items():
    print(k, v)