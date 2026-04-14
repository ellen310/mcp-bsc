"""Read-only access to .md work-record files inside the allowed base path."""

import os
from typing import List

from .config import is_path_allowed


def list_md_files(base_path: str) -> List[str]:
    """Return a sorted list of all .md file paths under *base_path*."""
    md_files: List[str] = []
    real_base = os.path.realpath(os.path.abspath(base_path))

    if not os.path.isdir(real_base):
        return md_files

    for root, _dirs, files in os.walk(real_base):
        for filename in files:
            if filename.lower().endswith(".md"):
                full_path = os.path.join(root, filename)
                md_files.append(full_path)

    return sorted(md_files)


def read_md_file(file_path: str, allowed_base: str) -> str:
    """Read and return the content of a .md file after security validation.

    Raises:
        PermissionError: If the resolved path is outside *allowed_base*.
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a .md file.
    """
    if not file_path.lower().endswith(".md"):
        raise ValueError(f"Only .md files are supported: {file_path}")

    if not is_path_allowed(file_path, allowed_base):
        raise PermissionError(
            f"Access denied: '{file_path}' is outside the allowed base path."
        )

    real_path = os.path.realpath(os.path.abspath(file_path))

    if not os.path.isfile(real_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(real_path, "r", encoding="utf-8") as fh:
        return fh.read()
