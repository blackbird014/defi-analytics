import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.allora.client import AlloraClient
from src.interfaces.ihttp_client import IHttpClient

@pytest.mark.asyncio
async def test_client_initialization():
    mock_http_client = AsyncMock(spec=IHttpClient)
    client = AlloraClient("test_key", "https://test.api.com", http_client=mock_http_client)
    assert client.api_key == "test_key"
    assert client.base_url == "https://test.api.com"
    assert client.http_client == mock_http_client

@pytest.mark.asyncio
async def test_get_prediction():
    # Mock HTTP client
    mock_http_client = AsyncMock(spec=IHttpClient)
    mock_http_client.post.return_value = {"predicted_price": 100.0}
    
    # Create client with mock HTTP client
    client = AlloraClient("test_key", http_client=mock_http_client)
    
    result = await client.get_price_prediction(
        "test_model",
        [{"timestamp": "2024-03-14T12:00:00Z"}],
        {"volatility": 0.02}
    )
    
    assert result["predicted_price"] == 100.0
    mock_http_client.post.assert_called_once()
    await client.close()

@pytest.mark.asyncio
async def test_api_error():
    # Mock HTTP client with error
    mock_http_client = AsyncMock(spec=IHttpClient)
    mock_http_client.post.side_effect = Exception("HTTP error 400: Bad Request")
    
    # Create client with mock HTTP client
    client = AlloraClient("test_key", http_client=mock_http_client)
    
    with pytest.raises(Exception) as exc_info:
        await client.get_price_prediction(
            "test_model",
            [],
            {}
        )
    
    assert "HTTP error" in str(exc_info.value)
    mock_http_client.post.assert_called_once()
    await client.close() 