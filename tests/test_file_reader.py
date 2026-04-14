"""Tests for file_reader.py."""

import os
import pytest

from mcp_bsc.file_reader import list_md_files, read_md_file


@pytest.fixture()
def work_dir(tmp_path):
    """Create a small directory tree with .md and .txt files."""
    (tmp_path / "a.md").write_text("# Record A\nContent A", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("# Record B\nContent B", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("plain text", encoding="utf-8")
    return tmp_path


class TestListMdFiles:
    def test_returns_only_md_files(self, work_dir):
        files = list_md_files(str(work_dir))
        assert all(f.endswith(".md") for f in files)

    def test_returns_all_md_files_recursively(self, work_dir):
        files = list_md_files(str(work_dir))
        basenames = [os.path.basename(f) for f in files]
        assert "a.md" in basenames
        assert "b.md" in basenames

    def test_does_not_return_non_md_files(self, work_dir):
        files = list_md_files(str(work_dir))
        basenames = [os.path.basename(f) for f in files]
        assert "notes.txt" not in basenames

    def test_returns_empty_for_nonexistent_dir(self, tmp_path):
        files = list_md_files(str(tmp_path / "nonexistent"))
        assert files == []

    def test_result_is_sorted(self, work_dir):
        files = list_md_files(str(work_dir))
        assert files == sorted(files)


class TestReadMdFile:
    def test_reads_valid_md_file(self, work_dir):
        path = str(work_dir / "a.md")
        content = read_md_file(path, str(work_dir))
        assert "Record A" in content

    def test_rejects_file_outside_base(self, tmp_path):
        base = tmp_path / "allowed"
        base.mkdir()
        (base / "inside.md").write_text("inside", encoding="utf-8")
        outside = tmp_path / "outside.md"
        outside.write_text("secret", encoding="utf-8")
        with pytest.raises(PermissionError):
            read_md_file(str(outside), str(base))

    def test_rejects_non_md_file(self, work_dir):
        path = str(work_dir / "notes.txt")
        with pytest.raises(ValueError):
            read_md_file(path, str(work_dir))

    def test_raises_file_not_found(self, work_dir):
        path = str(work_dir / "missing.md")
        with pytest.raises(FileNotFoundError):
            read_md_file(path, str(work_dir))
