"""
Use case for proxying requests to the LightRAG API.
Implements business logic for the LightRAG proxy functionality.
"""

import logging
from typing import AsyncIterator
from domain.ports.lightrag_proxy_client import LightRAGProxyClientPort
from domain.entities.lightrag_proxy_entities import (
    LightRAGProxyRequest,
    LightRAGProxyResponse,
)

logger = logging.getLogger(__name__)


class LightRAGProxyUseCase:
    """
    Use case for proxying requests to the LightRAG API.
    Handles the business logic of request forwarding to LightRAG.
    """

    # Paths that support streaming responses
    STREAMING_PATHS = [
        "query/stream",
        "api/generate",
        "api/chat",
    ]

    def __init__(self, proxy_client: LightRAGProxyClientPort):
        """
        Initialize the LightRAG proxy use case.

        Args:
            proxy_client: The LightRAG proxy client port implementation.
        """
        self.proxy_client = proxy_client

    def is_streaming_request(self, request: LightRAGProxyRequest) -> bool:
        """
        Determine if a request should use streaming response.

        Args:
            request: The proxy request to check.

        Returns:
            bool: True if the request should stream, False otherwise.
        """
        # Check if path matches streaming endpoints
        path_supports_streaming = any(sp in request.path for sp in self.STREAMING_PATHS)

        if not path_supports_streaming:
            return False

        # Only POST requests can stream
        if request.method != "POST":
            return False

        # Check if stream is explicitly enabled in body
        if isinstance(request.body, dict):
            return request.body.get("stream", True)

        return True

    async def execute(self, request: LightRAGProxyRequest) -> LightRAGProxyResponse:
        """
        Execute a non-streaming proxy request to LightRAG.

        Args:
            request: The proxy request to forward.

        Returns:
            LightRAGProxyResponse: The response from LightRAG API.

        Raises:
            Exception: If the request fails.
        """
        logger.debug(f"Proxying to LightRAG: {request.method} /{request.path}")

        try:
            response = await self.proxy_client.forward_request(request)
            logger.debug(
                f"LightRAG response: {response.status_code} for {request.method} /{request.path}"
            )
            return response
        except Exception as e:
            logger.error(
                f"LightRAG proxy request failed for {request.method} /{request.path}: {e}",
                exc_info=True,
            )
            raise

    async def execute_stream(
        self, request: LightRAGProxyRequest
    ) -> AsyncIterator[bytes]:
        """
        Execute a streaming proxy request to LightRAG.

        Args:
            request: The proxy request to forward.

        Yields:
            bytes: Chunks of the streaming response.

        Raises:
            Exception: If the request fails.
        """
        logger.debug(
            f"Proxying streaming to LightRAG: {request.method} /{request.path}"
        )

        try:
            async for chunk in self.proxy_client.forward_stream(request):
                yield chunk
        except Exception as e:
            logger.error(
                f"LightRAG streaming proxy request failed for {request.method} /{request.path}: {e}",
                exc_info=True,
            )
            raise
