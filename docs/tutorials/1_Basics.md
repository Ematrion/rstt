# RSTT Tutorial 1
## Concept, Component, Usage and Workflow

Welcome to the RSTT package introduction and thank you for your interest.

Competition simulation is build arround the following concept:
- **Participants**: players, competitors, athletes.
- **Match**: game, confrontation, encounter.
- **Score** (and Solver): Outcome, result of a match.
- **Ranking**: A list of player ordered by infered ratings.
- **Scheduler**: automated game generation worflow

## 1. Player

In RSTT, any object providing a .name() and a .level() method are [SPlayer](https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.SPlayer), they can be register in Rankings, take part in Competition and play games

When the **strenght of player is constant** you can use the [BasicPlayer](https://rstt.readthedocs.io/en/latest/rstt.player.html#rstt.player.basicplayer.BasicPlayer), but there are other alternatives.


```python
from rstt import BasicPlayer

p1 = BasicPlayer(name='Ready?', level=9000)
p2 = BasicPlayer(name='Fight!', level=1000)

print(p1.name(), p2.level())
```

    Ready? 1000


## 2. Match

Objects providing a .players() and a .scores() methords are called [SMatch](https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.SMatch). They model games as an encounter between competitors with an outcome. The [Duel](https://rstt.readthedocs.io/en/latest/rstt.game.html#rstt.game.match.Duel) class is usefull for **versus** type of game/sport - like Chess or Hockey.

**Note**: In RSTT a match does not reflect the sport or game rules. It is an encounter. The title rules, mechanism is reflected by the Solver (See cell [Play Games](#outcome)).


```python
from rstt import Duel

# create an encounter
duel = Duel(player1=p1, player2=p2)

# find opponent
print(p1.name(), duel.opponent(p1))

# get involved players
print('Match participants:', duel.players())

# Get the match outcome
print('Match score:', duel.scores())

# Has the game been played, or not yet ?
print('The match has not yet been played: ', duel.live())
```

    Ready? Fight!
    Match participants: [Player - name: Ready?, level: 9000, Player - name: Fight!, level: 1000]
    Match score: None
    The match has not yet been played:  True


## 3. Play Games

### 3.1 Score: Game Outcome
The Outcome of a game is modeled by a [Score](https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Score), which essentialy is a list of float values indicating the *score* of each participants in a match. The Package provides WIN, LOSE, DRAW aliases for direct confrontations.

### 3.2 Solver & Outcome Generation <a id='outcome'></a>
Score are not supposed to be *manualy* assigned to a match. [Solver](https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Solver) have this responsaility. It is meaningfull to use solver that decide the score depending on the players levels.
Obviously, match can only have one outcome and can not be *solved* twice. This can be sometimes annoying in an interactive environement like a notebook. But it is a feature ensuring data integrity. 


```python
from rstt import BetterWin

# Solver needs to be instanciated
better = BetterWin()

# Assign an outcome to a match
better.solve(duel)

# access match score
print('Duel score:', duel.scores())
print(f'Score of player: {duel.player1().name()}: {duel.score(duel.player1())}')

# get the winner and the lose (duel method)
print('Winner of the game:', duel.winner())
print('Loser of the game:', duel.loser())

# after being solver, the game is no longer live
print('The game has been played:', not duel.live())

print('\nRuntimeError')
try:
    # Be carefull when rerunning code portions in an interactive environement
    #
    better.solve(duel)
except RuntimeError as e:
    print(e)
```

    Duel score: [1.0, 0.0]
    Score of player: Ready?: 1.0
    Winner of the game: Ready?
    Loser of the game: Fight!
    The game has been played: True
    
    RuntimeError
    Attempt to assign a score to a game that has already one <class 'rstt.game.match.Duel'> - teams: [[Player - name: Ready?, level: 9000], [Player - name: Fight!, level: 1000]], scores: [1.0, 0.0]


## 4. Ranking

[Ranking](https://rstt.readthedocs.io/en/latest/rstt.ranking.html#module-rstt.ranking.ranking) in RSTT is a quiet complex construction that deserves its own formal and technical description. And realy, this does not fit in an introduction. But you know what a ranking is right?

- Ranking behaves as a list of player.
- Ranking behaves as a dictionnary mapping player with their index in the list
- Player in a ranking have a rank, point and a rating.
- Player's point are computed based on their rating
- A ranking can be updated, as a result player's rating might be affected.
- Players are automaticaly sorted using their point
- you can display a ranking to the standard output

There are many different ranking implemented. The [BTRanking](https://rstt.readthedocs.io/en/latest/rstt.ranking.standard.html#rstt.ranking.standard.consensus.BTRanking) is a consensual ranking that rates players by levels.

**Note:** index/rank start at 0, like list - unlike 'real life' ranking where the highest rank is 1. 


```python
from rstt import BTRanking

# create a ranking
btr = BTRanking('Player Level', players=[p1, p2])

# get a player information
print('Ranking information of:', p1.name(),
      '\nindex', btr[p1],
      '\nrank', btr.rank(p1), '(alias for index)',
      '\npoint', btr.point(p1), '(used to compute the player\'s rank)',
      '\nrating', btr.rating(p1), '(used to compute the player\'s point)\n')

# plot a ranking
btr.plot()
```

    Ranking information of: Ready? 
    index 0 
    rank 0 (alias for index) 
    point 9000.0 (used to compute the player's rank) 
    rating 9000 (used to compute the player's point)
    
    ----------- Player Level -----------
       0.               Ready?       9000
       1.               Fight!       1000


## 5. Scheduler

Any worklfow generating automaticaly games encounter is considered a Scheduler. There is not a type, class or protocl defining it in the package. It simply is a terminology you may see in the documentation. The notion covers tournament format such as round-robin and live matchmaking services in online-video games. 

[Competition](https://rstt.readthedocs.io/en/latest/rstt.scheduler.tournament.html#rstt.scheduler.tournament.competition.Competition) is an abstract class and defines Scheduler *bounded in time and space*: Competition have a clear defined amount of players, number of games, a start time and an end. Competition produces games and output a standing, the participant achievements. A round-robin is a competition, online live matchakings are not.

To implement a Competition you need to provide:
- a name: which is assumed to be unique, Player should not participate twice in the same Competition
- a raking as seeding: which helps deciding who faces who during the event
- a solver: which decide the matchs outcomes

At some point you need to *register* players as event participants. The seeding do not define who plays, it is only a matching tool during the event.
Then you need to run the competition and let the magic operate. You end up with a collection of games and a final standing.

**Note** It is not possible to specify the game mode - Competition produces Duel encounters. 


```python
from rstt import Player, SingleEliminationBracket

# more people more fun
competitors = Player.create(nb=16)

# one event 
tournament = SingleEliminationBracket(name='Example', seeding=btr, solver=BetterWin())

# add players - unseeded players are treated as being at the bottom of the ranking
tournament.registration(competitors)
print('Tournament Example started:', tournament.started(), 'ended:', tournament.over())

# automatic workflow
tournament.run()

# some cool 'get features'
print('Event has started:', tournament.started(),
      '\nEvent is live: ', tournament.live(),
      '\nEvent has finished:', tournament.over(),
      '\nA total of ', len(tournament.games()), 'games were played',
      '\nThe winner is:', tournament.top(1)[0].name(),
      '\nSeending do not define who participate: ', set(tournament.participants()) != set(btr.players()))
```

    Tournament Example started: False ended: False
    Event has started: True 
    Event is live:  False 
    Event has finished: True 
    A total of  15 games were played 
    The winner is: Eric Stone 
    Seending do not define who participate:  True



```python
# .games() return a list of SMatch, or a list of list if specified by rounds.
for i, round in enumerate(tournament.games(by_rounds=True)):
    print(f'Round {i+1}')
    for game in round:
        print(game.player1(), '- versus -', game.player2(), game.scores())
    print()
```

    Round 1
    Roy Melito - versus - Christopher Riddle [1.0, 0.0]
    Judy Bell - versus - John James [0.0, 1.0]
    Melba Reaves - versus - Eric Stone [0.0, 1.0]
    Mary Lindeman - versus - Frank Reed [1.0, 0.0]
    Nancy Obermiller - versus - Clarence Gutierrez [0.0, 1.0]
    Marie Ross - versus - Isaac Hang [0.0, 1.0]
    Michael Rhodes - versus - Crystal Levine [0.0, 1.0]
    Marsha Mcnally - versus - Gloria Hein [0.0, 1.0]
    
    Round 2
    Roy Melito - versus - John James [1.0, 0.0]
    Eric Stone - versus - Mary Lindeman [1.0, 0.0]
    Clarence Gutierrez - versus - Isaac Hang [1.0, 0.0]
    Crystal Levine - versus - Gloria Hein [1.0, 0.0]
    
    Round 3
    Roy Melito - versus - Eric Stone [0.0, 1.0]
    Clarence Gutierrez - versus - Crystal Levine [1.0, 0.0]
    
    Round 4
    Eric Stone - versus - Clarence Gutierrez [1.0, 0.0]
    



```python
# The standing is a dict[SPlayer, int] indicating the final placement of participants
tournament.standing()
```




    {Player - name: Christopher Riddle, level: 1422.1730698637937: 16,
     Player - name: Judy Bell, level: 1144.1287046178954: 16,
     Player - name: Melba Reaves, level: 1499.7034642194762: 16,
     Player - name: Frank Reed, level: 1255.764645335733: 16,
     Player - name: Nancy Obermiller, level: 505.23311632248215: 16,
     Player - name: Marie Ross, level: 1349.9002717856586: 16,
     Player - name: Michael Rhodes, level: 1572.8765080078756: 16,
     Player - name: Marsha Mcnally, level: 1377.9273555851837: 16,
     Player - name: John James, level: 1874.3127131433541: 8,
     Player - name: Mary Lindeman, level: 1687.514430881033: 8,
     Player - name: Isaac Hang, level: 1463.5917100418862: 8,
     Player - name: Gloria Hein, level: 1600.8192297704095: 8,
     Player - name: Roy Melito, level: 1995.2452069548683: 4,
     Player - name: Crystal Levine, level: 1603.932002691374: 4,
     Player - name: Clarence Gutierrez, level: 1810.7650548556942: 2,
     Player - name: Eric Stone, level: 2249.98213000531: 1}



#### Achievements

Player class differs from BasicPlayer by tracking their achievement in events. As a consequence, a Player can only participate in event with different names.


```python
player = competitors[0]
for achievement in player.achievements():
    print('event name:',achievement.event_name,
          f'\n{player.name()}', 'final placement:', achievement.place,
          '\nmoney earned in the event:', achievement.prize)
print('Total earnings in career:', player.earnings())
```

    event name: Example 
    John James final placement: 8 
    money earned in the event: 0
    Total earnings in career: 0



```python
# An example of simulation Error

# name='Example' is already used  in cell (5)
tournament2 = SingleEliminationBracket(name='Example', seeding=btr, solver=BetterWin())
tournament2.registration(competitors)
tournament2.run()
```


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    Cell In[9], line 6
          4 tournament2 = SingleEliminationBracket(name='Example', seeding=btr, solver=BetterWin())
          5 tournament2.registration(competitors)
    ----> 6 tournament2.run()


    File ~/Documents/GitHub/rstt/rstt/scheduler/tournament/competition.py:233, in Competition.run(self)
        231 self.start()
        232 self.play()
    --> 233 self.trophies()


    File ~/Documents/GitHub/rstt/rstt/scheduler/tournament/competition.py:315, in Competition.trophies(self)
        312 try:
        313     result = Achievement(
        314         self.__name, self.__standing[player], self.cashprize[self.__standing[player]])
    --> 315     player.collect(result)
        316 except AttributeError:
        317     continue


    File ~/Documents/GitHub/rstt/rstt/player/player.py:92, in collect(self, achievement)
         90 else:
         91     msg = f"Can not collect {achievement}. {self} already participated in an event called {achievement.event_name}"
    ---> 92     raise ValueError(msg)


    ValueError: Can not collect Achievement(event_name='Example', place=16, prize=0). Frank Reed already participated in an event called Example


#### Error Details

##### **Motivation**
RSTT is a powerfull package that enables production of multi millions games dataset in reasonable time. It is also meant for scientifical reseach, synthetic **data must be well defined** and strickly be the consequences of a specified model. Many errors raised by the package are annoying and seem unnecessary. They are here to ensure data integrity. They tell researcher and reviewer that something is not quiet right. 

##### **What happened ?**
At the very end of the Competition.run execution, paricipants *receive* an [Achievement](https://rstt.readthedocs.io/en/latest/rstt.html#rstt.stypes.Achievement), resulting in a ValueError raised by the player. You could execute multiple times the same event using BasicPlayer, since they do not track achievement, no error would occure.
The error is raised after all games have been played and a standing was decided and only by player tracking achievements. The problem is not the game, the players , the solver nor the competition handling. It just make no sense to host twice a **World Cup 2025**.

##### **What to do ?**
Either use BasicPlayer or a consistant naming convention for event. A formated string with an index in an enumerated for-loop works just fine.
Sometimes you realy, realy do need twice the exact same event with the same participants. In that case there is a player.reset() method, as an explicit syntax, that eraise object history.

## 6. Simulation

1) Specify a model specification. It consist in a population of player and a solver.
We consider 256 **Player** with a constant level in a probabilistic environement defined by the **[LogSolver](https://rstt.readthedocs.io/en/latest/_modules/rstt/solver/solvers.html#LogSolver)**.

2) Select a Ranking to test
We will use the famous **[Elo](https://rstt.readthedocs.io/en/latest/rstt.ranking.standard.html#module-rstt.ranking.standard.basicElo.BasicElo) rating system**.

3) Simulation Protocol. How do component interact with each. When do you play game and update a ranking. When do you update the player level or change solver ? The entire synthethic dataset production is under your control, inculding the inter-play between a test set and the training/validation set.
Let's keep it simple here. We play **one single swiss-sound tournament edition with initial random seed**. Then update our test ranking.
Typically a ranking under test has no prior information, i.e. all players have the same ratings and the ordering is assumed random.

4) Run
   
5) Evaluation:
What is fantastic with simulation is that you know the actual level of player and can compare infered ratings with the **groudtruth**.
Here we will compute rank differences between learned and model ranking. 


```python
from rstt import BasicElo, LogSolver, SwissRound, SingleEliminationBracket, RoundRobin

# 1. simulation model
players = Player.create(nb=256)
groundtruth = BTRanking('Ground Truth', players=players)
solver = LogSolver()

# 2. a ranking under test
test_ranking = BasicElo('Test Ranking', players=players)

# 33 & 4. a  dataset
tournament = SwissRound('One Event', groundtruth, solver)
tournament.registration(players)
tournament.run()

# 'train' ranking on dataset
test_ranking.update(games=tournament.games())
```


```python
import statistics

# 5. evaluation
rank_diff = [groundtruth[p]-test_ranking[p] for p in players]

# simple statistics
print('\nmean:',statistics.mean(rank_diff),
      '\nstandard deviation', statistics.stdev(rank_diff),
      '\nbiggest \'under-rating\' gap', max(rank_diff),
      '\nbiggest \'over-rating\' gap', abs(min(rank_diff))
     )
```

    
    mean: 0 
    standard deviation 30.461933815250564 
    biggest 'under-rating' gap 90 
    biggest 'over-rating' gap 98


## 7. Modularity

One of the greatest asset in RSTT is the modularity of its component. The following concepts:
Player, Solver, Scheduler and Ranking have different implementation available which are all inter-changeable. 

You can quickly switch model specification without breaking your simulation. For this reason it is often good practice to wrap your experimental protocol in a function taking the parameters as input. There is a stypes module that helps you typehint your functionalities.

**Note:** Most of the time the match mode is inherent to the problem or research question you are adressing and it rarely make sense to switch it.


```python
from rstt import Ranking, Competition
from rstt.stypes import SPlayer, SMatch, Solver


def rssc(players: list[SPlayer], ranking: Ranking, solver: Solver, tournament: Competition, depth: int) -> list[list[SMatch]]:
    """repeated self seeded cup
    
    A cup is seeded by a ranking.
    In turn the ranking is updated based on the cup games outcome.
    This Interplay is repeated many times.
    """

    dataset = []
    
    for i in range(depth):
        # play an event
        cup = tournament(name=f'rssc {i}', seeding=ranking, solver=solver)
        cup.registration(players)
        cup.run()

        # update ranking
        ranking.update(games=cup.games())
        
        # extend returned dataset
        dataset.append(cup.games())

    return dataset
```

## 8. Your Turn

Below is a collection of component for you to familiarize with and play arround. Do not forget to consult the documentation.


```python
# TODO CELL

from rstt.player import BasicPlayer, Player, GaussianPlayer, CyclePlayer, LogisticPlayer # noqa 401
from rstt.scheduler import SingleEliminationBracket, DoubleEliminationBracket, RoundRobin # noqa 401
from rstt import BasicElo, BasicGlicko # noqa 401
from rstt import BetterWin, CoinFlip, BradleyTerry, LogSolver # noqa 401


population = ...
solver = ...
ranking = ...
```

## 9. What else to learn

You enjoed this tutorial and want to discover more about the package features and applications. We have other tutorials for you to improve your skill in RSTT simulation research.


#### Tutorial 2: Integration

RSTT has its own **unique definition** of what a ranking is. You get a glimps of it in Tutorial 2. It is a powerfull one that allows you to integrate externally defined rating system within the RSTT framework.

In this tutorial you will build a simple ranking class that uses the [openskill](https://github.com/vivekjoshy/openskill.py) package to compute ratings within a RSTT simulation. The same approach can be extanded to [trueskill](https://trueskill.org) and probably any system you want to.



#### Tutorial 3: Research

In this tutorial, we reproduce a researched on the Elo ranking system. You will code some of the experimentation youself.
What you learn:
- Reproduce scientifical research
- How to read model specification and translate it into RSTT vocabulary and features
- Setup Experimental Protocol
- Make cool plot to vizualise simulation results


#### Tutorial 4: Modeling

RSTT allows you to design and implement custom component to combine. The design requirements are kept minimal thanks to high abstraction defining interaction and taking care of automation. We model here an entire professional video gam ecosystem (League of Legend), including ranking specfifcation and leagues structures with international events. We build a model to reflect both game title specificity and ranking consideration. We implement a naive baseline and perform a simple comparative study.

The tutorial also highlight some current limitation of the package, and how you can work arround to reach your goal. 

What you learn:
- Abstraction of components
- 'Deeper' functionalities
- Modeling
- Tips & Tricks from maintainer experiences
- Pitfall of simulation based research


```python

```
