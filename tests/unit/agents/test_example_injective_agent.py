import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.example_injective_agent import ExampleInjectiveAgent
from src.config import Config, MarketConfig, RiskParameters

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.logging = MagicMock()
    config.logging.level = "INFO"
    config.allora = MagicMock()
    config.allora.prediction_settings = MagicMock()
    config.allora.prediction_settings.min_confidence = 0.8
    config.monitoring = MagicMock()
    config.monitoring.min_profit_threshold = 0.01
    return config

@pytest.fixture
def mock_market_config():
    return MarketConfig(
        id="INJ/USDT",
        min_trade_size=100,
        max_trade_size=10000,
        risk_parameters=RiskParameters(
            max_position_size=5000,
            max_slippage=0.01,
            stop_loss=0.02
        )
    )

@pytest.fixture
def mock_orderbook():
    return {
        "bids": [
            {"price": "99.5", "quantity": "100"},
            {"price": "99.0", "quantity": "200"},
        ],
        "asks": [
            {"price": "100.5", "quantity": "150"},
            {"price": "101.0", "quantity": "300"},
        ]
    }

@pytest.fixture
def mock_prediction():
    return {
        "predicted_price": 102.0,
        "confidence": 0.95,
        "direction": "up",
        "timestamp": datetime.now()
    }

@pytest.fixture
def agent(mock_config, mock_market_config):
    agent = ExampleInjectiveAgent(mock_config, mock_market_config)
    agent.composer = AsyncMock()
    agent.address = MagicMock()
    agent.address.get_subaccount_id.return_value = "subaccount123"
    agent.address.to_acc_bech32.return_value = "inj123"
    return agent

@pytest.mark.asyncio
async def test_get_market_state(mock_config, mock_market_config, mock_orderbook):
    agent = ExampleInjectiveAgent(mock_config, mock_market_config)
    agent.composer = AsyncMock()
    agent.composer.fetch_spot_orderbook.return_value = mock_orderbook
    
    state = await agent.get_market_state()
    
    assert state["orderbook"] == mock_orderbook
    assert state["market_id"] == "INJ/USDT"
    assert isinstance(state["timestamp"], datetime)

@pytest.mark.asyncio
async def test_execute_with_valid_prediction(agent, mock_orderbook):
    # Setup market state mock
    current_price = 100.0
    agent.get_market_state = AsyncMock(return_value={
        "orderbook": mock_orderbook,
        "timestamp": datetime.now(),
        "market_id": "INJ/USDT"
    })
    
    # Setup historical prices
    agent.historical_prices = []
    agent._update_historical_prices = MagicMock()
    
    # Setup Allora predictor mock
    agent.allora_predictor = AsyncMock()
    agent.allora_predictor.predict_price_movement = AsyncMock(return_value={
        "predicted_price": 102.0,
        "confidence": 0.95,
        "direction": "up",
        "timestamp": datetime.now()
    })
    
    # Setup helper method mocks
    agent._get_mid_price = MagicMock(return_value=current_price)
    agent._get_available_liquidity = MagicMock(return_value=1000.0)
    agent._should_place_order = MagicMock(return_value=True)  # Ensure order should be placed
    agent._create_order_params = MagicMock(return_value={
        "price": current_price,
        "size": 500.0,
        "type": "LIMIT",
        "is_buy": True
    })
    
    # Explicitly set up place_order mock
    agent.place_order = AsyncMock()
    agent.can_trade = MagicMock(return_value=True)  # Ensure trading is allowed
    
    # Execute agent
    await agent.execute()
    
    # Verify order placement was attempted
    agent.place_order.assert_called_once()
    
    # Additional verification of order parameters
    order_params = agent.place_order.call_args[0][0]
    assert order_params["is_buy"] is True
    assert order_params["type"] == "LIMIT"
    assert isinstance(order_params["price"], float)
    assert isinstance(order_params["size"], float)
    assert order_params["size"] <= agent.market_config.max_trade_size

@pytest.mark.asyncio
async def test_execute_low_confidence_no_trade(mock_config, mock_market_config, mock_orderbook):
    agent = ExampleInjectiveAgent(mock_config, mock_market_config)
    
    # Setup mocks
    agent.get_market_state = AsyncMock(return_value={
        "orderbook": mock_orderbook,
        "timestamp": datetime.now(),
        "market_id": "INJ/USDT"
    })
    agent.allora_predictor = AsyncMock()
    agent.allora_predictor.predict_price_movement = AsyncMock(return_value={
        "predicted_price": 102.0,
        "confidence": 0.5  # Low confidence
    })
    agent.place_order = AsyncMock()
    
    # Execute agent
    await agent.execute()
    
    # Verify no order was placed
    agent.place_order.assert_not_called()

def test_get_mid_price(mock_config, mock_market_config, mock_orderbook):
    agent = ExampleInjectiveAgent(mock_config, mock_market_config)
    mid_price = agent._get_mid_price(mock_orderbook)
    assert mid_price == 100.0  # (99.5 + 100.5) / 2

def test_should_place_order(mock_config, mock_market_config):
    agent = ExampleInjectiveAgent(mock_config, mock_market_config)
    
    # Test case: Profit above threshold
    assert agent._should_place_order(
        {"predicted_price": 101.5},
        current_price=100.0
    ) is True
    
    # Test case: Profit below threshold
    assert agent._should_place_order(
        {"predicted_price": 100.5},
        current_price=100.0
    ) is False

def test_get_available_liquidity(agent, mock_orderbook):
    # Test buy side liquidity
    buy_liquidity = agent._get_available_liquidity(mock_orderbook, is_buy=True)
    assert buy_liquidity == 450.0  # 150 + 300
    
    # Test sell side liquidity
    sell_liquidity = agent._get_available_liquidity(mock_orderbook, is_buy=False)
    assert sell_liquidity == 300.0  # 100 + 200 