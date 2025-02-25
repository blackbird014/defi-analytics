from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta

from .interfaces import PricePredictor, PricePoint
from .client import AlloraClient

class AlloraPredictor(PricePredictor):
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize Allora predictor with configuration
        
        Args:
            model_config: Dictionary containing:
                - api_key: Allora API key
                - model_id: ID of the prediction model to use
                - base_url: Optional base URL for Allora API
                - confidence_level: Confidence level for intervals (default: 0.95)
        """
        self.model_config = model_config
        self.api_key = model_config["api_key"]
        self.model_id = model_config["model_id"]
        self.base_url = model_config.get("base_url", "https://api.allora.com/v1")
        self.confidence_level = model_config.get("confidence_level", 0.95)
        
    async def predict_price_movement(
        self, 
        historical_data: List[PricePoint],
        current_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Predict future price movements using Allora's API
        
        Args:
            historical_data: List of historical price points
            current_state: Current market conditions and state
            
        Returns:
            Dictionary containing prediction details:
                - predicted_price: float
                - confidence: float
                - direction: str ('up' or 'down')
                - timestamp: datetime
        """
        # Format historical data for Allora API
        formatted_data = [
            {
                "timestamp": point.timestamp.isoformat(),
                "price": point.price,
                "volume": point.volume,
                "pair": point.pair
            }
            for point in historical_data
        ]

        try:
            client = AlloraClient(self.api_key, self.base_url)
            prediction = await client.get_price_prediction(
                self.model_id,
                formatted_data,
                current_state
            )
            
            confidence_interval = self.get_confidence_interval(
                prediction["predicted_price"],
                current_state
            )
            
            await client.close()
            
            return {
                "predicted_price": prediction["predicted_price"],
                "confidence": prediction["confidence"],
                "direction": "up" if prediction["predicted_price"] > historical_data[-1].price else "down",
                "timestamp": datetime.now(),
                "confidence_interval": confidence_interval
            }
                
        except Exception as e:
            raise Exception(f"Failed to get prediction from Allora: {str(e)}")

    def get_confidence_interval(
        self, 
        prediction: float, 
        market_conditions: Dict[str, Any]
    ) -> tuple[float, float]:
        """
        Calculate confidence intervals for predictions
        
        Args:
            prediction: Predicted price value
            market_conditions: Current market conditions
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Get volatility from market conditions or use default
        volatility = market_conditions.get("volatility", 0.02)
        
        # Calculate interval based on volatility and confidence level
        z_score = {
            0.95: 1.96,
            0.99: 2.576,
            0.90: 1.645
        }.get(self.confidence_level, 1.96)
        
        margin = prediction * volatility * z_score
        
        return (prediction - margin, prediction + margin) 