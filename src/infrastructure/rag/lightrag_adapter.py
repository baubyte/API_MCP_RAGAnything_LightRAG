from typing import Dict, Any
from xml.etree.ElementInclude import include
from domain.ports.rag_engine import RAGEnginePort
from domain.entities.query_result import QueryResult
from raganything import RAGAnything
from lightrag import QueryParam
from fastapi.logger import logger
from domain.entities.query_entity import Query


class LightRAGAdapter(RAGEnginePort):
    """
    Adapter for RAGAnything/LightRAG implementing RAGEnginePort.
    Wraps the RAGAnything instance and provides a clean interface.
    """

    def __init__(self, rag_instance: RAGAnything, max_workers: int) -> None:
        """
        Initialize the LightRAG adapter.

        Args:
            rag_instance: The configured RAGAnything instance.
        """
        self.rag = rag_instance
        self._initialized = False
        self.max_workers = max_workers

    async def initialize(self) -> bool:
        """
        Initialize the RAG engine.

        Returns:
            bool: True if initialization was successful.
        """
        try:
            if not self._initialized:
                await self.rag._ensure_lightrag_initialized()
                self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}", exc_info=True)
            return False

    async def index_document(self, file_path: str, output_dir: str) -> bool:
        """
        Index a single document into the RAG system.

        Args:
            file_path: Absolute path to the document to index.
            output_dir: Directory for processing outputs.

        Returns:
            bool: True if indexing was successful.
        """
        try:
            await self.rag.process_document_complete(
                file_path=file_path,
                output_dir=output_dir,
                parse_method="auto"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}", exc_info=True)
            return False

    async def index_folder(
        self,
        folder_path: str,
        output_dir: str,
        recursive: bool = True,
        file_extensions: list[str] | None = None
    ) -> Dict[str, Any]:
        """
        Index all documents in a folder.

        Args:
            folder_path: Absolute path to the folder containing documents.
            output_dir: Directory for processing outputs.
            recursive: Whether to process subdirectories recursively.
            file_extensions: Optional list of file extensions to filter.
            max_workers: Number of parallel workers for processing.

        Returns:
            Dict containing indexing results and statistics.
        """
        try:
            result = await self.rag.process_folder_complete(
                folder_path=folder_path,
                output_dir=output_dir,
                parse_method="auto",
                file_extensions=file_extensions,
                recursive=recursive,
                display_stats=True,
                max_workers=self.max_workers
            )
            return result # type: ignore
        except Exception as e:
            logger.error(f"Failed to index folder {folder_path}: {e}", exc_info=True)
            return {"error": str(e)}

    async def query(
        self,
        query: Query,
    ) -> QueryResult:
        """
        Query the RAG system.

        Args:
            query: The query string.
            mode: Query mode (naive, local, global, hybrid).
            only_need_context: Return only context without LLM generation.
            **kwargs: Additional query parameters.

        Returns:
            QueryResult: The structured query result.
        """
        # Ensure initialized
        await self.initialize()
        
        # Create QueryParam from arguments
        query_param = QueryParam(**query.model_dump(exclude={"query", "include_metadata"}))

        result = QueryResult(**await self.rag.lightrag.aquery_data(query.query, param=query_param)) # type: ignore

        if not query.include_metadata:
            result = QueryResult(**result.model_dump(exclude={"metadata"}))

        if not query.include_references:
            result = QueryResult(**result.model_dump(exclude={"data"}))
            
        if not query.only_need_context:
            answer = await self.rag.lightrag.aquery(query.query, param=query_param) # type: ignore

        result.answer = answer if answer else None # type: ignore

        return result
