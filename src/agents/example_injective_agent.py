from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pyinjective.composer import Composer
from pyinjective.wallet import Address

from src.config import Config, MarketConfig
from src.interfaces.ipredictor import IPredictor, PricePoint
from src.allora.predictor import AlloraPredictor
from .base_agent import BaseAgent

class ExampleInjectiveAgent(BaseAgent):
    def __init__(
        self, 
        config: Config, 
        market_config: MarketConfig,
        predictor: Optional[IPredictor] = None
    ):
        """Initialize the example agent with configuration and predictor

        Args:
            config: Global configuration object
            market_config: Market-specific configuration
            predictor: Price prediction implementation (optional)
        """
        super().__init__(config, market_config)
        
        # Create default predictor if none provided
        if predictor is None:
            predictor = AlloraPredictor(
                model_config={
                    "api_key": config.allora.api_key,
                    "model_id": config.allora.model_id,
                    "base_url": config.allora.base_url,
                    "confidence_level": config.allora.confidence_level
                }
            )
        self.predictor = predictor
        self.historical_prices: List[PricePoint] = []

    async def execute(self) -> None:
        """Execute trading strategy using predictions"""
        try:
            # Get current market state
            market_state = await self.get_market_state()
            current_price = self._get_mid_price(market_state["orderbook"])
            
            # Update historical prices
            self._update_historical_prices(current_price)
            
            # Get prediction
            prediction = await self.predictor.predict_price_movement(
                self.historical_prices,
                market_state
            )
            
            # Check if prediction meets confidence threshold
            if prediction["confidence"] < self.config.allora.prediction_settings.min_confidence:
                self.logger.info(f"Prediction confidence {prediction['confidence']} below threshold")
                return
            
            # Determine trade direction and size
            if self._should_place_order(prediction, current_price):
                order_params = self._create_order_params(
                    prediction, 
                    current_price,
                    market_state
                )
                await self.place_order(order_params)
        
        except Exception as e:
            self.logger.error(f"Error in execute: {e}")

    def _update_historical_prices(self, current_price: float) -> None:
        """Update historical price list for predictions"""
        current_point = PricePoint(
            timestamp=datetime.now(),
            price=current_price,
            volume=0.0,  # We don't have volume data in this example
            pair=self.market_config.id
        )
        
        # Keep only recent history based on prediction time horizon
        cutoff_time = datetime.now() - timedelta(
            seconds=self.config.allora.prediction_settings.time_horizon
        )
        
        self.historical_prices = [
            point for point in self.historical_prices 
            if point.timestamp > cutoff_time
        ]
        self.historical_prices.append(current_point)

    def _should_place_order(
        self, 
        prediction: Dict[str, Any],
        current_price: float
    ) -> bool:
        """Determine if we should place an order based on prediction"""
        price_change = (prediction["predicted_price"] - current_price) / current_price
        min_profit = self.config.monitoring.min_profit_threshold
        
        # Only trade if predicted profit exceeds threshold
        return abs(price_change) > min_profit

    def _create_order_params(
        self,
        prediction: Dict[str, Any],
        current_price: float,
        market_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create order parameters based on prediction"""
        is_buy = prediction["predicted_price"] > current_price
        
        # Calculate position size based on confidence and risk parameters
        base_size = (
            self.market_config.risk_parameters.max_position_size * 
            prediction["confidence"]
        )
        
        # Adjust size based on available liquidity
        size = min(
            base_size,
            self.market_config.max_trade_size,
            self._get_available_liquidity(market_state["orderbook"], is_buy)
        )
        
        return {
            "price": current_price,
            "size": size,
            "type": "LIMIT",
            "is_buy": is_buy
        }

    def _get_mid_price(self, orderbook: Dict[str, Any]) -> float:
        """Calculate mid price from orderbook"""
        best_bid = float(orderbook["bids"][0]["price"]) if orderbook["bids"] else 0
        best_ask = float(orderbook["asks"][0]["price"]) if orderbook["asks"] else 0
        
        if not best_bid or not best_ask:
            raise ValueError("Invalid orderbook state")
            
        return (best_bid + best_ask) / 2

    def _get_available_liquidity(
        self, 
        orderbook: Dict[str, Any], 
        is_buy: bool
    ) -> float:
        """Calculate available liquidity for the trade"""
        orders = orderbook["asks"] if is_buy else orderbook["bids"]
        return sum(float(order["quantity"]) for order in orders[:3])  # Look at top 3 levels

    def get_name(self) -> str:
        return f"Example Injective Agent - {self.market_config.id}"

    def get_description(self) -> str:
        return "An example agent implementing the Injective Protocol with predictions" 