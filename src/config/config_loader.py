from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import yaml
from pathlib import Path

@dataclass
class RiskParameters:
    max_position_size: float
    max_slippage: float
    stop_loss: float

@dataclass
class MarketConfig:
    id: str
    min_trade_size: float
    max_trade_size: float
    risk_parameters: RiskParameters

@dataclass
class InjectiveConfig:
    network: str
    api_key: str
    markets: List[MarketConfig]

@dataclass
class AlloraPredictionSettings:
    min_confidence: float
    time_horizon: int
    update_interval: int

@dataclass
class AlloraConfig:
    api_key: str
    model_id: str
    base_url: str
    confidence_level: float
    prediction_settings: AlloraPredictionSettings

@dataclass
class RiskManagement:
    portfolio_stop_loss: float
    max_daily_trades: int
    cooldown_period: int

@dataclass
class MonitoringConfig:
    update_interval: int
    min_profit_threshold: float
    max_active_positions: int
    risk_management: RiskManagement

@dataclass
class LoggingConfig:
    level: str
    file_path: str
    rotation: str
    retention: str

@dataclass
class Config:
    injective: InjectiveConfig
    allora: AlloraConfig
    monitoring: MonitoringConfig
    logging: LoggingConfig

class ConfigLoader:
    @staticmethod
    def load(config_path: str = "config/settings.yaml") -> Config:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Convert dictionary to dataclass instances
        injective_config = InjectiveConfig(
            network=config_dict["injective"]["network"],
            api_key=config_dict["injective"]["api_key"],
            markets=[
                MarketConfig(
                    id=market["id"],
                    min_trade_size=market["min_trade_size"],
                    max_trade_size=market["max_trade_size"],
                    risk_parameters=RiskParameters(
                        max_position_size=market["risk_parameters"]["max_position_size"],
                        max_slippage=market["risk_parameters"]["max_slippage"],
                        stop_loss=market["risk_parameters"]["stop_loss"]
                    )
                )
                for market in config_dict["injective"]["markets"]
            ]
        )

        allora_config = AlloraConfig(
            api_key=config_dict["allora"]["api_key"],
            model_id=config_dict["allora"]["model_id"],
            base_url=config_dict["allora"]["base_url"],
            confidence_level=config_dict["allora"]["confidence_level"],
            prediction_settings=AlloraPredictionSettings(
                min_confidence=config_dict["allora"]["prediction_settings"]["min_confidence"],
                time_horizon=config_dict["allora"]["prediction_settings"]["time_horizon"],
                update_interval=config_dict["allora"]["prediction_settings"]["update_interval"]
            )
        )

        monitoring_config = MonitoringConfig(
            update_interval=config_dict["monitoring"]["update_interval"],
            min_profit_threshold=config_dict["monitoring"]["min_profit_threshold"],
            max_active_positions=config_dict["monitoring"]["max_active_positions"],
            risk_management=RiskManagement(
                portfolio_stop_loss=config_dict["monitoring"]["risk_management"]["portfolio_stop_loss"],
                max_daily_trades=config_dict["monitoring"]["risk_management"]["max_daily_trades"],
                cooldown_period=config_dict["monitoring"]["risk_management"]["cooldown_period"]
            )
        )

        logging_config = LoggingConfig(
            level=config_dict["logging"]["level"],
            file_path=config_dict["logging"]["file_path"],
            rotation=config_dict["logging"]["rotation"],
            retention=config_dict["logging"]["retention"]
        )

        return Config(
            injective=injective_config,
            allora=allora_config,
            monitoring=monitoring_config,
            logging=logging_config
        )

    @staticmethod
    def validate_api_keys(config: Config) -> None:
        """Validate that API keys are provided"""
        if not config.injective.api_key:
            raise ValueError("Injective API key is required")
        if not config.allora.api_key:
            raise ValueError("Allora API key is required") 