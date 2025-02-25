import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from src.allora.predictor import AlloraPredictor
from src.allora.interfaces import PricePoint

@pytest.fixture
def allora_config():
    return {
        "api_key": "test_api_key",
        "model_id": "test_model",
        "confidence_level": 0.95
    }

@pytest.fixture
def sample_price_points():
    return [
        PricePoint(
            timestamp=datetime.now() - timedelta(hours=i),
            price=100.0 + i,
            volume=1000.0,
            pair="INJ/USDT"
        )
        for i in range(24, 0, -1)
    ]

@pytest.fixture
def market_conditions():
    return {
        "volatility": 0.02,
        "market_trend": "bullish",
        "trading_volume": 1000000.0
    }

@pytest.fixture
def mock_allora_client():
    mock = AsyncMock()
    mock.get_price_prediction = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_predictor_initialization(allora_config):
    predictor = AlloraPredictor(allora_config)
    assert predictor.api_key == "test_api_key"
    assert predictor.model_id == "test_model"
    assert predictor.confidence_level == 0.95

@pytest.mark.asyncio
async def test_price_prediction(
    allora_config,
    sample_price_points,
    market_conditions
):
    with patch('src.allora.predictor.AlloraClient') as mock_client_class:
        # Setup mock client
        mock_client = AsyncMock()
        mock_prediction = {
            "predicted_price": 150.0,
            "confidence": 0.85
        }
        mock_client.get_price_prediction.return_value = mock_prediction
        mock_client_class.return_value = mock_client
        mock_client.__aenter__.return_value = mock_client

        predictor = AlloraPredictor(allora_config)
        
        result = await predictor.predict_price_movement(
            sample_price_points,
            market_conditions
        )
        
        assert result["predicted_price"] == 150.0
        assert result["confidence"] == 0.85
        assert "direction" in result
        assert isinstance(result["direction"], str)
        mock_client.get_price_prediction.assert_called_once()

@pytest.mark.asyncio
async def test_confidence_interval(allora_config, market_conditions):
    predictor = AlloraPredictor(allora_config)
    prediction = 100.0
    
    lower, upper = predictor.get_confidence_interval(prediction, market_conditions)
    
    assert lower < prediction
    assert upper > prediction
    assert upper - lower > 0

@pytest.mark.asyncio
async def test_error_handling(
    allora_config,
    sample_price_points,
    market_conditions
):
    with patch('src.allora.predictor.AlloraClient') as mock_client_class:
        # Setup mock client with error
        mock_client = AsyncMock()
        mock_client.get_price_prediction.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        mock_client.__aenter__.return_value = mock_client
        
        predictor = AlloraPredictor(allora_config)
        
        with pytest.raises(Exception) as exc_info:
            await predictor.predict_price_movement(
                sample_price_points,
                market_conditions
            )
        assert "Failed to get prediction from Allora" in str(exc_info.value) 