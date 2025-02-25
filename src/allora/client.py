from typing import Dict, Any, List
import aiohttp
from datetime import datetime

class AlloraClient:
    def __init__(self, api_key: str, base_url: str = "https://api.allora.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session

    async def close(self):
        """Close the client session"""
        if self._session:
            await self._session.close()
            self._session = None

    async def get_price_prediction(
        self,
        model_id: str,
        historical_data: List[Dict[str, Any]],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get price prediction from Allora API"""
        endpoint = f"{self.base_url}/predict/{model_id}"
        
        payload = {
            "historical_data": historical_data,
            "market_conditions": market_conditions
        }

        response = await self.session.post(endpoint, json=payload)
        if response.status != 200:
            error_text = await response.text()
            raise Exception(f"Allora API error: {error_text}")
        
        return await response.json() 