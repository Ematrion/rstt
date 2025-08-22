RSTT Tutorial 2 - Integration
=============================

In this notebook we will use the
`openskill <https://openskill.me/en/stable/>`__ rating system with RSTT.
The goal is to wrapp model in a Ranking class to benefit from its
functionnalities and fit in simulation. We will also use model
predictions to generate games outcome.

1. RSTT Ranking Design
----------------------

A
`Ranking <https://rstt.readthedocs.io/en/latest/rstt.ranking.html#rstt.ranking.ranking.Ranking>`__
is a composition over inheritance design that contains: - A
`Standing <https://rstt.readthedocs.io/en/latest/rstt.ranking.html#rstt.ranking.standing.Standing>`__:
dict/list hybrid container. **Automaticaly sorts player** based on their
*ranking point*. - A
`RatingSystem <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.RatingSystem>`__:
dict like container that **maps player with ratings** - An
`Inference <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Inference>`__:
provides a **.rate method()** to compute ratings - An
`Observer <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Observer>`__:
provides a **.handle_observations()** method that process ranking.update
inputs.

Before integrating external system, lets start with a simple
illustration. A ranking can be instanciated with its components
specified. However, we recommand to represent a ranking design in its
own class. It makes it more clear what parameters are intresect to the
ranking design, and which are hyper-parameters.

1.1 Instanciate with Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ranking can be instanciated with its components specified. NOT
RECOMMANDED

.. code:: python

    from rstt import Ranking
    from rstt.ranking import KeyModel, Elo, GameByGame
    
    # Ambiguity between core design elements and parameters. Is the handler a tunable parameter of the ranking?
    Ranking(name='elo', datamodel=KeyModel(default=1000), backend=Elo(k=20), handler=GameByGame())




.. parsed-literal::

    <rstt.ranking.ranking.Ranking at 0x11326b9e0>



1.2 Class Design
^^^^^^^^^^^^^^^^

We recommand to represent a ranking design in its own class with an
explicit naming. It makes it more clear what parameters are inherent to
the ranking design, and which are tunable hyper-parameters for
comparative studies.

.. code:: python

    # Distinguish core design from parameters, handler is not a parameter.
    class EloGBG(Ranking):
        def __init__(self, name: str, default_rating: float=1000, k: float=20):
            # The standing component provided in the super() init.
            super().__init__(name=name,
                             datamodel=KeyModel(default=default_rating), # RatingSystem
                             backend=Elo(k=k), # Inference
                             handler=GameByGame()) # Observer

1.3 Run illustration
^^^^^^^^^^^^^^^^^^^^

As you can see, there is not much to do and it works just fine in
simulation. The RSTT built-in `BasicElo <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.BasicElo>`__ class code is in fact very
similar. All ranking’s functionalities are implemented at a higher level
of abstraction and relies on minimal requirements from its components to
work as intended.

.. code:: python

    from rstt import Player, RoundRobin, LogSolver
    
    # our ranking design
    elo = EloGBG('elo')
    
    # players
    population = Player.create(nb=32)
    
    # play games - ranking used as seeding
    tournament = RoundRobin('test', elo, LogSolver())
    tournament.registration(population)
    tournament.run()
    
    # check if update works
    elo.update(games=tournament.games())
    elo.plot()


.. parsed-literal::

    ----------- elo -----------
       0.       Tiffany Vinson       1210
       1.           Gary Young       1196
       2.        Javier Henson       1192
       3.     Antionette Welsh       1145
       4.         Michael Mora       1130
       5.        Joseph Austin       1130
       6.       Shannon Monroe       1123
       7.      Timothy Hubbard       1120
       8.           Tim Cramer       1060
       9.        Theresa Doyle       1055
      10.         Linda Aberle       1047
      11.        Matthew Salas       1038
      12.        Beulah Mcgill       1031
      13.      Tamica Martinez       1031
      14.         Nancy Valdez       1027
      15.        Charles Tracy       1015
      16.        Donald Hauger        977
      17.         Anthony Tong        973
      18.        Stacie Parker        965
      19.         Billy Hughes        941
      20.          Susan Lesko        935
      21.        Betty Mehling        932
      22.       Richard Rosado        931
      23.         Debra Ferris        924
      24.     Howard Osterberg        921
      25.       Donald Nuttall        900
      26.         James Vasher        870
      27.        Tracy Cordova        861
      28.       Lorraine Walls        848
      29.          Peggy Smith        842
      30.         Megan Hinton        820
      31.        Joanne Patton        794


2. Use OpenSkill in RSTT
------------------------

`Openskill <https://github.com/vivekjoshy/openskill.py>`__ is an
Inference system according to RSTT terminology. On Github, it encourages
to drop TrueSkill and Elo. So … lets test it!

2.1 Ranking.datamodel: stypes.RatingSystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It acts as a container of rating object. It must provide get and set
method for player’s rating. It also provides a float interpretation of
rating with an ordinal funciton. Lets first take a look at openskill
rating.

.. code:: python

    from openskill.models import PlackettLuce
    
    model = PlackettLuce()
    rating = model.rating()
    print('Rating data - mu:', rating.mu, 'sigma:', rating.sigma, 'name:', rating.name, 'id:', rating.id)


.. parsed-literal::

    Rating data - mu: 25.0 sigma: 8.333333333333334 name: None id: 3db7d7a810ec4ea48d778f70bdfe652b


2.2 KeyModel, a general purpose RatingSystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The
`KeyModel <https://rstt.readthedocs.io/en/latest/rstt.ranking.html#module-rstt.ranking.datamodel>`__
class is a base class for the RatingSystem protocol (see elo example).
It provides all features needed and just require you to provide a
default rating (for player that do not have one yet).

There are 3 way to specify a default rating - by providing a value:
**default** = model.rating() - by providing a constructor: **template**
= model.rating - by providing a function which takes as input the player
for which a rating is created: **factory** = lambda player: …

In the case of openskill, since rating do contain an id, it is better to
avoid the default approach. The template is an option, but since rating
have names, why not make it match the one player.name()? Let us use the
factory approach.

KeyModel has a basic ordinal implementation that will not work here. We
need to overide it.

.. code:: python

    from rstt.ranking import KeyModel
    
    class OSRatings(KeyModel):
        def __init__(self, model, mu=None, sigma=None):
            # the first parameter of the factory is always the player getting a rating
            super().__init__(factory=lambda x, **kwargs: model.rating(name=x.name(), **kwargs), mu=mu, sigma=sigma)
    
        def ordinal(self, rating) -> float:
            # openskill ratings have an ordinal functionality themself - easy !
            return rating.ordinal()
    
    osr = OSRatings(PlackettLuce(), mu=40, sigma=5)
    rating = osr.get(Player('dummy'))
    print(rating)


.. parsed-literal::

    Plackett-Luce Player Data: 
    
    id: 83c17cdd2b90447a8ae5fc350375410c
    name: dummy
    mu: 40
    sigma: 5
    


2.2 Ranking.backend: stypes.Inference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inference is defined as a Protocol and typechecked in the RSTT package.
Anything that provide a .rate() method fits the bill. Openskill.models
have all a .rate method thus are RSTT.stypes.Inference and can directly
be passed to a ranking class as backend. Nothing to do. Cool!

This is not always the case. You can however write a simple class with a
rate method that wrapps the rate process of a system to intergrate.

2.3 Ranking.handler: stypes.Observer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The handler.handle_observations() method is called by the
ranking.forward() during the ranking.update() execution.

-  Ranking.update is a user level functionnality that should **NEVER**
   be override.
-  Ranking.forward is a develloper functionnality. It **CAN** be
   override, usualy not necessary.
-  Observer.handle_observations is a complete workflow from the update
   input to the new ranking state.

In a majority of cases, the handle_observations perform the following
steps: 1) Format the update inputs. The inputs are referred as
‘observations’. They justify a change of ranking state. 2) Extract from
the observations the relevant information 3) Query the datamodel for the
corresponding *prior* ratings 4) Call the backend.rate method with
correct arguments 5) Interpret the backend.rate return values 6) Push
the *posteriori* ratings to the datamodel

We want to input a list of RSTT.stypes.SMatch. We already have workedk
on the ratings in the datamodel. We need to extract relevant data from
games. So we need to know what to pass to the rate method. Lets have a
look at its signature.

.. code:: python

    import inspect
    inspect.getfullargspec(model.rate).annotations




.. parsed-literal::

    {'return': typing.List[typing.List[openskill.models.weng_lin.plackett_luce.PlackettLuceRating]],
     'teams': typing.List[typing.List[openskill.models.weng_lin.plackett_luce.PlackettLuceRating]],
     'ranks': typing.Optional[typing.List[float]],
     'scores': typing.Optional[typing.List[float]],
     'tau': typing.Optional[float],
     'limit_sigma': typing.Optional[bool]}



**TODO:** Your Task is to read the Observer code and try to identify the
6 steps.

.. code:: python

    from rstt.stypes import RatingSystem, Inference, SMatch
    
    class OSHandler:
        def handle_observations(self, datamodel: RatingSystem, infer: Inference, games: list[SMatch]):
            for game in games:
                # extract game info
                teams_of_players = game.teams()
                scores = game.scores() # alternative: ranks = game.ranks()
                
                # get corresponding rating from datamodel
                teams = [] # list[list[rating]]
                for team in teams_of_players:
                    ratings = [] # list[rating]
                    for player in team:
                        ratings.append(datamodel.get(player))
                    teams.append(ratings)
                
                # call rate
                new_ratings = infer.rate(teams=teams, scores=scores) # or ..., ranks=ranks)
                
                # push new ratings
                for team, ratings in zip(teams_of_players, new_ratings):
                    for player, rating in zip(team, ratings):
                        datamodel.set(player, rating)

**ANSWER**

-  step1: no formating, if the user does not pass a list of games, the
   observer will not work
-  step2: games.teams() and games.scores()
-  step3: datamodel.get() calls
-  step4: infer.rate() call
-  step5: the *for … in zip(…)* matches the output of the rate method
   with the adequate players in simulations
-  step6: datamodel.set() calls

2.4 Run illustration
^^^^^^^^^^^^^^^^^^^^

The OpenSkill Ranking class will take one single parameter, an
openskill.models object. And then it is ready to be used.

.. code:: python

    # Openskill class
    class OpenSkill(Ranking):
        def __init__(self, name: str, model):
            super().__init__(name=name, datamodel=OSRatings(model), backend=model, handler=OSHandler())
    
    # OS Instance
    os = OpenSkill('OpenSkill', model)
    
    # OS update on rstt simulated games
    os.update(games=tournament.games())

**Remark:** RSTT provides an OpenSkill ranking wrapper -
`BasicOS <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.BasicOS>`__
- which is not exactly implemented as present in the tutorials, but
works similary. You still need to import Openskill and pass a model
yourself.

3. Ranking functionality
------------------------

This is now openskill on steroïds. You can access playesr by ranks, get
rating of a player. You can use it to seed competition like a single
elimination bracket. Lets start by a standard output plot of the
standing.

.. code:: python

    os.plot()


.. parsed-literal::

    ----------- OpenSkill -----------
       0.       Tiffany Vinson         35
       1.           Gary Young         33
       2.        Javier Henson         31
       3.     Antionette Welsh         27
       4.         Michael Mora         26
       5.        Joseph Austin         24
       6.      Timothy Hubbard         24
       7.       Shannon Monroe         24
       8.           Tim Cramer         17
       9.         Linda Aberle         16
      10.        Theresa Doyle         16
      11.        Beulah Mcgill         16
      12.        Matthew Salas         15
      13.      Tamica Martinez         14
      14.        Charles Tracy         13
      15.         Nancy Valdez         12
      16.        Donald Hauger          9
      17.         Anthony Tong          8
      18.        Stacie Parker          7
      19.         Billy Hughes          5
      20.          Susan Lesko          4
      21.        Betty Mehling          3
      22.       Richard Rosado          3
      23.         Debra Ferris          3
      24.     Howard Osterberg          2
      25.       Donald Nuttall          0
      26.         James Vasher         -2
      27.        Tracy Cordova         -4
      28.       Lorraine Walls         -6
      29.          Peggy Smith         -8
      30.         Megan Hinton        -10
      31.        Joanne Patton        -15


3.1 Rank Correlation
^^^^^^^^^^^^^^^^^^^^

RSTT ranking interface simplifies some metrics compuation, like rank
correlation. The advantage of simulation is that you have a baseline to
comupte it. Lets compare elo and openskill to the simulation model.

.. code:: python

    from scipy import stats
    from rstt import BTRanking
    
    # ranking where players ratings are their respectives level(). 
    gt = BTRanking('consensus', population)
    
    print('OpenSkill - GroundTRuth correlation: \n  ', stats.kendalltau(gt[population], os[population]))
    print('Elo - GroundTRuth correlation: \n  ', stats.kendalltau(gt[population], elo[population]))
    print('OpenSkill - Elo correlation: \n  ', stats.kendalltau(elo[population], os[population]))


.. parsed-literal::

    OpenSkill - GroundTRuth correlation: 
       SignificanceResult(statistic=np.float64(0.8508064516129034), pvalue=np.float64(8.187631748655122e-17))
    Elo - GroundTRuth correlation: 
       SignificanceResult(statistic=np.float64(0.866935483870968), pvalue=np.float64(7.496744126671432e-18))
    OpenSkill - Elo correlation: 
       SignificanceResult(statistic=np.float64(0.9838709677419356), pvalue=np.float64(3.9371288142144177e-31))


3.2 Ranking state as simulation parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can easly play arround with the inital state of any RSTT ranking by
provding an arbitrary ordering of the players involved.

.. code:: python

    import random
    
    # random ordering
    seeds = list(range(len(os)))
    random.shuffle(seeds)
    
    print(list(range(len(os))))
    print(seeds)
    print('Seeds - Truth correlation:', stats.kendalltau(seeds, list(range(len(os)))).statistic)
    
    # reordering
    elo.rerank(seeds)
    os.rerank(seeds)
    
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[population], os[population]).statistic)
    print('Elo - GroundTRuth correlation:', stats.kendalltau(gt[population], elo[population]).statistic)
    print('OpenSkill - Elo correlation:', stats.kendalltau(elo[population], os[population]).statistic)


.. parsed-literal::

    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    [14, 10, 28, 3, 27, 26, 16, 17, 23, 22, 4, 0, 2, 13, 1, 11, 18, 30, 12, 24, 29, 20, 15, 31, 7, 8, 6, 21, 5, 9, 19, 25]
    Seeds - Truth correlation: -0.00806451612903226
    OpenSkill - GroundTRuth correlation: -0.00403225806451613
    Elo - GroundTRuth correlation: -0.00403225806451613
    OpenSkill - Elo correlation: 0.7822580645161291


3.3 Control the Interplay between a Ranking and a Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now it is possible to select players and seed them in a competition
based on their openskill ratings.

.. code:: python

    from rstt import SwissRound
    
    # reordered openskill ranking as seeding
    t2 = SwissRound(name='OpensKill seeded tournament', seeding=os, solver=LogSolver())
    
    # top 16 players according to openskill
    t2.registration(os[:16])
    t2.run()
    
    os.update(games=t2.games())
    elo.update(games=t2.games())

3.4 Fancy Analysis
^^^^^^^^^^^^^^^^^^

Let see what changed. Keep in mind that we atrificialy altered the
entire ranking state, but only half of the players where involved in the
new dataset.

.. code:: python

    print('-- Kendalltau rank correaltion on the entire population --')
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[population], os[population]).statistic)
    print('Elo - GroundTRuth correlation:', stats.kendalltau(gt[population], elo[population]).statistic)
    print('OpenSkill - Elo correlation:', stats.kendalltau(elo[population], os[population]).statistic)
    
    print('\n -- Kendalltau rank correaltion on the real top16 --')
    top16 = gt[:16]
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[top16], os[top16]).statistic)
    print('Elo - GroundTRuth correlation:', stats.kendalltau(gt[top16], elo[top16]).statistic)
    print('OpenSkill - Elo correlation:', stats.kendalltau(elo[top16], os[top16]).statistic)
    
    print('\n -- Kendalltau rank correaltion on the \'openskill prio\' top16 --')
    seed16 = t2.participants()
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[seed16], os[seed16]).statistic)
    print('Elo - GroundTRuth correlation:', stats.kendalltau(gt[seed16], elo[seed16]).statistic)
    print('OpenSkill - Elo correlation:', stats.kendalltau(elo[seed16], os[seed16]).statistic)


.. parsed-literal::

    -- Kendalltau rank correaltion on the entire population --
    OpenSkill - GroundTRuth correlation: 0.08064516129032259
    Elo - GroundTRuth correlation: 0.08467741935483872
    OpenSkill - Elo correlation: 0.7943548387096775
    
     -- Kendalltau rank correaltion on the real top16 --
    OpenSkill - GroundTRuth correlation: 0.0
    Elo - GroundTRuth correlation: 0.0
    OpenSkill - Elo correlation: 0.6333333333333333
    
     -- Kendalltau rank correaltion on the 'openskill prio' top16 --
    OpenSkill - GroundTRuth correlation: 0.26666666666666666
    Elo - GroundTRuth correlation: 0.15
    OpenSkill - Elo correlation: 0.5166666666666667


4 OpenSkill as Solver
---------------------

A Solver is anything that provide a solve() method. It is used to assign
a Score to SMatch. Because OpenSkill has methods to predict game
outcome, it could be used has a solver. Below is an example for Duel
confrontation. we are extending the Solver ScoreProb which generate game
outcome based on a score probability.

.. code:: python

    from rstt.solver.solvers import ScoreProb, WIN, LOSE
    from rstt import Duel
    
    import random
    
    # OpenSkill Solver
    class OSS(ScoreProb):
        def __init__(self, os: OpenSkill):
            self.model = os.backend
            self.ratings = os.datamodel
            
            # NOTE: WIN is an alias for player1 wins; LOSE if an alias for player1 lose, i.e player2 wins
            super().__init__(scores=[WIN, LOSE], func=self.predict_win)
    
        def predict_win(self, duel: Duel) -> list[float]:
            # NOTE: when player1 wins, then player2 lose and vice-versa
            return self.model.predict_win([[self.ratings.get(duel.player1())], [self.ratings.get(duel.player2())]])

4.1 Level Coherence
^^^^^^^^^^^^^^^^^^^

The OSS class does not care about involved player’s level. It needs
OpenSkill ratings, which is completely indepandent. Player with high
level having less than 0.5 win probability against player with lower
level can be confusing. One way to keep the Player base class coherent
with the solver is to train the rating on an *ideal dataset*, one where
every player faces each others at least once and the best player wins
the encounters. We can use
`RoundRobin <https://rstt.readthedocs.io/en/latest/rstt.scheduler.tournament.html#rstt.scheduler.tournament.groups.RoundRobin>`__
and
`BetterWin <https://rstt.readthedocs.io/en/latest/rstt.solver.html#rstt.solver.solvers.BetterWin>`__
for this purpose.

.. code:: python

    from openskill.models import BradleyTerryFull
    from rstt import BetterWin
    
    # Perfect Data Set
    training_set = RoundRobin('Training Set', seeding=gt, solver=BetterWin())
    training_set.registration(population)
    training_set.run()
    
    # Train OpenSkill -> make meaningfull ratings
    os_trained = OpenSkill('OpenSkill as Solver', model=BradleyTerryFull())
    os_trained.update(games=training_set.games())
    
    # assert ranking quality
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[population], os_trained[population]).statistic)


.. parsed-literal::

    OpenSkill - GroundTRuth correlation: 1.0


4.2 Simulation
^^^^^^^^^^^^^^

And now we can instanciate and run competition sublass by providing OSS
as a solver. The game results are generated according to OpenSkill model
prediction.

.. code:: python

    from rstt import SingleEliminationBracket, SwissBracket
    from rstt import BasicGlicko
    
    # OpenSkill as Solver
    oss = OSS(os_trained)
    
    # test ranking
    gl = BasicGlicko('Glicko')
    btf = OpenSkill('BTF tested', model=BradleyTerryFull())
    
    # play games using openskill prediction to generate scores
    seb = SingleEliminationBracket('Example SEB', seeding=gt, solver=oss)
    seb.registration(population)
    seb.run()
    
    
    print('OSS solver defines the truth level - After Single-Elimination-Bracket')
    gl.update(games=seb.games())
    btf.update(games=seb.games())
    print('GroundTRuth - Glicko correlation:', stats.kendalltau(os_trained[population], gl[population]).statistic)
    print('GroundTRuth - BTS correlation:', stats.kendalltau(os_trained[population], btf[population]).statistic)
    
    # play games using openskill prediction to generate scores
    swb = SwissBracket('Example SwissBracket', seeding=gt, solver=oss)
    swb.registration(population[:16])
    swb.run()
    
    print('OSS solver defines the truth level - After Swiss-Bracket')
    gl.update(games=seb.games())
    btf.update(games=swb.games())
    print('GroundTRuth - Glicko correlation:', stats.kendalltau(os_trained[population], gl[population]).statistic)
    print('GroundTRuth - BTS correlation:', stats.kendalltau(os_trained[population], btf[population]).statistic)


.. parsed-literal::

    OSS solver defines the truth level - After Single-Elimination-Bracket
    GroundTRuth - Glicko correlation: 0.5967741935483871
    GroundTRuth - BTS correlation: 0.5967741935483871
    OSS solver defines the truth level - After Swiss-Bracket
    GroundTRuth - Glicko correlation: 0.4435483870967743
    GroundTRuth - BTS correlation: 0.7500000000000001


5. Your Turn - Trueskill
------------------------

`Trueskill <https://trueskill.org>`__ also fits the
RSTT.stypes.Inference interface with a rate method. You know how to use
it now!

6. Your Turn - Real Data
------------------------

Running rstt ranking on real dataset is not hard? Do you have an idea
how to make it work?

That is right. You write an observer! The component that deals with the
update input.
