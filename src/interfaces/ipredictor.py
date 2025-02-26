from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class PricePoint:
    def __init__(self, timestamp: datetime, price: float, volume: float, pair: str):
        self.timestamp = timestamp
        self.price = price
        self.volume = volume
        self.pair = pair

class IPredictor(ABC):
    @abstractmethod
    async def predict_price_movement(
        self, 
        historical_data: List[PricePoint],
        current_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Predict future price movements
        
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
        pass 