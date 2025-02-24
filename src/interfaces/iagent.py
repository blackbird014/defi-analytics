from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pyinjective.composer import Composer
from pyinjective.wallet import Address

class IAgent(ABC):
    @abstractmethod
    async def initialize(self, composer: Composer, address: Address) -> None:
        """Initialize the agent with composer and address"""
        pass

    @abstractmethod
    async def execute(self) -> None:
        """Execute the agent's main trading logic"""
        pass

    @abstractmethod
    async def get_market_state(self) -> Dict[str, Any]:
        """Get current market state including orderbook, positions, etc."""
        pass

    @abstractmethod
    async def place_order(self, order_params: Dict[str, Any]) -> Optional[str]:
        """Place an order on Injective Exchange"""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get agent identifier"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get agent description"""
        pass 