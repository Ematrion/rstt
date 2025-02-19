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

def ruban(players: List[Any]) -> List[List[Any]]:
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

    # algorithm variable
    fix = players.pop(len(players)-1) # num10 in the ref .png

    # control variables
    r = 1  # current round
    nb = len(players)-1 if len(players) % 2 == 0 else len(players) # expected len(rounds) - total amount of rounds
    
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


