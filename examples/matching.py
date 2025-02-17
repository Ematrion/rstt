from rstt.utils.matching import *
import itertools


elems = [i for i in range(16)]

print('--- splits ---')
print('middle', middle_split(elems))
print('neighboor', neighboor_split(elems))
print('symetric', symetric_split(elems))

splits = {'symetric': symetric_split,
          'middle': middle_split,
          'neighboor': neighboor_split}
shuffles = {'riffle': riffle_shuffle}

for split, shuffle in itertools.product(list(splits.keys()), list(shuffles.keys())):
    print(split, shuffle)
    print(shuffles[shuffle](*splits[split](elems)))
    
print('tree_match', tree_match(elems))
print('speedup', speedup_match(elems))
