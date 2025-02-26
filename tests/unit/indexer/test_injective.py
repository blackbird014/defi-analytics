import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from src.indexer.injective import InjectiveIndexer
from src.interfaces.iblockchain_client import IBlockchainClient

@pytest.fixture
def mock_blockchain_client():
    client = AsyncMock(spec=IBlockchainClient)
    return client

@pytest.mark.asyncio
async def test_injective_indexer_initialization(mock_blockchain_client):
    indexer = InjectiveIndexer(client=mock_blockchain_client)
    assert indexer.client == mock_blockchain_client

@pytest.mark.asyncio
async def test_fetch_market_data(mock_blockchain_client):
    # Create indexer with mock client
    indexer = InjectiveIndexer(client=mock_blockchain_client)
    
    # Setup mock response
    mock_data = [
        {
            "timestamp": 1234567890,
            "price": "100.0",
            "volume": "1000.0",
            "liquidity": "10000.0"
        }
    ]
    mock_blockchain_client.fetch_market_history.return_value = mock_data
    
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
    mock_blockchain_client.fetch_market_history.assert_called_once()

@pytest.mark.asyncio
async def test_get_liquidity_pools(mock_blockchain_client):
    # Create indexer with mock client
    indexer = InjectiveIndexer(client=mock_blockchain_client)
    
    # Setup mock response
    mock_data = {
        "pool_size": "10000.0",
        "base_volume": "1000.0",
        "quote_volume": "100000.0"
    }
    mock_blockchain_client.fetch_market_info.return_value = mock_data
    
    # Execute test
    result = await indexer.get_liquidity_pools("INJ/USDT")
    
    # Verify results
    assert result["pool_size"] == 10000.0
    assert result["base_volume"] == 1000.0
    assert result["quote_volume"] == 100000.0
    assert isinstance(result["last_updated"], datetime)
    mock_blockchain_client.fetch_market_info.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_market_data_error_handling(mock_blockchain_client):
    # Create indexer with mock client
    indexer = InjectiveIndexer(client=mock_blockchain_client)
    
    # Setup mock error
    mock_blockchain_client.fetch_market_history.side_effect = Exception("API Error")
    
    # Execute test and verify error handling
    with pytest.raises(Exception) as exc_info:
        await indexer.get_price_history(
            "INJ/USDT",
            datetime.now(),
            datetime.now()
        )
    assert str(exc_info.value) == "API Error" 