"""
HTTP client for proxying requests to the LightRAG API.
Implements the LightRAGProxyClientPort interface.
"""

import httpx
import logging
from typing import Any, AsyncIterator, Optional
from config import ProxyConfig
from domain.ports.lightrag_proxy_client import LightRAGProxyClientPort
from domain.entities.lightrag_proxy_entities import LightRAGProxyRequest, LightRAGProxyResponse

logger = logging.getLogger(__name__)


class LightRAGProxyClient(LightRAGProxyClientPort):
    """
    Async HTTP client for forwarding requests to LightRAG API.
    Implements ProxyClientPort for hexagonal architecture compliance.
    Handles token forwarding, streaming responses, and OpenAPI spec retrieval.
    """

    def __init__(self, config: ProxyConfig):
        self.config = config
        self.base_url = config.LIGHTRAG_API_URL.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.config.LIGHTRAG_TIMEOUT),
                follow_redirects=True,
            )
            logger.info(f"LightRAG proxy client initialized for {self.base_url}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("LightRAG proxy client closed")

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not initialized."""
        if self._client is None:
            raise RuntimeError("LightRAG proxy client not initialized. Call initialize() first.")
        return self._client

    async def get_openapi_spec(self) -> dict[str, Any]:
        """
        Fetch the OpenAPI specification from LightRAG API.
        
        Returns:
            dict: The OpenAPI specification JSON.
        """
        try:
            response = await self.client.get("/openapi.json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch OpenAPI spec from LightRAG: {e}")
            return {}

    def _build_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """
        Build headers for forwarding, extracting Authorization if present.
        
        Args:
            headers: Original headers from the request.
            
        Returns:
            dict: Headers to forward to LightRAG.
        """
        request_headers = {}
        if headers:
            # Forward authorization header (case-insensitive)
            if "authorization" in headers:
                request_headers["Authorization"] = headers["authorization"]
            elif "Authorization" in headers:
                request_headers["Authorization"] = headers["Authorization"]

            # Forward API key header if present
            if "api_key_header_value" in headers:
                request_headers["api_key_header_value"] = headers["api_key_header_value"]

            # Forward Content-Type if present
            if "Content-Type" in headers:
                request_headers["Content-Type"] = headers["Content-Type"]

        return request_headers

    async def forward_request(
        self,
        request: LightRAGProxyRequest,
    ) -> LightRAGProxyResponse:
        """
        Forward a request to LightRAG API.
        
        Args:
            request: The proxy request containing method, path, body, params, headers.
            
        Returns:
            LightRAGProxyResponse: The response from LightRAG API.
        """
        request_headers = self._build_headers(request.headers)

        # Set content type if provided
        if request.content_type:
            request_headers["Content-Type"] = request.content_type

        # Prepare request kwargs
        kwargs: dict[str, Any] = {
            "method": request.method,
            "url": f"/{request.path.lstrip('/')}",
            "headers": request_headers,
        }

        if request.params:
            kwargs["params"] = request.params

        if request.raw_content is not None:
            kwargs["content"] = request.raw_content
        elif request.body is not None:
            kwargs["json"] = request.body

        logger.debug(f"Forwarding {request.method} /{request.path} to LightRAG")

        response = await self.client.request(**kwargs)

        # Build response headers (exclude hop-by-hop headers)
        excluded_headers = {
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        }
        response_headers = {
            k: v
            for k, v in response.headers.items()
            if k.lower() not in excluded_headers
        }

        return LightRAGProxyResponse(
            status_code=response.status_code,
            content=response.content,
            headers=response_headers,
            media_type=response.headers.get("content-type"),
        )

    async def forward_stream(
        self,
        request: LightRAGProxyRequest,
    ) -> AsyncIterator[bytes]:  # type: ignore[override]
        """
        Forward a streaming request to LightRAG API.
        
        Args:
            request: The proxy request containing method, path, body, params, headers.
            
        Yields:
            bytes: Chunks of the streaming response.
        """
        request_headers = self._build_headers(request.headers)

        # Use longer timeout for streaming
        timeout = httpx.Timeout(self.config.LIGHTRAG_STREAM_TIMEOUT)

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=True,
        ) as stream_client:
            kwargs: dict[str, Any] = {
                "method": request.method,
                "url": f"/{request.path.lstrip('/')}",
                "headers": request_headers,
            }

            if request.params:
                kwargs["params"] = request.params

            if request.body is not None:
                kwargs["json"] = request.body

            logger.debug(f"Forwarding streaming {request.method} /{request.path} to LightRAG")

            async with stream_client.stream(**kwargs) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk


# Singleton instance (initialized in dependencies.py)
_lightrag_client: Optional[LightRAGProxyClient] = None


def get_lightrag_client_instance() -> LightRAGProxyClient:
    """Get the singleton LightRAG client instance."""
    global _lightrag_client
    if _lightrag_client is None:
        from config import ProxyConfig
        proxy_config = ProxyConfig()  # type: ignore
        _lightrag_client = LightRAGProxyClient(proxy_config)
    return _lightrag_client


async def init_lightrag_client() -> LightRAGProxyClient:
    """Initialize and return the LightRAG client."""
    client = get_lightrag_client_instance()
    await client.initialize()
    return client


async def close_lightrag_client() -> None:
    """Close the LightRAG client."""
    global _lightrag_client
    if _lightrag_client:
        await _lightrag_client.close()
        _lightrag_client = None
