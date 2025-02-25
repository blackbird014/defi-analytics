from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..indexer.interfaces import DataIndexer
from ..allora.predictor import AlloraPredictor
import asyncio

@dataclass
class MispricingOpportunity:
    token_pair: str
    dex_a: str
    dex_b: str
    price_difference: float
    confidence: float
    estimated_profit: float
    liquidity_constraints: Dict[str, Any]

class MispricingAnalyzer:
    def __init__(self, indexers: List[DataIndexer], allora_predictor: AlloraPredictor):
        self.indexers = indexers
        self.predictor = allora_predictor

    async def analyze_pair(
        self, 
        token_pair: str, 
        timeframe: tuple[datetime, datetime]
    ) -> List[MispricingOpportunity]:
        """Analyze price differences between DEXes"""
        # Get historical data from all indexers
        price_histories = await asyncio.gather(*[
            indexer.get_price_history(token_pair, *timeframe)
            for indexer in self.indexers
        ])
        
        # Get current liquidity data
        liquidity_data = await asyncio.gather(*[
            indexer.get_liquidity_pools(token_pair)
            for indexer in self.indexers
        ])
        
        # Get price predictions
        predictions = await self.predictor.predict_price_movement(
            price_histories[0],  # Using first indexer as reference
            {"liquidity": liquidity_data}
        )
        
        # Find mispricing opportunities
        opportunities = []
        for i, dex_a in enumerate(self.indexers):
            for j, dex_b in enumerate(self.indexers[i+1:], i+1):
                if opportunity := self.calculate_arbitrage_opportunity(
                    {
                        dex_a.__class__.__name__: price_histories[i][-1].price,
                        dex_b.__class__.__name__: price_histories[j][-1].price
                    },
                    {
                        dex_a.__class__.__name__: liquidity_data[i]["pool_size"],
                        dex_b.__class__.__name__: liquidity_data[j]["pool_size"]
                    },
                    token_pair
                ):
                    opportunities.append(opportunity)
        
        return opportunities

    def calculate_arbitrage_opportunity(
        self, 
        prices: Dict[str, float], 
        liquidity: Dict[str, float],
        token_pair: str
    ) -> Optional[MispricingOpportunity]:
        """Calculate if there's a viable arbitrage opportunity"""
        dex_a, dex_b = list(prices.keys())
        price_diff = abs(prices[dex_a] - prices[dex_b])
        price_ratio = price_diff / min(prices.values())
        
        # Minimum thresholds
        MIN_PRICE_RATIO = 0.01  # 1% difference
        MIN_LIQUIDITY = 10000   # $10k minimum liquidity
        
        if price_ratio > MIN_PRICE_RATIO and all(liq > MIN_LIQUIDITY for liq in liquidity.values()):
            return MispricingOpportunity(
                token_pair=token_pair,
                dex_a=dex_a,
                dex_b=dex_b,
                price_difference=price_diff,
                confidence=0.95,  # Could be calculated based on historical accuracy
                estimated_profit=price_diff * min(liquidity.values()),
                liquidity_constraints={
                    "max_trade_size": min(liquidity.values()),
                    "slippage_estimate": 0.001  # This should be calculated based on liquidity
                }
            )
        return None 