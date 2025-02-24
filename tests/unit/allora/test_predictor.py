import pytest
from datetime import datetime, timedelta
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
    market_conditions,
    mock_allora_client,
    monkeypatch
):
    # Mock the AlloraClient
    mock_prediction = {
        "predicted_price": 150.0,
        "confidence": 0.85
    }
    mock_allora_client.get_price_prediction.return_value = mock_prediction

    predictor = AlloraPredictor(allora_config)
    
    result = await predictor.predict_price_movement(
        sample_price_points,
        market_conditions
    )
    
    assert result["predicted_price"] == 150.0
    assert result["confidence"] == 0.85
    assert "direction" in result
    assert "confidence_interval" in result
    assert isinstance(result["confidence_interval"], tuple)

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
    market_conditions,
    mock_allora_client
):
    mock_allora_client.get_price_prediction.side_effect = Exception("API Error")
    
    predictor = AlloraPredictor(allora_config)
    
    with pytest.raises(Exception) as exc_info:
        await predictor.predict_price_movement(sample_price_points, market_conditions)
    assert "Failed to get prediction from Allora" in str(exc_info.value) 