from application.requests.query_request import QueryRequest
from domain.entities.query_result import QueryResult
from fastapi.logger import logger
from domain.entities.query_entity import Query
from domain.ports.rag_engine import RAGEnginePort


class QueryUseCase:
    """
    Use case for querying the RAG system.
    Orchestrates the query process.
    """

    def __init__(self, rag_engine: RAGEnginePort) -> None:
        """
        Initialize the use case.

        Args:
            query_service: The service handling query operations.
        """
        self.rag_engine = rag_engine

    async def execute(self, request: QueryRequest) -> QueryResult:
        """
        Execute the query process.

        Args:
            request: The query request containing query parameters.

        Returns:
            QueryResult: The structured query result.
        """
        query_entity = Query(**request.model_dump())
        result = await self.rag_engine.query(query_entity)
        return result
