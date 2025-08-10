.. RSTT documentation master file, created by
   sphinx-quickstart on Tue Mar 18 10:03:34 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


==================
RSTT Documentation
==================

**Ranking Simulation Testing Tool**

The package provides everything needed to simulate competition and generate synthetic match dataset.
It contains ranking implementation (such as Elo and Glicko), popular tournament format (Single elimination bracket, round robin), many versus many game mode with automated outcome (score/result) generation methods.
Additionaly different player model are available, including time varing strenght.

It is a framework, letting user developp and intergrate with ease their own models to test.


First Steps
===========

.. toctree::
   :caption: First steps
   :hidden:

   install
   usage
   tutorials

:doc:`install`
   Get RSTT

:doc:`usage`
   A Simple example gives you a good overview of what the package has to offers.

:doc:`tutorials`
   Selection of notebook


Tutorials
=========

.. toctree::
   :caption: Tutorials
   :hidden:


   Here is a collections of notebooks that helps learning the package functionnalities.

   tutorials/basic
   tutorials/integration
   tutorials/elo


:doc:`tutorials/basic`
   RSTT fundamentals, from concepts to user interfaces

:doc:`tutorials/integration`
   Run simulation with externally defined rating system

:doc:`tutorials/elo`
   A Complete research redo in RSTT



Concepts
========

The rstt package is build on 5 fundamental abstractions:
* Player: who participate in games and are items in rankings. Different models are available including ones with 'time varying skills'.
* Match: which represent more the notion of an encounter than a game title with rules. It contains players grouped in teams to which a Score (the outcome) is assigned once.
* Solver: Protocol that assign a score to a game instance. Usually implements probabilistic model based on player level. 
* Scheduler: Automated game generator procedure. Matchmaking and Competition are scheduler. The package provides standards like elimination bracket and round robin variations.
* Ranking: Composed of a standing, a rating system, an inference method and a data update procedure, rankings estimate skill value of player.


Regarding ranking's component. 
* Standing: is an hybrid container that implement a triplet relationship between (rank: int, player: Player, point: float) and behave similar to a List[Player ], Dict[Player, rank] and Dict[rank, Player]
* RatingSystem: store rating computed by ranking for player
* Inference: in charge of statistical inference.
* Observer: manage the workflow from the observation that triggers the update of a ranking to the new computed ratings of players.



.. toctree::
   :caption: Table of Contents:

   tutorials
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
