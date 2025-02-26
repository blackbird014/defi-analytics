import aiohttp
from typing import Dict, Any, Optional
from src.interfaces.ihttp_client import IHttpClient

class AioHttpClient(IHttpClient):
    def __init__(self, default_headers: Optional[Dict[str, str]] = None):
        self._session = None
        self.default_headers = default_headers or {}

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.default_headers)
        return self._session

    async def post(
        self, 
        endpoint: str, 
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a POST request using aiohttp"""
        request_headers = {**self.default_headers, **(headers or {})}
        
        async with self.session.post(endpoint, json=payload, headers=request_headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"HTTP error {response.status}: {error_text}")
            
            return await response.json()

    async def close(self) -> None:
        """Close the aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None 