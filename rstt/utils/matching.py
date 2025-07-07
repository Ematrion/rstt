from typing import List, Tuple, Any


# ----------------- #
# --- Shuffling --- #
# ----------------- #
def riffle_shuffle(half1: List[Any], half2: List[Any]) -> List[Any]:
    return [half[i] for i in range(len(half1)) for half in [half1, half2]]


# ----------------- #
# --- Splitting --- #
# ----------------- #
def symetric_split(elems: List[Any]) -> Tuple[List[Any], List[Any]]:
    h = len(elems)//2
    half1 = elems[:h]
    half2 = list(reversed(elems[-h:]))
    return half1, half2


def middle_split(elems: List[Any]) -> Tuple[List[Any], List[Any]]:
    h = len(elems)//2
    half1 = elems[:h]
    half2 = elems[-h:]
    return half1, half2


def neighboor_split(elems: List[Any]) -> Tuple[List[Any], List[Any]]:
    half1 = elems[::2]
    half2 = elems[1::2]
    return half1, half2


# ---------------- #
# --- matching --- #
# ---------------- #
def symetric_match(elems: List[Any]) -> List[List[Any]]:
    return [[elems[i], elems[-i]] for i in range(len(elems)//2)]


def parallel_match(elems: List[Any]) -> List[List[Any]]:
    h = len(elems)//2
    return [[elems[i], elems[h+i]] for i in range(h)]


def neighboor_match(elems: List[Any]) -> List[List[Any]]:
    return [[elems[2*i], elems[2*i+1]] for i in range(len(elems)//2)]


# --------------- #
# --- Common ---- #
# --------------- #
def ruban(players: List[Any]) -> List[List[Any]]:
    if len(players) % 2 == 0:
        return _ruban_even(players)
    else:
        return _ruban_odd(players)


def _ruban_even(players: List[Any]) -> List[List[Any]]:
    # QUEST: does it work with odd length of players input ?
    # QUEST: return List[List[List[Any]]] to match other matching func logic ?
    '''
    implement 'clock-like' algorithm, source:
    https://en.wikipedia.org/wiki/File:Round-robin_tournament_10teams_en.png
    '''

    # prevent side-effect due to .pop() usage
    players = [player for player in players]

    # return value
    rounds = []

    # algorithm variable - num10 in the ref .png
    fix = players.pop(len(players)-1)

    # control variables
    r = 1  # current round
    # expected len(rounds) - total amount of rounds
    nb = len(players)-1 if len(players) % 2 == 0 else len(players)

    # build rounds one-by-one
    while r <= nb:

        # round[r-1]
        new_round = []
        # num1, 2, 3, ...
        flex = players.pop(0)

        # first we deal with the special match
        if r % 2 == 0:
            # duel := Duel(flex, fix)
            new_round.append(flex)
            new_round.append(fix)
        else:
            # duel := Duel(fix, flex)
            new_round.append(fix)
            new_round.append(flex)

        # then with the ruban
        half = len(players)//2
        half1 = players[:half]
        half2 = players[half:]
        half2.reverse()
        for index, (p1, p2) in enumerate(zip(half1, half2)):
            if index % 2 == 0:
                # duel = Match(p2,p1)
                new_round.append(p2)
                new_round.append(p1)
            else:
                # duel = Match(p1,p2)
                new_round.append(p1)
                new_round.append(p2)

        # update variable
        rounds.append(new_round)
        r += 1
        players.append(flex)

    return rounds


def _ruban_odd(players: List[Any]) -> List[List[Any]]:
    # each player get a BYE round
    BYE = None
    # avoid side- effect
    players = [player for player in players]
    players.append(BYE)
    rounds = _ruban_even(players)
    for round in rounds:
        for p1, p2 in zip(*neighboor_split(round)):
            if not p1 or not p2:
                round.remove(p1)
                round.remove(p2)

    return rounds


def chord_diagrams_n6(players: List[Any]) -> List[List[Any]]:
    '''
    source:
    https://en.wikipedia.org/wiki/Double_factorial
    https://en.wikipedia.org/wiki/Chord_diagram_(mathematics)

    NOTE: I do not know a algorithm to compute it for an abritrary n=2*k (in reseaonable complexity)
    But n=6 is a frequent needs in SwissBracket for 16 players variations so I hard coded the 15 solutions
    '''

    if len(players) != 6:
        msg = f'chord_diagrams_n6 function is implemented only for 6 participants, len(players) = {len(players)})'
        raise ValueError(msg)

    matchings = [
        [players[0], players[5], players[1], players[4], players[2], players[3]],
        [players[0], players[5], players[1], players[5], players[2], players[4]],
        [players[0], players[4], players[1], players[5], players[2], players[3]],
        [players[0], players[2], players[1], players[4], players[3], players[5]],
        [players[0], players[3], players[1], players[4], players[2], players[5]],

        [players[0], players[1], players[2], players[5], players[3], players[4]],
        [players[0], players[2], players[1], players[2], players[4], players[5]],
        [players[0], players[4], players[1], players[2], players[3], players[5]],
        [players[0], players[3], players[1], players[5], players[2], players[4]],
        [players[0], players[5], players[1], players[2], players[3], players[4]],

        [players[0], players[3], players[1], players[2], players[4], players[5]],
        [players[0], players[2], players[1], players[5], players[3], players[4]],
        [players[0], players[1], players[2], players[4], players[3], players[5]],
        [players[0], players[4], players[1], players[3], players[2], players[5]],
        [players[0], players[1], players[2], players[3], players[4], players[5]],
    ]
    return matchings


def swiss_bracket_n6(players: List[Any]) -> List[List[Any]]:
    '''
    Source : https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md
    Look for the 'Priority' table in section 'Swiss Bracket'
    '''

    if len(players) != 6:
        msg = f'swiss_bracket_n6 function is implemented only for 6 participants, len(players) = {len(players)})'
        raise ValueError(msg)

    matchings = [
        [players[0], players[5], players[1], players[4], players[2], players[3]],
        [players[0], players[5], players[1], players[3], players[2], players[4]],
        [players[0], players[4], players[1], players[5], players[2], players[3]],
        [players[0], players[4], players[1], players[3], players[2], players[5]],
        [players[0], players[3], players[1], players[5], players[2], players[4]],

        [players[0], players[3], players[1], players[4], players[2], players[5]],
        [players[0], players[5], players[1], players[2], players[3], players[4]],
        [players[0], players[4], players[1], players[2], players[3], players[5]],
        [players[0], players[2], players[1], players[5], players[3], players[4]],
        [players[0], players[2], players[1], players[4], players[3], players[5]],

        [players[0], players[3], players[1], players[2], players[4], players[5]],
        [players[0], players[2], players[1], players[3], players[4], players[5]],
        [players[0], players[1], players[2], players[5], players[3], players[4]],
        [players[0], players[1], players[2], players[4], players[3], players[5]],
        [players[0], players[1], players[2], players[3], players[4], players[5]],
    ]
    return matchings
