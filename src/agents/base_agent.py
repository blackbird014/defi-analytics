from abc import ABC
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pyinjective.composer import Composer
from pyinjective.wallet import Address

from src.interfaces.iagent import IAgent
from src.config import Config, MarketConfig

class BaseAgent(IAgent, ABC):
    def __init__(self, config: Config, market_config: MarketConfig):
        """Initialize base agent with configuration

        Args:
            config: Global configuration object
            market_config: Market-specific configuration
        """
        self.config = config
        self.market_config = market_config
        self.composer = None
        self.address = None
        self.last_trade_time = None
        self.daily_trades = 0
        self.active_positions = 0
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure logging based on config"""
        logging.basicConfig(
            level=self.config.logging.level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config.logging.file_path
        )

    async def initialize(self, composer: Composer, address: Address) -> None:
        """Initialize the agent with Injective composer and address"""
        self.composer = composer
        self.address = address
        self.logger.info(f"Initialized agent for market {self.market_config.id}")

    def can_trade(self) -> bool:
        """Check if agent can trade based on constraints"""
        # Check cooldown period
        if (self.last_trade_time and 
            (datetime.now() - self.last_trade_time).total_seconds() < 
            self.config.monitoring.risk_management.cooldown_period):
            self.logger.debug("Agent in cooldown period")
            return False

        # Check daily trade limit
        if (self.daily_trades >= 
            self.config.monitoring.risk_management.max_daily_trades):
            self.logger.debug("Daily trade limit reached")
            return False

        # Check active positions limit
        if (self.active_positions >= 
            self.config.monitoring.max_active_positions):
            self.logger.debug("Maximum active positions reached")
            return False

        return True

    def validate_order_size(self, size: float, price: float) -> bool:
        """Validate order size against configuration limits"""
        if size < self.market_config.min_trade_size:
            self.logger.warning(f"Order size {size} below minimum {self.market_config.min_trade_size}")
            return False
        
        if size > self.market_config.max_trade_size:
            self.logger.warning(f"Order size {size} above maximum {self.market_config.max_trade_size}")
            return False

        if size * price > self.market_config.risk_parameters.max_position_size:
            self.logger.warning("Order would exceed maximum position size")
            return False

        return True

    def update_trade_metrics(self) -> None:
        """Update trading metrics after successful trade"""
        self.last_trade_time = datetime.now()
        self.daily_trades += 1
        self.active_positions += 1

    def reset_daily_metrics(self) -> None:
        """Reset daily trading metrics"""
        self.daily_trades = 0

    async def get_market_state(self) -> Dict[str, Any]:
        """Get current market state"""
        if not self.composer:
            raise ValueError("Agent not initialized")
        
        try:
            orderbook = await self.composer.fetch_spot_orderbook(
                self.market_config.id
            )
            return {
                "orderbook": orderbook,
                "timestamp": datetime.now(),
                "market_id": self.market_config.id
            }
        except Exception as e:
            self.logger.error(f"Error fetching market state: {e}")
            raise

    async def place_order(self, order_params: Dict[str, Any]) -> Optional[str]:
        """Place an order with validation"""
        if not self.can_trade():
            return None

        if not self.validate_order_size(
            order_params.get("size", 0), 
            order_params.get("price", 0)
        ):
            return None

        try:
            tx_hash = await self.composer.submit_spot_order(
                market_id=self.market_config.id,
                subaccount_id=self.address.get_subaccount_id(),
                fee_recipient=self.address.to_acc_bech32(),
                price=order_params["price"],
                quantity=order_params["size"],
                order_type=order_params.get("type", "LIMIT"),
                is_buy=order_params["is_buy"]
            )
            
            if tx_hash:
                self.update_trade_metrics()
                self.logger.info(f"Order placed successfully: {tx_hash}")
            
            return tx_hash
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        if not self.composer:
            raise ValueError("Agent not initialized")
        
        try:
            await self.composer.cancel_spot_order(
                market_id=self.market_config.id,
                order_id=order_id
            )
            self.active_positions -= 1
            self.logger.info(f"Order cancelled successfully: {order_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False 