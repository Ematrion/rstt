from rstt import Player, Match, Duel, BradleyTerry


# create two player
p1 = Player(name='Achille', level=2000)
p2 = Player(name='Hector', level=1500)

# create a match
match = Match(teams=[[p1],[p2]])
duel = Duel(player1=p1, player2=p2)

# test some getter
print(duel.player1(), duel.player2())
print(duel.opponent(duel.player1()))


# print
print(match)
print(duel)

# play the match
BradleyTerry().solve(duel)

# print
print(match)
print(duel)