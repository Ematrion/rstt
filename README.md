# RSTT

ALPHA STATE - usable but frequent changes

Rstt stands for Ranking Simulation Testing Tool. 
A package to test how ranking and seedings of players, behave regarding different format of competitions.
It has features to closely study interaction between ranking design, matchmaking algorithm and competitiors models.

The goal is to offer an inituitive syntax to build complex simulation that output syntethetic dataset for analysis.
The package has been designed with modularity and inheritance in mind. Users should be able to build upon the package and intergrete their own ranking, matchmaking or player models with ease. 


### Installation
The package is available on PyPi

### Concept

The rstt package is build on 5 fundamental abstraction:
- Player: who participate in games and are items in rankings

- Match: which represent more the notion of an event than a physical game. It is a container for player to which a Score is assigned only once.

- Solver: Protocol with  a solve(Game) that assign a score to a game instance. Usually implements probabilistic model based on player level. 

- Competition: Automated game generator protocol

- Ranking: Ranking is a tuple (standing, rating system, inference method, observer) that estimate a skill value (or point) for player.


The following concepts are directly related to the notion of Ranking. There are of interest only if you work on ranking design rather than ranking performances and properties.
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

