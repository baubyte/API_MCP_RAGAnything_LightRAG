"""
Routes for forwarding requests to the LightRAG API.
"""

import logging
from typing import Any, Optional
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import StreamingResponse
from domain.entities.lightrag_proxy_entities import LightRAGProxyRequest
from application.use_cases.lightrag_proxy_use_case import LightRAGProxyUseCase
from dependencies import get_lightrag_proxy_use_case

logger = logging.getLogger(__name__)

lightrag_proxy_router = APIRouter(tags=["LightRAG Proxy"])


def extract_headers_for_forwarding(request: Request) -> dict[str, str]:
    """Extract headers that should be forwarded to LightRAG."""
    headers = {}

    # Forward Authorization header
    auth_header = request.headers.get("authorization") or request.headers.get(
        "Authorization"
    )
    if auth_header:
        headers["Authorization"] = auth_header

    # Forward API key header if present
    api_key_header = request.headers.get("api_key_header_value")
    if api_key_header:
        headers["api_key_header_value"] = api_key_header

    return headers


async def build_lightrag_proxy_request(
    path: str,
    request: Request,
) -> LightRAGProxyRequest:
    """
    Build a LightRAGProxyRequest from a FastAPI Request.

    Args:
        path: The path to proxy to.
        request: The FastAPI request object.

    Returns:
        LightRAGProxyRequest: The domain entity for the proxy request.
    """
    method = request.method
    query_params = dict(request.query_params) if request.query_params else None
    headers = extract_headers_for_forwarding(request)

    # Get request body
    body: Optional[Any] = None
    raw_content: Optional[bytes] = None
    content_type = request.headers.get("content-type", "")

    if method in ["POST", "PUT", "PATCH"]:
        if "application/json" in content_type:
            try:
                body = await request.json()
            except Exception:
                raw_content = await request.body()
        elif "multipart/form-data" in content_type:
            # For file uploads, get raw content
            raw_content = await request.body()
            # Preserve content-type with boundary
            headers["Content-Type"] = content_type
        else:
            raw_content = await request.body()
            if content_type:
                headers["Content-Type"] = content_type

    return LightRAGProxyRequest(
        method=method,
        path=path,
        body=body,
        params=query_params,
        headers=headers,
        content_type=content_type if content_type and "multipart" in content_type else None,
        raw_content=raw_content,
    )


@lightrag_proxy_router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,  # Hide from OpenAPI - real endpoints come from LightRAG spec merge
)
async def proxy_to_lightrag(
    path: str,
    request: Request,
    use_case: LightRAGProxyUseCase = Depends(get_lightrag_proxy_use_case),
):
    """
    Proxy all requests to LightRAG API.

    This endpoint forwards requests to the LightRAG API, preserving:
    - HTTP method
    - Request body
    - Query parameters
    - Authorization headers

    Streaming endpoints (/query/stream, /api/generate, /api/chat) return
    StreamingResponse for real-time data delivery.
    """
    proxy_request = await build_lightrag_proxy_request(path, request)

    # Check if this is a streaming endpoint
    if use_case.is_streaming_request(proxy_request):
        async def stream_generator():
            async for chunk in use_case.execute_stream(proxy_request):
                yield chunk

        return StreamingResponse(
            stream_generator(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming request
    try:
        response = await use_case.execute(proxy_request)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response.headers,
            media_type=response.media_type,
        )

    except Exception as e:
        logger.error(
            f"LightRAG proxy request failed for {proxy_request.method} /{path}: {e}",
            exc_info=True,
        )
        return Response(
            content=f'{{"detail": "LightRAG proxy error: {str(e)}"}}',
            status_code=502,
            media_type="application/json",
        )
