import rstt
import random
import numpy as np


tot = 10
players = rstt.Player.create(nb=tot)
elo1 = rstt.BasicElo(name='elo 1', players=players)
elo2 = rstt.BasicElo(name='elo 2', players=players)
elo3 = rstt.BasicElo(name='elo 3', players=players)
elo4 = rstt.BasicElo(name='elo 4', players=players)
elos = [elo1, elo2, elo3, elo4]

for p in players:
    r = random.gauss(1500, 700)
    for elo in elos:
        elo.set_rating(p, r)

elo1.plot()

permu = np.random.permutation(list(range(tot)))
permu = [int(x) for x in permu]
print(permu)

elo2.rerank(permu, name='direct', direct=True)
elo2.plot()

elo3.rerank(permu, name='indirect', direct=False)
elo3.plot()


def cycle(total):
    permutation = []
    for i in range(0, total):
        if i != total-1:
            permutation.append(i+1)
        else:
            permutation.append(0)

    return permutation


reference = {p: elo4[p] for p in elo4}
elo4.plot()
elo4.rerank(name='elo 4 direct', permutation=cycle(tot), direct=True)
elo4.plot()
elo4.rerank(name='elo 4 direct and back', permutation=cycle(tot), direct=False)
elo4.plot()
for p in elo:
    assert elo4[p] == reference[p]
