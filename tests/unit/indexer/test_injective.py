import pytest
from src.indexer.injective import InjectiveIndexer

@pytest.mark.asyncio
async def test_injective_indexer_initialization(mock_injective_client):
    indexer = InjectiveIndexer(client=mock_injective_client)
    assert indexer.client == mock_injective_client

@pytest.mark.asyncio
async def test_fetch_market_data(mock_injective_client, sample_market_data):
    # Arrange
    mock_injective_client.get_market_data.return_value = sample_market_data
    indexer = InjectiveIndexer(client=mock_injective_client)
    
    # Act
    result = await indexer.fetch_market_data(["INJ/USDT"])
    
    # Assert
    assert result["INJ/USDT"]["price"] == 100.0
    mock_injective_client.get_market_data.assert_called_once_with(["INJ/USDT"])

@pytest.mark.asyncio
async def test_fetch_market_data_error_handling(mock_injective_client):
    # Arrange
    mock_injective_client.get_market_data.side_effect = Exception("API Error")
    indexer = InjectiveIndexer(client=mock_injective_client)
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await indexer.fetch_market_data(["INJ/USDT"])
    assert str(exc_info.value) == "API Error" 