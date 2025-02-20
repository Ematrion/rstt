from typing import Dict
import pytest

from rstt import Player, BTRanking
from rstt.scheduler.tournament.competition import Competition



class DummyCup(Competition):    
    def generate_games(self):
        return []

    def _end_of_stage(self) -> bool:
        return True
    
    def _standing(self) -> Dict[Player, int]:
        return {}

population = Player.create(nb=20)
competitors, spectators = population[:5], population[5:]
seeding = BTRanking('Seeding', players=population)

# --- test control variable --- #
def test_start_live():
    cup = DummyCup('test', seeding)
    cup.start()
    assert cup.live()

def test_not_live_after_play():
    cup = DummyCup('test', seeding)
    assert not cup.live()
    cup.start()
    assert cup.live()
    cup.play()
    assert not cup.live()

def test_run_after_state():
    cup = DummyCup('test', seeding)
    assert not cup.started() and not cup.live() and not cup.over()
    cup.run()
    assert cup.started() and not cup.live() and cup.over()
    
# --- test play mechanism --- #
def test_registration():
    cup = DummyCup('test', seeding)
    cup.registration(competitors)
    assert set(cup.participants) == set(competitors)
    
def test_registration_after_start():
    cup = DummyCup('test', seeding)
    cup._Competition__started = True
    cup.registration(competitors)
    assert set(cup.participants) == set()
    
def test_start_seeding():
    cup = DummyCup('test', seeding)
    cup.registration(competitors)
    assert set(cup.seeding) != set(cup.participants)
    cup.start()
    assert set(cup.seeding) == set(cup.participants)
    
def test_play_not_started():
    cup = DummyCup('test', seeding)
    with pytest.raises(RuntimeError):
        cup.play()

def test_run_already_started():
    cup = DummyCup('test', seeding)
    cup.start()
    with pytest.raises(RuntimeError):
        cup.run()


    
    
    
    

