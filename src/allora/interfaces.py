from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PricePoint:
    timestamp: datetime
    price: float
    volume: float
    pair: str

class PricePredictor(ABC):
    @abstractmethod
    async def predict_price_movement(
        self, 
        historical_data: List[PricePoint],
        current_state: Dict[str, Any]
    ) -> Dict[str, float]:
        """Predict future price movements based on historical data and current state"""
        pass

    @abstractmethod
    def get_confidence_interval(
        self, 
        prediction: float, 
        market_conditions: Dict[str, Any]
    ) -> tuple[float, float]:
        """Calculate confidence intervals for predictions"""
        pass 