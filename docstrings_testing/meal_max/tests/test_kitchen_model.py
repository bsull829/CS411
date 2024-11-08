# Based on and modified from playlist.tests.test_song_model. 
from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import Meal

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
    def mock_get_deb_connection():
        yield mock_conn # Yield the mocked connection object
        
    return mock_conn # Yield the mock connection object 
    

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""
    pass

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""
    pass

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an price (e.g., negative price)"""
    pass
    
def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., not 'LOW', 'MED', or 'HIGH')."""
    pass

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the database by meal ID."""
    pass

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    pass

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""
    pass

######################################################
#
#    Get Leaderboard
#
######################################################

# get leaderboard's stub is a bit less straightforward than the others
# I'll be adding it later with unit test impementations but rn I'm busy 

# ADD LEADERBOARD STUB HERE     

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    pass

def test_get_meal_by_id_bad_id(mock_cursor):
    pass

def test_get_meal_by_name(mock_cursor):
    pass

def test_get_meal_by_id_bad_name(mock_cursor):
    pass

def test_update_meal_stats(mock_cursor):
    """Test updating the battle count and win count of a song."""
    # look into if one function is sufficient for updating battle count AND win count!!
    pass
    
### Test for Updating a Deleted Meal:
def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to battle count and win count for a deleted meal."""
    pass
    
def test_update_meal_stats_bad_result(mock_cursor):
    """Test error when trying to update meal stats with an invalid result, something that is not 'win' or 'loss'."""
    # something like this wasn't present in song model's test but it makes sense to add this 
    pass 
    

    





