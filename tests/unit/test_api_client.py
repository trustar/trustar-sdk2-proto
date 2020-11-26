import pytest

from trustar.api_client import ApiClient
from trustar.trustar import TruStar


@pytest.fixture
def api_client():
    return ApiClient(TruStar("API_KEY", "API_SECRET", "TEST_METATAG"))


def test_get_token_successfully(api_client, mocked_auth):
    token = api_client._get_token()
    assert token == "TOKEN12345"


def test_get_headers(api_client, mocked_auth):
    headers = api_client._get_headers("POST")
    expected_headers = {
        "Authorization": "Bearer TOKEN12345",
        "Client-Metatag": "TEST_METATAG",
        "Client-Type": "PYTHON_SDK",
        "Client-Version": "1.0.0",
        "Content-Type": "application/json",
    }
    assert headers == expected_headers


def test_token_is_not_expired(api_client, mocker):
    mock_response = mocker.Mock(status_code=200)
    expired = api_client._token_is_expired(mock_response)
    assert expired == False


def test_token_is_expired(api_client, mocker):
    mock_response = mocker.Mock(
        status_code=400,
        json=lambda: {"error_description": "Expired oauth2 access token"},
    )
    expired = api_client._token_is_expired(mock_response)
    assert expired == True


def test_sleep_wait_time_lower_max_wait_time(api_client, mocker):
    mock_response = mocker.Mock(
        json=lambda: {"waitTime": 500},
    )
    keep_trying = api_client._sleep(mock_response)
    assert keep_trying == True


def test_sleep_wait_time_higher_max_wait_time(api_client, mocker):
    mock_response = mocker.Mock(
        json=lambda: {"waitTime": 65000},
    )
    keep_trying = api_client._sleep(mock_response)
    assert keep_trying == False