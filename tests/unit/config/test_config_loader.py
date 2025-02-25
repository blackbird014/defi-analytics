import pytest
from pathlib import Path
from src.config.config_loader import ConfigLoader, Config

@pytest.fixture
def sample_config_path(tmp_path):
    config_content = """
injective:
  network: "testnet"
  api_key: "test_injective_key"
  markets:
    - id: "INJ/USDT"
      min_trade_size: 100
      max_trade_size: 10000
      risk_parameters:
        max_position_size: 5000
        max_slippage: 0.01
        stop_loss: 0.02

allora:
  api_key: "test_allora_key"
  model_id: "price_prediction_v1"
  base_url: "https://api.allora.com/v1"
  confidence_level: 0.95
  prediction_settings:
    min_confidence: 0.8
    time_horizon: 3600
    update_interval: 300

monitoring:
  update_interval: 60
  min_profit_threshold: 0.01
  max_active_positions: 3
  risk_management:
    portfolio_stop_loss: 0.05
    max_daily_trades: 50
    cooldown_period: 300

logging:
  level: "INFO"
  file_path: "logs/trading.log"
  rotation: "1 day"
  retention: "30 days"
"""
    config_file = tmp_path / "test_settings.yaml"
    config_file.write_text(config_content)
    return str(config_file)

def test_config_loader_loads_valid_config(sample_config_path):
    config = ConfigLoader.load(sample_config_path)
    
    assert isinstance(config, Config)
    assert config.injective.network == "testnet"
    assert config.injective.api_key == "test_injective_key"
    assert len(config.injective.markets) == 1
    
    market = config.injective.markets[0]
    assert market.id == "INJ/USDT"
    assert market.min_trade_size == 100
    assert market.max_trade_size == 10000
    
    assert config.allora.api_key == "test_allora_key"
    assert config.allora.model_id == "price_prediction_v1"
    assert config.allora.prediction_settings.time_horizon == 3600
    
    assert config.monitoring.update_interval == 60
    assert config.monitoring.risk_management.portfolio_stop_loss == 0.05
    
    assert config.logging.level == "INFO"
    assert config.logging.rotation == "1 day"

def test_config_loader_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("nonexistent.yaml")

def test_validate_api_keys_missing_injective(sample_config_path):
    config = ConfigLoader.load(sample_config_path)
    config.injective.api_key = ""
    
    with pytest.raises(ValueError, match="Injective API key is required"):
        ConfigLoader.validate_api_keys(config)

def test_validate_api_keys_missing_allora(sample_config_path):
    config = ConfigLoader.load(sample_config_path)
    config.allora.api_key = ""
    
    with pytest.raises(ValueError, match="Allora API key is required"):
        ConfigLoader.validate_api_keys(config) 