<div align="center">
<h1>RSTT</h1>

[![MIT License](https://img.shields.io/badge/license-MIT-lightgrey)](https://github.com/Ematrion/rstt/blob/main/LICENSE) [![PyPI - Types](https://img.shields.io/pypi/types/RSTT)](https://pypi.org/project/rstt/) [![Documentation Status](https://readthedocs.org/projects/rstt/badge/?version=latest)](https://rstt.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/github/Ematrion/rstt/graph/badge.svg?token=GY15EY4OTZ)](https://codecov.io/github/Ematrion/rstt) [![RSTT Discord](https://img.shields.io/discord/1354379146221981777?color=blue&label=Discord&logo=discord)](https://discord.gg/m8gN4UgHZ3) [![DOI](https://zenodo.org/badge/929746523.svg)](https://zenodo.org/badge/latestdoi/929746523)
</div>

**Simulation Framework for Tournament and Ranking in Competition**


- ⚠️ ALPHA version. Package still under construction. Feature suggestions are welcomed.
- 💡 Design for simulation based research
- 💽 Production of large synthetic dataset
- 💻 Automated simulation workflow
- 📃 Document model by referercing class sources
- 📈 Enhance Analysis by comparing trained models to simulation models.
- 🔧 Design and integrate custom components
- ❓ Support and advise on [Discord](https://discord.gg/CzjPzdzY)


## Installation

The package is available on PyPi. To install, run

```
pip install rstt
```

User [Documentation](https://rstt.readthedocs.io/en/latest/) is available on readthedocs.


## Description

RSTT stands for Ranking Simulation Testing Tool.

The package provides everything needed to simulate competition and generate synthetic match dataset.
It contains ranking implementation (such as Elo and Glicko ...), popular tournament format (Single elimination bracket, round robin, ...), many versus many game mode with automated outcome (score/result) generation methods. Additionaly different player model are available, including time varing strenght.

It is a framework, letting user developp and intergrate with ease their own models to test.

## Getting Started

### Code Example

```python
from rstt import Player, BTRanking, LogSolver, BasicElo
from rstt import SingleEliminationBracket

# some player
population = Player.create(nb=16)

# a ranking to infer player's skills.
elo = BasicElo(name='Elo Ranking', players=population)

# display the ranking to the standard output
elo.plot()

# create a competition - the solver param specify how match outcome are generated
tournament = SingleEliminationBracket(name='RSTT World Cup 2024', seeding=elo, solver=LogSolver())

# register player, unranked partcipants get assigned lower seeds.
tournament.registration(population)

# play the tournament - the magic happens!
tournament.run()

# update ranking based on games played
elo.update(games=tournament.games())

# display the updated ranking
elo.plot()

# The LogSolver implies a 'Consensus' Ranking based on 'the real level' of players.
truth = BTRanking(name='Consensus Ranking', players=population)
truth.plot()
```

### Simulation Based Research

RSTT is meant for science and simulation based research in the context of competition.
Whenever possible code is based on peer reviewed publication and cite the sources.

The following papers are great start for journey in the field:

- [Anu Maria](https://dl.acm.org/doi/pdf/10.1145/268437.268440) [[1]](#1), covers steps to follow and pitfalls to avoid in simulation based research.
- [D. Aldous](https://www.stat.berkeley.edu/~aldous/Papers/me-Elo-SS.pdf) [[2]](#2) presents base models in the context of sport competition and introduce research questions. Several features of RSTT are based on it.
- [S. Tang & Cie](https://arxiv.org/pdf/2502.10985) [[3]](#3) Is a recent example of reseach. It uses synthetic dataset to provide insight about observations in real game data set.


### Tutorial

The tutorials contains a collections of topic to about RSTT usages.

1) [The basics](tutorials/1_Basics/1_Basics.ipynb) illustrate common fonctionnalities and 
2) [Integreation](tutorials/2_Intergration/2_Integration.ipynb). You can use use extermaly defined rating system in RSTT. We provide an example for with [openskill](https://github.com/vivekjoshy/openskill.py). It can easly be extended to [trueskill](https://trueskill.org).
3) Simulation based research should not be code dependant, rather model dependant. [tutrial_3](tutorials/3_Research_Reproduction) propose a reproduction of [A Krifa & Cie](https://hal.science/hal-03286065/document) [[4]](#4). There is an exercises version where you code part of the experiments, and a solutions one that runs most of the research report.


Soon Available:
4) [Modeling](). You can extend and developp your own model and integrate them well into simulation.  We model a professional video game ecosystem from ranking specfifcation to leagues structures with international events.


### Package Concept

The rstt package is build on 5 fundamental abstractions:
- Player: who participate in games and are items in rankings. Different models are available including ones with 'time varying skills'
- Match: which represent more the notion of an encounter than a game title with rules. It contains players grouped in teams to which a Score (the outcome) is assigned once.
- Solver: Protocol that assign a score to a game instance. Usually implements probabilistic model based on player level. 
- Scheduler: Automated game generator procedure. Matchmaking and Competition are scheduler. The package provides standards like elimination bracket and round robin variations.
- Ranking: Composed of a standing, a rating system, an inference method and a data update procedure, rankings estimate skill value of player.


Regarding ranking's component. 
- Standing: is an hybrid container that implement a triplet relationship between (rank: int, player: Player, point: float) and behave similar to a List[Player ], Dict[Player, rank] and Dict[rank, Player]
- RatingSystem: store rating computed by ranking for player
- Inference: in charge of statistical inference.
- Observer: manage the workflow from the observation that triggers the update of a ranking to the new computed ratings of players.

## Community
Join our [Discord](https://discord.gg/m8gN4UgHZ3) and exchange with us.

## How to cite
You can cite rstt with DOI 10.5281/zenodo.16926605. Also consider linking the repo.

## Source
<a id="1">[1]</a> 
Anu Maria. (1997).
Introduction to modeling and simulation.
In Proceedings of the 29th conference on Winter simulation (WSC '97). IEEE Computer Society, USA, 7–13.
https://doi.org/10.1145/268437.268440

<a id="2">[2]</a> 
Aldous, D. (2017).
Elo ratings and the sports model: A neglected topic in applied probability?
Statistical Science, 32(4):616–629, 2017.
https://www.stat.berkeley.edu/~aldous/Papers/me-Elo-SS.pdf

<a id="3">[3]</a>
Tang, S., Wang, Y., & Jin, C. (2025).
Is Elo Rating Reliable? A Study Under Model Misspecification.
arXiv preprint arXiv:2502.10985.
https://arxiv.org/pdf/2502.10985

<a id="4">[4]</a>
Adrien Krifa, Florian Spinelli, Stéphane Junca.
On the convergence of the Elo rating system for a Bernoulli model and round-robin tournaments.
[Research Report] Université Côte D’Azur. 2021. ⟨hal-03286065⟩.
https://hal.science/hal-03286065/document