"""Solver for simulation

The subpackage implements :class:`rstt.stypes.Solver` of different models.
Solver are responsible to produce a :class:`rstt.stypes.Score` and assign it to a :class:`rstt.stypes.SMatch`.

.. warning::
    The current version of RSTT only support Solver for the :class:`rstt.game.match.Duel` class.
    
    Solver for other match will be added in future version (as will other Match classes). 
    
    In the mean time, if you need help to write your own Solver, ask for advise on the RSTT `discord <https://discord.gg/CyB3Ptf3>`_
"""


from .solvers import BetterWin, BradleyTerry, LogSolver, CoinFlip, WIN, LOSE
