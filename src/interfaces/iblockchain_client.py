from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class IBlockchainClient(ABC):
    @abstractmethod
    async def fetch_market_history(
        self,
        market_id: str,
        from_time: datetime,
        to_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical market data
        
        Args:
            market_id: The market identifier
            from_time: Start time for historical data
            to_time: End time for historical data
            
        Returns:
            List of market data points
        """
        pass

    @abstractmethod
    async def fetch_market_info(
        self,
        market_id: str
    ) -> Dict[str, Any]:
        """
        Fetch current market information
        
        Args:
            market_id: The market identifier
            
        Returns:
            Current market information
        """
        pass 