import os
import logging
from domain.ports.rag_engine import RAGEnginePort
from domain.entities.indexing_result import FolderIndexingResult
from application.requests.indexing_request import IndexFolderRequest

logger = logging.getLogger(__name__)


class IndexFolderUseCase:
    """
    Use case for indexing a folder of documents.
    Orchestrates the folder indexing process.
    """

    def __init__(self, rag_engine: RAGEnginePort, output_dir: str) -> None:
        """
        Initialize the use case.

        Args:
            rag_engine: Port for RAG engine operations.
            output_dir: Output directory for processing.
        """
        self.rag_engine = rag_engine
        self.output_dir = output_dir

    async def execute(self, request: IndexFolderRequest) -> FolderIndexingResult:
        """
        Execute the folder indexing process.

        Args:
            request: The indexing request containing folder parameters.

        Returns:
            FolderIndexingResult: Structured result with statistics and file details.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        result = await self.rag_engine.index_folder(
            folder_path=request.folder_path,
            output_dir=self.output_dir,
            recursive=request.recursive,
            file_extensions=request.file_extensions,
        )

        logger.info(f"Indexation finished with result: {result.model_dump()}")

        return result
