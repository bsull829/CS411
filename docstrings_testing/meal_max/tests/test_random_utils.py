import pytest
import requests

from meal_max.utils.random_utils import get_random

"Random number to test against"
RANDOM_NUMB = 0.99

@pytest.fixture
def mock_random_org(mocker):
    #Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mock_response.text = f"{RANDOM_NUMB}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org): 
    """Test retrieval of random number in correct format from random.org"""

    result = get_random()

    assert result == RANDOM_NUMB, f"Expected {RANDOM_NUMB} but got {result} instead"

    """Ensure that correct URL is used to fetch result"""
    requests.get.assert_called_once_with("https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new", timeout=5)

def test_get_random_timeout(mocker):
    """Simulate a request timeout"""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_fail(mocker): 
    """Simulate a request failure to URL"""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_invalid(mock_random_org): 
    """Simulate an invalid input response"""
    mock_random_org.text = "invalid_response"

    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()
