import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_injective_client():
    return Mock()

@pytest.fixture
def mock_allora_client(mocker):
    mock = mocker.patch("src.allora.predictor.AlloraClient")
    mock.return_value.__aenter__.return_value = mock
    return mock

@pytest.fixture
def mock_response(mocker):
    return mocker.Mock()

@pytest.fixture
def aiohttp_client(mocker):
    mock_client = mocker.patch("aiohttp.ClientSession")
    return mock_client

@pytest.fixture
def sample_market_data():
    return {
        "INJ/USDT": {
            "price": 100.0,
            "volume": 1000000.0,
            "timestamp": "2024-03-14T12:00:00Z"
        },
        "ETH/USDT": {
            "price": 3000.0,
            "volume": 5000000.0,
            "timestamp": "2024-03-14T12:00:00Z"
        }
    } 