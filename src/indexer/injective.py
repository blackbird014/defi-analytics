from datetime import datetime
from typing import List, Dict, Any
from src.interfaces.iblockchain_client import IBlockchainClient
from src.blockchain.injective_client import InjectiveClient
from .interfaces import DataIndexer, PricePoint

class InjectiveIndexer(DataIndexer):
    def __init__(self, client: IBlockchainClient = None, network: str = "mainnet"):
        self.client = client or InjectiveClient(network)
    
    async def get_price_history(
        self, 
        token_pair: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[PricePoint]:
        """Fetch historical price data"""
        raw_data = await self.client.fetch_market_history(
            market_id=token_pair,
            from_time=start_time,
            to_time=end_time
        )
        
        return [
            PricePoint(
                timestamp=datetime.fromtimestamp(entry["timestamp"]),
                dex_name="Injective",
                token_pair=token_pair,
                price=float(entry["price"]),
                volume_24h=float(entry["volume"]),
                liquidity=float(entry["liquidity"])
            )
            for entry in raw_data
        ]

    async def get_liquidity_pools(
        self, 
        token_pair: str
    ) -> Dict[str, Any]:
        """Get liquidity pool information"""
        pool_data = await self.client.fetch_market_info(
            market_id=token_pair
        )
        
        return {
            "pool_size": float(pool_data["pool_size"]),
            "base_volume": float(pool_data["base_volume"]),
            "quote_volume": float(pool_data["quote_volume"]),
            "last_updated": datetime.now()
        } 