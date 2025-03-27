<div align="center">
<h1>RSTT</h1>

[![MIT License](https://img.shields.io/badge/license-MIT-lightgrey)](https://github.com/Ematrion/rstt/blob/main/LICENSE) ![PyPI - Types](https://img.shields.io/pypi/types/RSTT) [![Documentation Status](https://readthedocs.org/projects/rstt/badge/?version=latest)](https://rstt.readthedocs.io/en/latest/?badge=latest) [![Awpy Discord](https://img.shields.io/discord/1354379146221981777?color=blue&label=Discord&logo=discord)](https://discord.gg/CyB3Ptf3) 
</div>

**Simulation Framework for Tournament and Ranking in Competition**


- :warning: ALPHA version. Package still under construction. Do not hesitate to suggest features addition
- :bulb: Design for simulation based research
- :minidisc: Production of large synthetic dataset
- :computer: Automated simulation workflow
- :page_with_curl: Document your model by referercing class sources
- :chart_with_upwards_trend: Enhance Analysis by comparing trained models to simulation models. 
- :wrench: Design and integrate your own custom componen
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

## Code Examples




## Concept

The rstt package is build on 5 fundamental abstraction:
- Player: who participate in games and are items in rankings

- Match: which represent more the notion of an event than a physical game. It is a container for player to which a Score is assigned only once.

- Solver: Protocol with  a solve(Game) that assign a score to a game instance. Usually implements probabilistic model based on player level. 

- Competition: Automated game generator protocol

- Ranking: Ranking is a tuple (standing, rating system, inference method, observer) that estimate a skill value (or point) for player.


The following concepts are directly related to the notion of Ranking. There are of interest if you intend to use the package for ranking design or comparative studies.
- Standing: is an hybrid container that implement a triplet relationship between (rank, player, point) and behave like a List[Player], Dict[Player, rank] and Dict[rank, Player]. 

- RatingSystem: store data computed by ranking for player

- Inferer: in charge of statistical inference, implement a rate([ratings], [Score]) -> [ratings] method

- Observer: manage the workflow between the observation that triggers the update of a ranking to the new computed ratings of involved players while maintaining the players rank in the Standing.


### Basic code example

'first_simulation.py' in the examples folder provide a small piece of code involving all the different notion of the package.
For people interested in making their own ranking algorithm run in rstt simulation (or design with the package), we recommand to take a look at the source code of 'BasicOS' in 'src/ranking/standard.py' file. It is a class wrapping the openskill package to fit the ranking interface of rstt.


### Repository Structure

- rstt: Contains the package source code. The package is in a usable state. It still contains bugs.
Problematic coding styles. The competitions.py module should be refactor and its classes should be written in the scheduler.tournaments.py module and respecting its cnew oncepts. Same goes for the solver.py module. 

- test: contains pytest code for maintaining src. It has problematic coding style and does not cover the entire package.

- examples: contains notebook illustrating fundamentals of the rstt package. I believe it is in a decent state. The Standing notebook does introduce the notion of ranking but does not realy show all its functionality.
There is no illustration for devellopers on how to extends the rstt concepts.

