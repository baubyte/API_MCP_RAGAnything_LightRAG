from typing import Optional, List
import time
import os
from domain.ports.rag_engine import RAGEnginePort
from domain.entities.query_result import QueryResult
from domain.entities.indexing_result import (
    FileIndexingResult,
    FolderIndexingResult,
    FolderIndexingStats,
    FileProcessingDetail,
    IndexingStatus,
)
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

    async def index_document(
        self, file_path: str, file_name: str, output_dir: str
    ) -> FileIndexingResult:
        """
        Index a single document into the RAG system.

        Args:
            file_path: Absolute path to the document to index.
            file_name: Name of the file being indexed.
            output_dir: Directory for processing outputs.

        Returns:
            FileIndexingResult: Structured result of the indexing operation.
        """
        start_time = time.time()
        try:
            await self.rag.process_document_complete(
                file_path=file_path, output_dir=output_dir, parse_method="auto"
            )
            processing_time_ms = (time.time() - start_time) * 1000
            return FileIndexingResult(
                status=IndexingStatus.SUCCESS,
                message=f"File '{file_name}' indexed successfully",
                file_path=file_path,
                file_name=file_name,
                processing_time_ms=round(processing_time_ms, 2),
            )
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            logger.error(f"Failed to index document {file_path}: {e}", exc_info=True)
            return FileIndexingResult(
                status=IndexingStatus.FAILED,
                message=f"Failed to index file '{file_name}'",
                file_path=file_path,
                file_name=file_name,
                processing_time_ms=round(processing_time_ms, 2),
                error=error_msg,
            )

    async def index_folder(
        self,
        folder_path: str,
        output_dir: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
    ) -> FolderIndexingResult:
        """
        Index all documents in a folder.

        Args:
            folder_path: Absolute path to the folder containing documents.
            output_dir: Directory for processing outputs.
            recursive: Whether to process subdirectories recursively.
            file_extensions: Optional list of file extensions to filter.

        Returns:
            FolderIndexingResult: Structured result with statistics and file details.
        """
        start_time = time.time()
        try:
            result = await self.rag.process_folder_complete(
                folder_path=folder_path,
                output_dir=output_dir,
                parse_method="auto",
                file_extensions=file_extensions,
                recursive=recursive,
                display_stats=True,
                max_workers=self.max_workers,
            )
            processing_time_ms = (time.time() - start_time) * 1000

            # Parse the result from RAGAnything
            result_dict = result if isinstance(result, dict) else {}
            stats = FolderIndexingStats(
                total_files=result_dict.get("total_files", 0),
                files_processed=result_dict.get("successful_files", 0),
                files_failed=result_dict.get("failed_files", 0),
                files_skipped=result_dict.get("skipped_files", 0),
            )

            # Build file results if available
            file_results: Optional[List[FileProcessingDetail]] = None
            if result_dict and "file_details" in result_dict:
                file_results = []
                file_details = result_dict["file_details"]
                if isinstance(file_details, list):
                    for detail in file_details:
                        file_results.append(
                            FileProcessingDetail(
                                file_path=detail.get("file_path", ""),
                                file_name=os.path.basename(detail.get("file_path", "")),
                                status=(
                                    IndexingStatus.SUCCESS
                                    if detail.get("success", False)
                                    else IndexingStatus.FAILED
                                ),
                                error=detail.get("error"),
                            )
                        )

            # Determine overall status
            if stats.files_failed == 0 and stats.files_processed > 0:
                status = IndexingStatus.SUCCESS
                message = f"Successfully indexed {stats.files_processed} file(s) from '{folder_path}'"
            elif stats.files_processed > 0 and stats.files_failed > 0:
                status = IndexingStatus.PARTIAL
                message = f"Partially indexed folder '{folder_path}': {stats.files_processed} succeeded, {stats.files_failed} failed"
            elif stats.files_processed == 0 and stats.total_files > 0:
                status = IndexingStatus.FAILED
                message = f"Failed to index any files from '{folder_path}'"
            else:
                status = IndexingStatus.SUCCESS
                message = f"No files found to index in '{folder_path}'"

            return FolderIndexingResult(
                status=status,
                message=message,
                folder_path=folder_path,
                recursive=recursive,
                stats=stats,
                processing_time_ms=round(processing_time_ms, 2),
                file_results=file_results,
            )
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            logger.error(f"Failed to index folder {folder_path}: {e}", exc_info=True)
            return FolderIndexingResult(
                status=IndexingStatus.FAILED,
                message=f"Failed to index folder '{folder_path}'",
                folder_path=folder_path,
                recursive=recursive,
                stats=FolderIndexingStats(),
                processing_time_ms=round(processing_time_ms, 2),
                error=error_msg,
            )

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
        query_param = QueryParam(
            **query.model_dump(exclude={"query", "include_metadata"})
        )

        result = QueryResult(**await self.rag.lightrag.aquery_data(query.query, param=query_param))  # type: ignore

        if not query.include_metadata:
            result = QueryResult(**result.model_dump(exclude={"metadata"}))

        if not query.include_references:
            result = QueryResult(**result.model_dump(exclude={"data"}))

        answer = None

        if not query.only_need_context:
            answer = await self.rag.lightrag.aquery(query.query, param=query_param)  # type: ignore

        result.answer = answer if answer else None  # type: ignore

        return result
