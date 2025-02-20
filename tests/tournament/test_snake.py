import pytest

from rstt import Player, BetterWin, BTRanking
from rstt.scheduler.tournament.snake import Snake


total = 128
population = Player.create(nb=total)
seeding = BTRanking('Seedings', players=population)
    
@pytest.mark.parametrize("nb", [i for i in range(2, total)]) 
def test_nb_games(nb):
    snake = Snake('test', seeding, BetterWin())
    snake.registration(population[:nb])
    snake.run()
    assert len(snake.games()) == nb-1

@pytest.mark.parametrize("nb", [i for i in range(2, total)]) 
def test_nb_rounds(nb):
    snake = Snake('test', seeding, BetterWin())
    snake.registration(population[:nb])
    snake.run()
    assert len(snake.games(by_rounds=True)) == nb-1
    
    