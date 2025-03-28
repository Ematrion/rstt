<div align="center">
<h1>RSTT</h1>

[![MIT License](https://img.shields.io/badge/license-MIT-lightgrey)](https://github.com/Ematrion/rstt/blob/main/LICENSE) [![PyPI - Types](https://img.shields.io/pypi/types/RSTT)](https://pypi.org/project/rstt/) [![Documentation Status](https://readthedocs.org/projects/rstt/badge/?version=latest)](https://rstt.readthedocs.io/en/latest/?badge=latest) [![Awpy Discord](https://img.shields.io/discord/1354379146221981777?color=blue&label=Discord&logo=discord)](https://discord.gg/CyB3Ptf3) 
</div>

**Simulation Framework for Tournament and Ranking in Competition**


- :warning: ALPHA version. Package still under construction. Do not hesitate to suggest features addition
- :bulb: Design for simulation based research
- :minidisc: Production of large synthetic dataset
- :computer: Automated simulation workflow
- :page_with_curl: Document your model by referercing class sources
- :chart_with_upwards_trend: Enhance Analysis by comparing trained models to simulation models. 
- :wrench: Design and integrate your own custom components
- :question: Support and advise on [Discord](https://discord.gg/CyB3Ptf3) 


## Installation

The package is available on PyPi. To install, run

```
pip install rstt
```

User [Documentation](https://rstt.readthedocs.io/en/latest/) is available on readthedocs.


## Description

The package is meant for science and simulation based research in the context of competition.
Whenever possible code is based on peer reviewed publication and cite the sources.

This package provides everything needed to simulate competition and generate synthetic match dataset.
It contains ranking implementation (such as Elo and Glicko ...), popular tournament format (Single elimination bracket, round robin, ...), many versus many game mode with automated outcome (score/result) generation methods. Additionaly different player model are available, including time varing strenght.

RSTT is a framework, letting user developp and intergrate with ease their own models to test.

## Getting Started

#### Basic package example

```python
from rstt import Player, BTRanking, LogSolver, BasicElo
from rstt import SingleEliminationBracket

# some player
population = Player.create(nb=16)

# a ranking
elo = BasicElo(name='Elo Ranking', players=population)

# display the ranking to the standard output
elo.plot()

# create a competition - we specify to use the elo ranking for seedings and the LogSolver to produce match outcome.
tournament = SingleEliminationBracket(name='RSTT World Cup 2024', seeding=elo, solver=LogSolver())

# register player (the seedings do not define the participants) unranked partcipants get assigned lower seeds.
tournament.registration(population)

# play the tournament - this triggers a bunch of stuff, including game generation and a the production of a final standing.
tournament.run()

# update ranking based on games played
elo.update(games=tournament.games())

# display the updated ranking
elo.plot()

# Using the LogSolver implies a 'Consensus' Ranking based on 'the real level' of players.
truth = BTRanking(name='Consensus Ranking', players=population)
truth.plot()
```


#### Package Concept

The rstt package is build on 5 fundamental abstraction:
- Player: who participate in games and are items in rankings. Different models are available including ones with 'time varying skills'
- Match: which represent more the notion of an encounter than a game title with rules. It contains players grouped in teams to which a Score (the outcome) is assigned once.
- Solver: Protocol with a solve(Match) that assign a score to a game instance. Usually implements probabilistic model based on player level. 
- Scheduler: Automated game generator protocol. Matchmaking and Competition are scheduler, the package includes standards like elimination bracket and round robin variations..
- Ranking: Implmeneted as a tuple (standing, rating system, inference method, observer) that estimate a skill value (or point) for player.


Regarding ranking's component. 
- Standing: is an hybrid container that implement a triplet relationship between (rank: int, player: Player, point: float) and behave like a List[Player ], Dict[Player, rank] and Dict[rank, Player]
- RatingSystem: store data computed by ranking for player
- Inferer: in charge of statistical inference and provide a rate() method.
- Observer: manage the workflow from the observation that triggers the update of a ranking to the new computed ratings of players.


#### Simulation Based Research

The package is meant to enable research question and research in the field of competition.

If you are interested, but unfamiliar with simulation approach you can refer to Anu Maria's [paper](https://dl.acm.org/doi/10.1145/268437.268440) [[1]](#1). It covers steps to follow and pitfalls to avoid. 

If you are interested in what and how research can be conducted specificaly in the context of this package, the


## Community


## How to cite pyosPackage


## Source
<a id="1">[1]</a> 
Anu Maria. (1997).
Introduction to modeling and simulation.
In Proceedings of the 29th conference on Winter simulation (WSC '97). IEEE Computer Society, USA, 7–13. https://doi.org/10.1145/268437.268440

<a id="2">[2]</a> 
Aldous, D. (2017).
Elo ratings and the sports model: A neglected topic in applied probability?
Statistical Science, 32(4):616–629, 2017.

<a id="3">[3]</a>
Tang, S., Wang, Y., & Jin, C. (2025).
Is Elo Rating Reliable? A Study Under Model Misspecification.
arXiv preprint arXiv:2502.10985.

<a id="4">[4]</a>
Adrien Krifa, Florian Spinelli, Stéphane Junca.
On the convergence of the Elo rating system for a Bernoulli model and round-robin tournaments.
[Research Report] Université Côte D’Azur. 2021. ⟨hal-03286065⟩ (https://hal.science/hal-03286065v1/file/Elo%20M1%20IM%20hal.pdf).