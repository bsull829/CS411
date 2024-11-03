import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()

def battle_model():
    """Fixture to provide a new instance of Battle Model for each test"""
    return BattleModel()

"""Fixtures providing sample meals for the tests."""
@pytest.fixture()
def sample_meal1():
    return Meal(1, 'Sushi', 'Japanese', 100, 'MED')

@pytest.fixture()
def sample_meal2():
    return Meal(2, 'Meal 2', 'Japanese', 110, 'LOW')

@pytest.fixture()
def sample_meal3():
    return Meal(3, 'Meal 3', 'Cuisine 3', 120, 'HIGH')

@pytest.fixture()
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Battle Test Cases
##################################################

def test_battle(battle_model, sample_meal1, sample_combatants):
    battle_model.combatants = [sample_meal1]
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

    battle_model.combatants = sample_combatants
    battle_result = battle_model.battle()

    assert battle_result == 'Meal 2', "Expected meal 2 to win due to higher prices"

    "Check combatants to see if loser was removed"
    assert len(battle_model.combatants) == 1, "Expected only winner to remain"
    assert battle_model.combatants[0].id == 2, "Expected winning meal to remain"
    assert battle_model.combatants[0].price == 110, "Expected winning meal to remain (which is meal 2)"

##################################################
# Clear Combatants Test Cases
##################################################

def test_clear_combatants(battle_model, sample_combatants):
    """Test clearing a Battle Model object's combatants"""
    battle_model.combatants = sample_combatants
    assert len(battle_model.combatants) == 2, "Expected 2 Meals to be in list"

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, f"Combatants should be empty after clearing"

def test_clear_empty_combatants(battle_model, caplog):
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected 0 Meals to be in empty list"
    assert "Clearing empty combatants" in caplog.text, "Expected warning message when clearing empty combatants list"

##################################################
# Getting Information Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test retrieving a calculated battle score from a certain Meal object"""
    retrieved_battle_score = battle_model.get_battle_score(sample_meal1)

    assert type(retrieved_battle_score) == float, "Make sure score is a float, not an integer"
    assert retrieved_battle_score == 798, "Make sure retrieved battle score is correct, after calculating manually"

def test_get_combatants(battle_model):
    """Test retrieving existing list of combatants from a battle model"""
    battle_model.combatants = sample_combatants
    retrieved_combatants = battle_model.get_combatants()

    assert len(retrieved_combatants) == len(battle_model.combatants) == 2, "Expected two combatants to be retrieved"

    "Checking combatant 1"
    assert retrieved_combatants[0].id == 1
    assert retrieved_combatants[0].meal == 'Sushi'
    assert retrieved_combatants[0].cuisine == 'Japanese'
    assert retrieved_combatants[0].price == 100
    assert retrieved_combatants[0].difficulty == 'MED'

    "Checking combatant 2"
    assert retrieved_combatants[1].id == 2
    assert retrieved_combatants[1].meal == 'Meal 2'
    assert retrieved_combatants[1].cuisine == 'Japanese'
    assert retrieved_combatants[1].price == 110
    assert retrieved_combatants[1].difficulty == 'Difficulty 2'


##################################################
# Prepping combatant Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1, sample_meal2):
    """Test prepping a new combatant to be entered into the Battle Model"""

    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1, "Expected combatant to be successfully prepped and added to 'combatants' list"
    assert battle_model.combatants[0].meal == 'Sushi', """Expected correct meal to be prepped and added"""

    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2, "Expected another combatant to be added to list"
    assert battle_model.combatants[1].meal == 'Meal 2', """Second meal should be appended to end of list"""

def test_prep_combatant_limit(battle_model, sample_combatants, sample_meal3, caplog):
    """Test prepping too many combatants"""
    battle_model.combatants = sample_combatants
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

def test_prep_combatant_duplicate(battle_model, sample_meal1, caplog):
    battle_model.combatants = [sample_meal1]
    battle_model.prep_combatant(sample_meal1)

    assert "Added duplicate combatant" in caplog.text, "Expected warning message when adding two of the same meals"






