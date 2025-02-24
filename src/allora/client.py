from typing import Dict, Any, List
import aiohttp
from datetime import datetime

class AlloraClient:
    def __init__(self, api_key: str, base_url: str = "https://api.allora.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_price_prediction(
        self,
        model_id: str,
        historical_data: List[Dict[str, Any]],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get price prediction from Allora API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use with 'async with'")

        endpoint = f"{self.base_url}/predict/{model_id}"
        
        payload = {
            "historical_data": historical_data,
            "market_conditions": market_conditions
        }

        async with self.session.post(endpoint, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Allora API error: {error_text}")
            
            return await response.json() 