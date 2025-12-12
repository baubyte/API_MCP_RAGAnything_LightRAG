"""
Domain entities for LightRAG proxy operations.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LightRAGProxyRequest:
    """
    Represents a request to be proxied to the LightRAG API.
    """

    method: str
    """HTTP method (GET, POST, PUT, DELETE, PATCH)."""

    path: str
    """Request path (without base URL)."""

    body: Optional[Any] = None
    """Request body (JSON serializable)."""

    params: Optional[dict[str, Any]] = None
    """Query parameters."""

    headers: dict[str, str] = field(default_factory=dict)
    """Headers to forward (including Authorization)."""

    content_type: Optional[str] = None
    """Content-Type header value."""

    raw_content: Optional[bytes] = None
    """Raw bytes content for non-JSON requests (e.g., file uploads)."""

    is_streaming: bool = False
    """Whether this request expects a streaming response."""

    def __post_init__(self):
        """Normalize the HTTP method to uppercase."""
        self.method = self.method.upper()


@dataclass
class LightRAGProxyResponse:
    """
    Represents a response from the LightRAG API.
    """

    status_code: int
    """HTTP status code from the LightRAG API."""

    content: bytes
    """Response body content."""

    headers: dict[str, str] = field(default_factory=dict)
    """Response headers."""

    media_type: Optional[str] = None
    """Content-Type of the response."""

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success (2xx status code)."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error (4xx or 5xx status code)."""
        return self.status_code >= 400
