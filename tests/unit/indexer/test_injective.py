import pytest
from unittest.mock import AsyncMock, patch
from src.indexer.injective import InjectiveIndexer
from pyinjective.async_client import AsyncClient
from datetime import datetime

@pytest.fixture
def mock_async_client():
    mock = AsyncMock(spec=AsyncClient)
    # Add required methods to the mock
    mock.fetch_spot_market_history = AsyncMock()
    mock.fetch_spot_market_info = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_injective_indexer_initialization():
    with patch('src.indexer.injective.AsyncClient') as mock_client:
        indexer = InjectiveIndexer(network="testnet")
        mock_client.assert_called_once_with("testnet")

@pytest.mark.asyncio
async def test_fetch_market_data(mock_async_client):
    with patch('src.indexer.injective.AsyncClient', return_value=mock_async_client):
        # Create indexer
        indexer = InjectiveIndexer(network="testnet")
        
        # Setup mock response
        mock_data = [
            {
                "timestamp": 1234567890,
                "price": "100.0",
                "volume": "1000.0",
                "liquidity": "10000.0"
            }
        ]
        mock_async_client.fetch_spot_market_history.return_value = mock_data
        
        # Execute test
        result = await indexer.get_price_history(
            "INJ/USDT",
            datetime.fromtimestamp(1234567890),
            datetime.fromtimestamp(1234567890)
        )
        
        # Verify results
        assert len(result) == 1
        assert result[0].price == 100.0
        assert result[0].volume_24h == 1000.0
        assert mock_async_client.fetch_spot_market_history.called

@pytest.mark.asyncio
async def test_get_liquidity_pools(mock_async_client):
    with patch('src.indexer.injective.AsyncClient', return_value=mock_async_client):
        # Create indexer
        indexer = InjectiveIndexer(network="testnet")
        
        # Setup mock response
        mock_data = {
            "pool_size": "10000.0",
            "base_volume": "1000.0",
            "quote_volume": "100000.0"
        }
        mock_async_client.fetch_spot_market_info.return_value = mock_data
        
        # Execute test
        result = await indexer.get_liquidity_pools("INJ/USDT")
        
        # Verify results
        assert result["pool_size"] == 10000.0
        assert result["base_volume"] == 1000.0
        assert result["quote_volume"] == 100000.0
        assert isinstance(result["last_updated"], datetime)
        assert mock_async_client.fetch_spot_market_info.called

@pytest.mark.asyncio
async def test_fetch_market_data_error_handling(mock_async_client):
    with patch('src.indexer.injective.AsyncClient', return_value=mock_async_client):
        # Create indexer
        indexer = InjectiveIndexer(network="testnet")
        
        # Setup mock error
        mock_async_client.fetch_spot_market_history.side_effect = Exception("API Error")
        
        # Execute test and verify error handling
        with pytest.raises(Exception) as exc_info:
            await indexer.get_price_history(
                "INJ/USDT",
                datetime.now(),
                datetime.now()
            )
        assert str(exc_info.value) == "API Error" 