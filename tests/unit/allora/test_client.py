import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from src.allora.client import AlloraClient

@pytest.mark.asyncio
async def test_client_initialization():
    client = AlloraClient("test_key", "https://test.api.com")
    assert client.api_key == "test_key"
    assert client.base_url == "https://test.api.com"
    assert client._session is None

@pytest.mark.asyncio
async def test_get_prediction():
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"predicted_price": 100.0}
    
    # Mock session
    mock_session = AsyncMock()
    mock_session.post.return_value = mock_response
    
    # Create client and patch session property
    client = AlloraClient("test_key")
    with patch.object(AlloraClient, 'session', new_callable=PropertyMock) as mock_session_prop:
        mock_session_prop.return_value = mock_session
        
        result = await client.get_price_prediction(
            "test_model",
            [{"timestamp": "2024-03-14T12:00:00Z"}],
            {"volatility": 0.02}
        )
        
        assert result["predicted_price"] == 100.0
        mock_session.post.assert_called_once()
        await client.close()

@pytest.mark.asyncio
async def test_api_error():
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.text.return_value = "Bad Request"
    
    # Mock session
    mock_session = AsyncMock()
    mock_session.post.return_value = mock_response
    
    # Create client and patch session property
    client = AlloraClient("test_key")
    with patch.object(AlloraClient, 'session', new_callable=PropertyMock) as mock_session_prop:
        mock_session_prop.return_value = mock_session
        
        with pytest.raises(Exception) as exc_info:
            await client.get_price_prediction(
                "test_model",
                [],
                {}
            )
        
        assert "Allora API error" in str(exc_info.value)
        mock_session.post.assert_called_once()
        await client.close() 