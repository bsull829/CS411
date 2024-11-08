# Based on and modified from playlist.tests.test_song_model. 
from contextlib import contextmanager
import re
import sqlite3
"b"
import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None
    
    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn # Yield the mocked connection object
        
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test
    

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""
    
    # Call the function to create a new meal
    create_meal(meal="Meal Name", cuisine="Cuisine", price=12.0, difficulty="LOW")
    
    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine", 12.0, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Meal Name' already exists"):
        create_meal(meal="Meal Name", cuisine="Cuisine", price=12.0, difficulty="LOW")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an price (e.g., negative price)"""
    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -18. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine", price=-18, difficulty="LOW")

    # Attempt to create a meal with a non-integer price
    with pytest.raises(ValueError, match="Invalid price: invalid. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine", price="invalid", difficulty="LOW")
    
def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., not 'LOW', 'MED', or 'HIGH')."""
    # Attempt to create a meal with a difficulty that's not 'LOW', 'MED', or 'HIGH' 
    with pytest.raises(ValueError, match="Invalid difficulty level: Orange. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine", price=18, difficulty="Orange")

    # Attempt to create a difficulty with a non-string value 
    with pytest.raises(ValueError, match="Invalid difficulty level: 4. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine", price=18, difficulty=4)

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the database by meal ID."""
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""
    
    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

######################################################
#
#    Get Leaderboard
#
######################################################

def test_get_leaderboard_sort_by_wins(mock_cursor):
    """Test retrieving all meals constituting a leaderboard, sorted based on wins."""

    # Simulate leaderboard rows
    mock_cursor.fetchall.return_value = [
        (2, "Meal B", "Cuisine B", 2021, "LOW", 180, 20, 0.5),
        (1, "Meal A", "Cuisine A", 2020, "MED", 210, 10, 0.7),
        (3, "Meal C", "Cuisine C", 2022, "HIGH", 200, 5, 0.6)
    ]

    # Call the get_leaderboard function with sort_by = "wins"
    meals = get_leaderboard(sort_by="wins")

    # Ensure the results are sorted by win count
    expected_result = [
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 2021, "difficulty": "LOW", "battles": 180, "wins": 20, "win_pct": 50.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 2020, "difficulty": "MED", "battles": 210, "wins": 10, "win_pct": 70.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 2022, "difficulty": "HIGH", "battles": 200, "wins": 5, "win_pct": 60.0}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
def test_get_leaderboard_sort_by_win_pct(mock_cursor):
    """Test retrieving all meals constituting a leaderboard, sorted based on win percentages."""

    # Simulate leaderboard rows
    mock_cursor.fetchall.return_value = [
        (2, "Meal B", "Cuisine B", 2021, "LOW", 180, 20, 0.5),
        (1, "Meal A", "Cuisine A", 2020, "MED", 210, 10, 0.7),
        (3, "Meal C", "Cuisine C", 2022, "HIGH", 200, 5, 0.6)
    ]

    # Call the get_leaderboard function with sort_by = "wins"
    meals = get_leaderboard(sort_by="win_pct")

    # Ensure the results are sorted by win count
    expected_result = [
        {"id": 2, "meal": "Meal B", "cuisine": "Cuisine B", "price": 2021, "difficulty": "LOW", "battles": 180, "wins": 20, "win_pct": 50.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Cuisine A", "price": 2020, "difficulty": "MED", "battles": 210, "wins": 10, "win_pct": 70.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Cuisine C", "price": 2022, "difficulty": "HIGH", "battles": 200, "wins": 5, "win_pct": 60.0}
    ]

    assert meals == expected_result, f"Expected {expected_result}, but got {meals}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test error when trying to get leaderboard with an invalid sort_by (e.g., not 'wins' or 'win_pct')."""
    # Attempt to get leaderboard a sort_by that's not 'wins' or 'win_pct'
    with pytest.raises(ValueError, match="Invalid sort_by parameter: flower"):
        get_leaderboard("flower")

    # Attempt to get leaderboard with a sort_by that's a non-string value 
    with pytest.raises(ValueError, match="Invalid sort_by parameter: 4"):
        get_leaderboard(4)

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine", 18.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(id=1, meal="Meal Name", cuisine="Cuisine", price=18.0, difficulty="LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_already_deleted(mock_cursor):
    """Test error when trying to delete a meal by id that's already marked as deleted."""
    
    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = (999, "Meal Name", "Cuisine Name", 18.0, "LOW", True)

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        get_meal_by_id(999)
    

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (meal name = "Meal Name")
    mock_cursor.fetchone.return_value = (1, "Breakfast", "Cuisine", 18.0, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_name("Breakfast")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(id=1, meal="Breakfast", cuisine="Cuisine", price=18.0, difficulty="LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Breakfast",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given name
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name Breakfast not found"):
        get_meal_by_name("Breakfast")

def test_get_meal_by_name_already_deleted(mock_cursor):
    """Test error when trying to delete a meal by name that's already marked as deleted."""
    
    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = (999, "Lunch", "Cuisine Name", 18.0, "LOW", True)

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with name Lunch has been deleted"):
        get_meal_by_name("Lunch")

def test_update_meal_stats_result_win(mock_cursor):
    """Test updating the battle count and win count of a meal whose result is 'win'."""
    
    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with the "win" result 
    meal_id = 1
    update_meal_stats(meal_id, "win")
    
    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_result_loss(mock_cursor):
    """Test updating the battle count and win count of a meal whose result is 'loss'."""
    
    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with the "loss" result 
    meal_id = 1
    update_meal_stats(meal_id, "loss")
    
    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""UPDATE meals SET battles = battles + 1 WHERE id = ?""")

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
### Test for Updating a Deleted Meal:
def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to battle count and win count for a deleted meal."""
    
    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))
    
def test_update_meal_stats_invalid_result(mock_cursor):
    """Test error when trying to update meal stats with an invalid result (e.g., not 'win' or 'loss')."""
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])
    
    # Attempt to update meal stats with a result that's not 'win' or 'loss'
    with pytest.raises(ValueError, match="Invalid result: orange. Expected 'win' or 'loss'."):
        update_meal_stats(1, "orange")

    # Attempt to update meal stats with a result that's a non-string value 
    with pytest.raises(ValueError, match="Invalid result: 4. Expected 'win' or 'loss'."):
        update_meal_stats(1, 4)

def test_update_meal_stats_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        update_meal_stats(999, "win")
    
    

    





