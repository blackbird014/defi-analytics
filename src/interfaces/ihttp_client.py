from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IHttpClient(ABC):
    @abstractmethod
    async def post(
        self, 
        endpoint: str, 
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the specified endpoint
        
        Args:
            endpoint: The URL endpoint to post to
            payload: The data to send in the request body
            headers: Optional headers to include in the request
            
        Returns:
            Response data as a dictionary
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections"""
        pass 