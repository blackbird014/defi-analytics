from typing import Dict, Any, List
from src.interfaces.ihttp_client import IHttpClient
from src.http.aiohttp_client import AioHttpClient

class AlloraClient:
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.allora.com/v1",
        http_client: IHttpClient = None
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.http_client = http_client or AioHttpClient(
            default_headers={"Authorization": f"Bearer {api_key}"}
        )

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

        return await self.http_client.post(endpoint, payload)

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.close() 