from datetime import datetime
from typing import Dict, Any, List
from pyinjective.async_client import AsyncClient
from src.interfaces.iblockchain_client import IBlockchainClient

class InjectiveClient(IBlockchainClient):
    def __init__(self, network: str = "mainnet"):
        self.client = AsyncClient(network)

    async def fetch_market_history(
        self,
        market_id: str,
        from_time: datetime,
        to_time: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch historical market data from Injective"""
        raw_data = await self.client.fetch_spot_market_history(
            market_id=market_id,
            from_time=int(from_time.timestamp()),
            to_time=int(to_time.timestamp())
        )
        return raw_data

    async def fetch_market_info(
        self,
        market_id: str
    ) -> Dict[str, Any]:
        """Fetch current market information from Injective"""
        return await self.client.fetch_spot_market_info(
            market_id=market_id
        ) 