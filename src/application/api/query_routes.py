from fastapi import APIRouter, Depends, HTTPException, status
from application.use_cases.query_use_case import QueryUseCase
from application.requests.query_request import QueryRequest
from domain.entities.query_result import QueryResult
from dependencies import get_query_use_case
import logging

logger = logging.getLogger(__name__)


query_router = APIRouter(tags=["Query"])


@query_router.post(
    "/query",
    response_model=QueryResult,
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,
)
async def query_rag(
    request: QueryRequest,
    use_case: QueryUseCase = Depends(get_query_use_case),
):
    """
    Query the RAG system.

    Args:
        request: The query request containing query parameters.
        use_case: The query use case dependency.

    Returns:
        dict: Query results including answer and context.
    """
    try:
        result: QueryResult = await use_case.execute(request)
        return result
    except Exception as e:
        logger.error(f"Failed to query RAG system: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
