from typing import List, Tuple, Any
from typeguard import typechecked


'''
This file deals with how Player faces each other


# ???: a decorator to raise error/warning for list of odd length
'''


# --- Shuffling --- #
def riffle_shuffle(half1: List[int], half2: List[int]) -> List[int]:
    return [half[i] for i in range(len(half1)) for half in [half1, half2]]


# --- Splitting --- #
def symetric_split(elems: List[int]) -> Tuple[List[int], List[int]]:
    h = len(elems)//2
    half1 = elems[:h]
    half2 = list(reversed(elems[-h:]))
    return half1, half2

def middle_split(elems: List[int]) -> Tuple[List[int], List[int]]:
    h = len(elems)//2
    half1 = elems[:h]
    half2 = elems[-h:]
    return half1, half2

def neighboor_split(elems: List[int]) -> Tuple[List[int], List[int]]:
    half1 = elems[::2]
    half2 = elems[1::2]
    return half1, half2

# --- matching --- #
def symetric_match(elems: List[Any]) -> List[List[Any]]:
    return [[elems[i], elems[-i]] for i in range(len(elems)//2)]

def parallel_match(elems: List[Any]) -> List[List[Any]]:
    h = len(elems)//2
    return [[elems[i], elems[h+i]] for i in range(h)]

def neighboor_match(elems: List[Any]) -> List[List[Any]]:
    return [[elems[2*i], elems[2*i+1]] for i in range(len(elems)//2)]

