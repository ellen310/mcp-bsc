"""Configuration loader and path security validation."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def load_config() -> dict:
    """Load configuration from environment variables."""
    return {
        "allowed_base_path": os.getenv("ALLOWED_BASE_PATH", ""),
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3"),
        "output_dir": os.getenv("OUTPUT_DIR", "./output"),
    }


def is_path_allowed(path: str, allowed_base: str) -> bool:
    """Check whether *path* is under *allowed_base* (prevents path traversal).

    Both paths are resolved with ``os.path.realpath`` before comparison so that
    symlinks and ``..`` components cannot escape the allowed directory.
    """
    real_path = os.path.realpath(os.path.abspath(path))
    real_base = os.path.realpath(os.path.abspath(allowed_base))

    # Ensure the base ends with a separator so that a directory named
    # "allowed_base_extended" does not pass the prefix check.
    if not real_base.endswith(os.sep):
        real_base = real_base + os.sep

    return real_path.startswith(real_base) or real_path == real_base.rstrip(os.sep)
