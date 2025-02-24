from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class PricePoint:
    timestamp: datetime
    dex_name: str
    token_pair: str
    price: float
    volume_24h: float
    liquidity: float

class DataIndexer(ABC):
    @abstractmethod
    async def get_price_history(
        self, 
        token_pair: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[PricePoint]:
        """Fetch historical price data for a token pair"""
        pass

    @abstractmethod
    async def get_liquidity_pools(
        self, 
        token_pair: str
    ) -> Dict[str, Any]:
        """Get liquidity pool information across DEXes"""
        pass 