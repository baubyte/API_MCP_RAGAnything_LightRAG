import os
import pytest
from pathlib import Path

from application.use_cases.index_folder_use_case import IndexFolderUseCase
from application.requests.indexing_request import IndexFolderRequest
from domain.entities.indexing_result import (
    IndexingStatus,
    FolderIndexingResult,
    FolderIndexingStats,
)
from tests.doubles.double_rag_engine import DoubleRAGEngine


class TestIndexFolderUseCase:
    """Unit tests for IndexFolderUseCase."""

    async def test_execute_returns_result_from_rag_engine(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute returns the result from rag_engine.index_folder."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
            recursive=True,
        )

        result = await use_case.execute(request)

        assert result.status == IndexingStatus.SUCCESS
        assert result.folder_path == "/tmp/documents"
        assert result.recursive is True

    async def test_execute_passes_correct_arguments_to_rag_engine(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute passes correct arguments to rag_engine.index_folder."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
            recursive=True,
            file_extensions=[".pdf", ".docx"],
        )

        await use_case.execute(request)

        assert len(double_rag_engine.index_folder_calls) == 1
        call = double_rag_engine.index_folder_calls[0]
        assert call.folder_path == "/tmp/documents"
        assert call.output_dir == output_dir
        assert call.recursive is True
        assert call.file_extensions == [".pdf", ".docx"]

    async def test_execute_with_recursive_false(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute correctly passes recursive=False."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
            recursive=False,
        )

        await use_case.execute(request)

        assert len(double_rag_engine.index_folder_calls) == 1
        call = double_rag_engine.index_folder_calls[0]
        assert call.recursive is False

    async def test_execute_with_no_file_extensions(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute correctly passes None for file_extensions."""
        output_dir = str(tmp_path / "output")
        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
        )

        await use_case.execute(request)

        assert len(double_rag_engine.index_folder_calls) == 1
        call = double_rag_engine.index_folder_calls[0]
        assert call.file_extensions is None

    async def test_execute_creates_output_directory(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute creates the output directory if it doesn't exist."""
        output_dir = str(tmp_path / "new_output_dir")
        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
        )

        assert not os.path.exists(output_dir)

        await use_case.execute(request)

        assert os.path.exists(output_dir)
        assert os.path.isdir(output_dir)

    async def test_execute_with_configured_result(
        self,
        double_rag_engine: DoubleRAGEngine,
        tmp_path: Path,
    ) -> None:
        """Test that execute returns configured result from double."""
        output_dir = str(tmp_path / "output")
        expected_result = FolderIndexingResult(
            status=IndexingStatus.PARTIAL,
            message="Some files failed",
            folder_path="/custom/folder",
            recursive=True,
            stats=FolderIndexingStats(
                total_files=10,
                files_processed=7,
                files_failed=3,
                files_skipped=0,
            ),
            error="3 files failed to process",
        )
        double_rag_engine.set_index_folder_result(expected_result)

        use_case = IndexFolderUseCase(
            rag_engine=double_rag_engine,
            output_dir=output_dir,
        )
        request = IndexFolderRequest(
            folder_path="/tmp/documents",
        )

        result = await use_case.execute(request)

        assert result.status == IndexingStatus.PARTIAL
        assert result.message == "Some files failed"
        assert result.stats.files_failed == 3
        assert result.error == "3 files failed to process"
