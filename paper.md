---
title: 'RSTT: A Python package to simulate competition and evaluate ranking system'
tags:
  - Python
  - Simulation
  - Synthetic data
  - Ranking
  - Rating system
  - Competition
  - Bradley-Terry model
authors:
  - name: David Bucher

date: 28 July 2025
bibliography: paper.bib
---

# Summary

Who is the best Chess player in the world ? And in Football, Hockey or Counter-Strike ?
The GOAT (Greatest Of All Time) is a debate that animate with passions bars, tv show,
schools, your work place and sometimes even an entire city or country.
Competition provides evidences by krowning champions. Ranking aims at predicting games result.

Competition and ranking dependants on and influence each others. Ranking uses data from competition.
Often tournament use ranking as seeding to match athletes against. This interplay is challenging to study since prety much any dataset has an uderlying specific structure and bias.

Diverse field have their own practices. Chess uses an Elo ranking system and  swiss-rounds or double round-robin tournaments. Domestic football league use multiple round robin and a point system as final ranking. Online matchmaking tends to relies on more complex baysian rating system and skill based matchmaking. Tennis uses a point system to rank players and single elimination brackets.


# Statement of need

`RSTT` is a package in support of simulation based research for competition. It relies on consensual probabilistic models for sport, such as `Bradley-Terry`, to generate game outcomes and famous tournament system and matching strategies to produce game encounters. It enables to study the impact of seedings and matching strategies on a system. Its high modulartiy allows externaly defined system to be wrapped and use. It is not limited to simulation and can be used to design ranking and perform test on real data set.

