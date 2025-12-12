"""
Port interface for LightRAG proxy client operations.
Defines the contract for proxying requests to the LightRAG API.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from domain.entities.lightrag_proxy_entities import (
    LightRAGProxyRequest,
    LightRAGProxyResponse,
)


class LightRAGProxyClientPort(ABC):
    """
    Port interface for LightRAG proxy client operations.
    Defines the contract for forwarding requests to the LightRAG API.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the proxy client connection."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the proxy client connection."""
        pass

    @abstractmethod
    async def forward_request(
        self,
        request: LightRAGProxyRequest,
    ) -> LightRAGProxyResponse:
        """
        Forward a request to the LightRAG API.

        Args:
            request: The proxy request containing method, path, body, params, headers.

        Returns:
            LightRAGProxyResponse: The response from the LightRAG API.
        """
        pass

    @abstractmethod
    def forward_stream(
        self,
        request: LightRAGProxyRequest,
    ) -> AsyncIterator[bytes]:
        """
        Forward a streaming request to the LightRAG API.

        Args:
            request: The proxy request containing method, path, body, params, headers.

        Yields:
            bytes: Chunks of the streaming response.
        """
        pass

    @abstractmethod
    async def get_openapi_spec(self) -> dict[str, Any]:
        """
        Fetch the OpenAPI specification from the LightRAG API.

        Returns:
            dict: The OpenAPI specification JSON.
        """
        pass
