from rstt import Player, Match, BradleyTerry


# create two player
p1 = Player(name='Achille', level=2000)
p2 = Player(name='Hector', level=1500)

# create a match
match = Match(teams=[[p1],[p2]])

# print
print(match)

# play the match
BradleyTerry().solve(match)

# print
print(match)