"""Module for Observer

Observer is a protocol providing a handle_observations() method for ranking.
This method is responsible:

    - to proprocess observations - parameters passed to :func:`rstt.ranking.ranking.Raning.update` justifying ratings changes.
    - properly call the ranking.backend :func:`rstt.stypes.Infere.rate`
    - store new ratings in the ranking.datamodel :class:`rstt.stypes.RatingSystem`
    
.. warning::
    Currently RSTT SMatch support is limited to the Duel class.
    This is also true for 'Game based' Observer. Typecheckers may look for SMatch and not for Duel.
    This can cause unexpected errors in your simulations.

"""

from .obs import ObsTemplate, NoHandling
from .gameObserver import GameByGame, BatchGame
from .playerObserver import PlayerChecker
