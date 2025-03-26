"""Modues defining SMatch

SMatch are the notion of game/match, competitive confrontation. It is more of a ponctual event with an outcome rather than a game with its own set of rules and mechanics.
SMatch have participants, accessed by the method :func:`rstt.game.match.Match.players` and the result - a :class:`rstt.stypes.Score` returned by the method :func:`rstt.game.match.Match.scores`
"""


from .match import Match, Duel
