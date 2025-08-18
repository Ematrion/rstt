RSTT Tutorial 2
===============

Integration
-----------

In this notebook we will use the
`openskill <https://openskill.me/en/stable/>`__ rating system with RSTT.
The goal is to wrapp model in a Ranking class to benefit from its
functionnalities and fit in simulation.

1. RSTT Ranking Design
----------------------

A
`Ranking <https://rstt.readthedocs.io/en/latest/rstt.ranking.html#rstt.ranking.ranking.Ranking>`__
is a composition over inheritance design that contains: - A
`Standing <https://rstt.readthedocs.io/en/latest/rstt.ranking.html#rstt.ranking.standing.Standing>`__:
dict/list container hybrid. **Automaticaly sorts player** based on their
*ranking point* - A
`RatingSystem <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.RatingSystem>`__:
dict like container that **maps player with ratings** - An
`Inference <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Inference>`__:
provide a **.rate method()** to compute ratings - An
`Observer <https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Observer>`__:
provide an **.handle_observations()** method that process ranking.update
input

Before integrating external system, lets start with a simple
illustration. A ranking can be instanciated with its components
specified. However, we recommand to represent a ranking design in its
own class. It makes it more clear what parameters are intresect to the
ranking design, and which are hyper-parameters.

1.1 Simple instanciation
^^^^^^^^^^^^^^^^^^^^^^^^

A ranking can be instanciated with its components specified. NOT
RECOMMANDED

.. code:: python

    from rstt import Ranking
    from rstt.ranking import KeyModel, Elo, GameByGame
    
    # Ambiguity about between core element and parameters. Is the handler a tunable parameter of the ranking?
    Ranking(name='elo', datamodel=KeyModel(default=1000), backend=Elo(k=20), handler=GameByGame())




.. parsed-literal::

    <rstt.ranking.ranking.Ranking at 0x1063ff350>



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
                             backend=Elo(k=20), # Inference
                             handler=GameByGame()) # Observer

1.3 Run illustration
^^^^^^^^^^^^^^^^^^^^

As you can see, there is not much to do and it works just fine in
simulation. The RSTT built-in `BasicElo <>`__ class code is in fact very
similar. All ranking’s functionalities are implemented at a higher level
of abstraction and relies on minimal requirements from its components to
work as intended.

.. code:: python

    from rstt import Player, RoundRobin, LogSolver
    
    # our ranking design
    elo = EloGBG('elo')
    
    # players
    population = Player.create(nb=32)
    
    # games
    tournament = RoundRobin('test', elo, LogSolver())
    tournament.registration(population)
    tournament.run()
    
    # check if it works
    elo.update(games=tournament.games())
    elo.plot()


.. parsed-literal::

    ----------- elo -----------
       0.       Veronica Clark       1219
       1.     Stephanie Jordan       1191
       2.           Chad Brown       1186
       3.     Christopher Cade       1172
       4.          Mable Baker       1143
       5.          Donna Mckee       1143
       6.        Margaret Bass       1132
       7.       Ashley Sanchez       1099
       8.         Ryan Pickard       1085
       9.        Steven Dupree       1085
      10.      Kathryn Coleman       1056
      11.       Timothy Vargas       1051
      12.          Hilda Smith       1036
      13.        Angela Mccray       1015
      14.      Virginia Seeley       1005
      15.        Marina Thomas        990
      16.       Randy Richards        989
      17.          David Bowen        972
      18.        Scott Dobbins        963
      19.        Alyson Curiel        962
      20.        Joyce Calisto        941
      21.         Ana Valencia        926
      22.      Allyson Johnson        922
      23.        Todd Crawford        901
      24.     Seymour Frerichs        899
      25.     Charles Mitchell        884
      26.          John Lawson        871
      27.        Gregory Saari        867
      28.         Pearl Crouse        866
      29.          Kevin Dryer        820
      30.          Glady Davis        800
      31.         Peter Chavez        791


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

    from openskill.models import PlackettLuce, BradleyTerryFull, BradleyTerryPart, ThurstoneMostellerFull, ThurstoneMostellerPart # noqa F401
    
    model = PlackettLuce()
    rating = model.rating()
    print('name:', rating.name, 'id:', rating.id)
    rating


.. parsed-literal::

    name: None id: 8dddf85814d54895b9bce6fa52de4d2b




.. parsed-literal::

    PlackettLuceRating(mu=25.0, sigma=8.333333333333334)



2.2 KeyModel, a general purpose RatingSystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The KeyModel class is a base class for the RatingSystem protocol (see
elo example). It provides all features needed and just require you to
provide a default rating (for player that do not have one yet).

There are 3 way to specify a default rating - by providing a value:
**default** = model.rating() - by providing a constructor: **template**
= model.rating - by providing a function which takes as input the player
for which a rating is created: **factory** = lambda player:
model.rating(name=player.name()

In the case of openskill, since rating do contain an id, it is better to
avoid the default approach. The template is an option, but since rating
have names, why not make it match the one player.name()? Let us use the
factory approach.

KeyModel has a basic ordinal implementation that will not work here. We
need to overite it.

.. code:: python

    from rstt.ranking import KeyModel
    
    class OSRatings(KeyModel):
        def __init__(self, model):
            super().__init__(factory= lambda x, **kwargs: model.rating(name=x.name(), **kwargs), mu=40, sigma =5)
    
        def ordinal(self, rating) -> float:
            # openskill ratings have an ordinal functionality themself - easy !
            return rating.ordinal()

.. code:: python

    osr = OSRatings(PlackettLuce())
    osr.get(Player('dummy'))




.. parsed-literal::

    PlackettLuceRating(mu=25.0, sigma=8.333333333333334)



2.2 Ranking.backend: stypes.Inference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inference is a notion define as a Protocol and typechecked in the RSTT
package. Anything that provide a .rate() method fits the bill.
Openskill.models have all a .rate method thus are RSTT.stypes.Inference
and can directly be passed to a ranking class as backend. Nothing to do.
Cool!

This is not always the case. You can however write a simple class with a
rate method that wrapps the rate process of the system to intergrate.

2.3 Ranking.handler: stypes.Observer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The handler.handle_observations() method is called by the
ranking.forward() during the ranking.update() execution.

-  Ranking.update is a user level functionnality that should **NEVER**
   be override.
-  Ranking.forward is a develloper functionnality. It **CAN** be
   override, usualy not necessary.
-  Observer.handle_observations deals is a complete workflow from the
   update input to the new ranking state

In a majority of cases, the handle_observations perform the following
steps: 1) Format the update inputs. The inputs are referred as
‘observations’. They justify a change of ranking state. 2) Extract from
the observations the relevant information 3) Query the datamodel for the
corresponding *prior* ratings 4) Call the backend.rate method with
correct arguments 5) Interpret the backend.rate return values 6) Push
the *posteriori* ratings to the datamodel

We want to input a list of RSTT.stypes.SMatch. We already have work on
the ratings in the datamodel. We need to extract relevant data from
games. So we need to know what to pass to the rate method. Lets have a
look at its signature. Your Task is to read the Observer code and
identify the 6 steps.

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

2.4 Run illustration
^^^^^^^^^^^^^^^^^^^^

The OpenSkill Ranking class will take one single parameter, an
openskill.models object. And then it is ready to be used.

.. code:: python

    class OpenSKill(Ranking):
        def __init__(self, name: str, model):
            super().__init__(name=name, datamodel=OSRatings(model), backend=model, handler=OSHandler())
    
    os = OpenSKill('OpenSkill', model)
    os.update(games=tournament.games())
    os.plot()


.. parsed-literal::

    ----------- OpenSkill -----------
       0.       Veronica Clark         37
       1.     Stephanie Jordan         33
       2.           Chad Brown         32
       3.     Christopher Cade         31
       4.          Donna Mckee         27
       5.          Mable Baker         27
       6.        Margaret Bass         25
       7.       Ashley Sanchez         21
       8.         Ryan Pickard         20
       9.        Steven Dupree         19
      10.      Kathryn Coleman         18
      11.       Timothy Vargas         16
      12.          Hilda Smith         14
      13.        Angela Mccray         13
      14.      Virginia Seeley         11
      15.        Marina Thomas         10
      16.       Randy Richards          9
      17.        Alyson Curiel          8
      18.          David Bowen          7
      19.        Scott Dobbins          7
      20.        Joyce Calisto          4
      21.         Ana Valencia          3
      22.      Allyson Johnson          2
      23.     Seymour Frerichs          0
      24.        Todd Crawford          0
      25.     Charles Mitchell         -1
      26.          John Lawson         -3
      27.        Gregory Saari         -3
      28.         Pearl Crouse         -4
      29.          Kevin Dryer        -10
      30.          Glady Davis        -13
      31.         Peter Chavez        -16


3. Ranking functionality
------------------------

This is now openskill on steroïds. You can access playesr by ranks, get
rating of a player You can use it to seed competition like a single
elimination bracket. Lets start by a simple standard output plot of the
standing.

.. code:: python

    os.plot()


.. parsed-literal::

    ----------- OpenSkill -----------
       0.       Veronica Clark         37
       1.     Stephanie Jordan         33
       2.           Chad Brown         32
       3.     Christopher Cade         31
       4.          Donna Mckee         27
       5.          Mable Baker         27
       6.        Margaret Bass         25
       7.       Ashley Sanchez         21
       8.         Ryan Pickard         20
       9.        Steven Dupree         19
      10.      Kathryn Coleman         18
      11.       Timothy Vargas         16
      12.          Hilda Smith         14
      13.        Angela Mccray         13
      14.      Virginia Seeley         11
      15.        Marina Thomas         10
      16.       Randy Richards          9
      17.        Alyson Curiel          8
      18.          David Bowen          7
      19.        Scott Dobbins          7
      20.        Joyce Calisto          4
      21.         Ana Valencia          3
      22.      Allyson Johnson          2
      23.     Seymour Frerichs          0
      24.        Todd Crawford          0
      25.     Charles Mitchell         -1
      26.          John Lawson         -3
      27.        Gregory Saari         -3
      28.         Pearl Crouse         -4
      29.          Kevin Dryer        -10
      30.          Glady Davis        -13
      31.         Peter Chavez        -16


3.1 Rank Correlation
^^^^^^^^^^^^^^^^^^^^

RSTT ranking interface simplifies some metrics compuation, like rank
correlation. The advantage of simulation is that you have a baseline to
comupte it. Lets compare elo, openskill and the simulation model.

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
       SignificanceResult(statistic=np.float64(0.9233870967741936), pvalue=np.float64(1.8369284310000514e-22))
    Elo - GroundTRuth correlation: 
       SignificanceResult(statistic=np.float64(0.931451612903226), pvalue=np.float64(2.6719535498432205e-23))
    OpenSkill - Elo correlation: 
       SignificanceResult(statistic=np.float64(0.9838709677419356), pvalue=np.float64(3.9371288142144177e-31))


3.2 Ranking state as simulation parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can easly play arround with the inital state of any RSTT ranking by
provding an arbitrary ordering of the players involved.

.. code:: python

    import random
    
    seeds = list(range(len(os)))
    random.shuffle(seeds)
    
    print(list(range(len(os))))
    print(seeds)
    print('Seeds - Truth correlation:', stats.kendalltau(seeds, list(range(len(os)))).statistic)
    
    elo.rerank(seeds)
    os.rerank(seeds)
    print('OpenSkill - GroundTRuth correlation:', stats.kendalltau(gt[population], os[population]).statistic)
    print('Elo - GroundTRuth correlation:', stats.kendalltau(gt[population], elo[population]).statistic)
    print('OpenSkill - Elo correlation:', stats.kendalltau(elo[population], os[population]).statistic)


.. parsed-literal::

    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    [2, 12, 1, 17, 18, 26, 16, 24, 25, 19, 31, 3, 20, 11, 27, 15, 29, 9, 4, 10, 7, 23, 30, 13, 21, 22, 8, 5, 0, 14, 28, 6]
    Seeds - Truth correlation: -0.036290322580645164
    OpenSkill - GroundTRuth correlation: 0.0
    Elo - GroundTRuth correlation: 0.0
    OpenSkill - Elo correlation: 0.8467741935483872


3.3 Control the Interplay between a Ranking and a Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now it is possible to select players and seed them in a competition
based on their openskill ratings.

.. code:: python

    from rstt import SwissRound
    
    t2 = SwissRound(name='OpensKill seeded tournament', seeding=os, solver=LogSolver())
    t2.registration(os[:16]) # top 16 players according to openskill
    t2.run()
    os.update(games=t2.games())
    elo.update(games=t2.games())

3.4 Fancy Analisys
^^^^^^^^^^^^^^^^^^

Let see what changed. Keep in mind that we atrificialy changed the
entire ranking state, but only a fraction of the players where involved
in the new dataset.

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
    OpenSkill - GroundTRuth correlation: 0.060483870967741944
    Elo - GroundTRuth correlation: 0.040322580645161296
    OpenSkill - Elo correlation: 0.8427419354838711
    
     -- Kendalltau rank correaltion on the real top16 --
    OpenSkill - GroundTRuth correlation: 0.5499999999999999
    Elo - GroundTRuth correlation: 0.5333333333333333
    OpenSkill - Elo correlation: 0.8499999999999999
    
     -- Kendalltau rank correaltion on the 'openskill prio' top16 --
    OpenSkill - GroundTRuth correlation: 0.35
    Elo - GroundTRuth correlation: 0.26666666666666666
    OpenSkill - Elo correlation: 0.7833333333333333


4. Your Turn - Trueskill
------------------------

`Trueskill <https://trueskill.org>`__ is also an RSTT.stypes.Inference.
You know how to use it now!

5. Your Turn - Real Data
------------------------

If I tell you it is not hard to run rstt ranking on real dataset, do you
have an idea how to make it work?

That is right. You write an oberserver! The component that deals with
the update input.
