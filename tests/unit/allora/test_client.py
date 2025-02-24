import pytest
from src.allora.client import AlloraClient

@pytest.mark.asyncio
async def test_client_initialization():
    client = AlloraClient("test_key", "https://test.api.com")
    assert client.api_key == "test_key"
    assert client.base_url == "https://test.api.com"

@pytest.mark.asyncio
async def test_client_context_manager():
    async with AlloraClient("test_key") as client:
        assert client.session is not None

@pytest.mark.asyncio
async def test_get_prediction(aiohttp_client, mock_response):
    mock_response.json.return_value = {"predicted_price": 100.0}
    mock_response.status = 200
    
    async with AlloraClient("test_key") as client:
        result = await client.get_price_prediction(
            "test_model",
            [{"timestamp": "2024-03-14T12:00:00Z"}],
            {"volatility": 0.02}
        )
        
        assert result["predicted_price"] == 100.0

@pytest.mark.asyncio
async def test_api_error(aiohttp_client, mock_response):
    mock_response.status = 400
    mock_response.text.return_value = "Bad Request"
    
    async with AlloraClient("test_key") as client:
        with pytest.raises(Exception) as exc_info:
            await client.get_price_prediction(
                "test_model",
                [],
                {}
            )
        assert "Allora API error" in str(exc_info.value) 