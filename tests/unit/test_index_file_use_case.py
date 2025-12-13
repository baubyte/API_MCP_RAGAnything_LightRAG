import os
import pytest
from pathlib import Path

from application.use_cases.index_file_use_case import IndexFileUseCase
from domain.entities.indexing_result import IndexingStatus, FileIndexingResult
from tests.doubles.double_rag_engine import DoubleRAGEngine


class TestIndexFileUseCase:
    """Unit tests for IndexFileUseCase."""

    async def test_execute_returns_result_from_rag_engine(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute returns the result from rag_engine.index_document."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFileUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )

        result = await use_case.execute(
            file_path="/tmp/documents/report.pdf",
            file_name="report.pdf",
        )

        assert result.status == IndexingStatus.SUCCESS
        assert result.file_path == "/tmp/documents/report.pdf"
        assert result.file_name == "report.pdf"

    async def test_execute_passes_correct_arguments_to_rag_engine(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute passes correct arguments to rag_engine.index_document."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFileUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )

        await use_case.execute(
            file_path="/tmp/documents/report.pdf",
            file_name="report.pdf",
        )

        assert len(double_rag_engine.index_document_calls) == 1
        call = double_rag_engine.index_document_calls[0]
        assert call.file_path == "/tmp/documents/report.pdf"
        assert call.file_name == "report.pdf"
        assert call.output_dir == output_dir

    async def test_execute_creates_output_directory(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute creates the output directory if it doesn't exist."""
        output_dir = str(tmp_path / "new_output_dir")
        use_case = IndexFileUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )

        assert not os.path.exists(output_dir)

        await use_case.execute(
            file_path="/tmp/documents/report.pdf",
            file_name="report.pdf",
        )

        assert os.path.exists(output_dir)
        assert os.path.isdir(output_dir)

    async def test_execute_with_configured_result(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute returns configured result from double."""
        output_dir = str(tmp_path / "output")
        expected_result = FileIndexingResult(
            status=IndexingStatus.FAILED,
            message="Custom error message",
            file_path="/custom/path.pdf",
            file_name="path.pdf",
            error="Parsing failed",
        )
        double_rag_engine.set_index_document_result(expected_result)

        use_case = IndexFileUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )

        result = await use_case.execute(
            file_path="/tmp/documents/report.pdf",
            file_name="report.pdf",
        )

        assert result.status == IndexingStatus.FAILED
        assert result.message == "Custom error message"
        assert result.error == "Parsing failed"
