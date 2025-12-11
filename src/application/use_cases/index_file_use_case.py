import logging
import os
from domain.ports.rag_engine import RAGEnginePort
from domain.entities.indexing_result import FileIndexingResult

logger = logging.getLogger(__name__)




class IndexFileUseCase:
    """
    Use case for indexing a single file.
    Orchestrates the file indexing process.
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

    async def execute(self, file_path: str, file_name: str) -> FileIndexingResult:
        """
        Execute the file indexing process.

        Args:
            file_path: Path to the file to index.
            file_name: Name of the file.

        Returns:
            FileIndexingResult: Structured result of the indexing operation.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        result = await self.rag_engine.index_document(
            file_path=file_path, file_name=file_name, output_dir=self.output_dir
        )

        logger.info(f"Indexation finished with result: {result.model_dump()}")
        return result
