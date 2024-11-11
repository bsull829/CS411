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
    return Meal(1, 'Meal 1', 'Japanese', 100, 'MED')

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

def test_battle(battle_model, sample_meal1, sample_combatants, mocker):
    """Test correct selecting of a winner and updating associated meal stats"""
    battle_model.combatants = [sample_meal1]
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

    battle_model.combatants = sample_combatants

    # Use mocker to mock update meal_stats and prevent database interaction
    mock_update_meal_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")

    battle_result = battle_model.battle()

    assert battle_result == 'Meal 1'
    "Expected meal 1 to win due to higher prices"

    "Check combatants to see if loser was removed"
    assert len(battle_model.combatants) == 1, "Expected only winner to remain"
    assert battle_model.combatants[0].id == 1, "Expected winning meal to remain"
    assert battle_model.combatants[0].price == 100, "Expected winning meal to remain (which is meal 2)"

    assert mock_update_meal_stats.call_count == 2

def test_battle_insufficient_combatants(battle_model, sample_meal1):
    """Test whether state of <2 combatants correctly raises an error"""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

##################################################
# Clear Combatants Test Cases
##################################################

def test_clear_combatants(battle_model, sample_combatants):
    """Test clearing a Battle Model object's nonempty combatants list"""
    battle_model.combatants = sample_combatants
    assert len(battle_model.combatants) == 2, "Expected 2 Meals to be in list"

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, f"Combatants should be empty after clearing"

def test_clear_empty_combatants(battle_model):
    """Test clearing a Battle Model object's empty combatants list"""
    
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected 0 Meals to be in empty list"

##################################################
# Getting Information Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test retrieving a calculated battle score from a certain Meal object"""
    difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
    retrieved_battle_score = battle_model.get_battle_score(sample_meal1)
    expected_battle_score = (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]

    assert retrieved_battle_score == expected_battle_score, "Make sure retrieved battle score is correct, after calculating manually"

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving existing list of combatants from a battle model"""
    battle_model.combatants = [sample_meal1, sample_meal2]
    retrieved_combatants = battle_model.get_combatants()

    assert len(retrieved_combatants) == 2, "Expected two combatants to be retrieved"

    "Checking combatant 1"
    assert retrieved_combatants[0].id == 1
    assert retrieved_combatants[0].meal == 'Meal 1'
    assert retrieved_combatants[0].cuisine == 'Japanese'
    assert retrieved_combatants[0].price == 100
    assert retrieved_combatants[0].difficulty == 'MED'

    "Checking combatant 2"
    assert retrieved_combatants[1].id == 2
    assert retrieved_combatants[1].meal == 'Meal 2'
    assert retrieved_combatants[1].cuisine == 'Japanese'
    assert retrieved_combatants[1].price == 110
    assert retrieved_combatants[1].difficulty == 'LOW'

##################################################
# Prepping combatant Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1, sample_meal2):
    """Test prepping a new combatant to be entered into the Battle Model"""

    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1, "Expected combatant to be successfully prepped and added to 'combatants' list"
    assert battle_model.combatants[0].meal == 'Meal 1', """Expected correct meal to be prepped and added"""

    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2, "Expected another combatant to be added to list"
    assert battle_model.combatants[1].meal == 'Meal 2', """Second meal should be appended to end of list"""

def test_prep_combatant_limit(battle_model, sample_combatants, sample_meal3, caplog):
    """Test prepping too many combatants"""
    battle_model.combatants = sample_combatants
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)








