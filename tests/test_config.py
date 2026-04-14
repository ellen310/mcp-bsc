"""Tests for config.py — load_config and is_path_allowed."""

import os
import pytest

from mcp_bsc.config import load_config, is_path_allowed


class TestLoadConfig:
    def test_returns_dict_with_required_keys(self):
        config = load_config()
        assert "allowed_base_path" in config
        assert "ollama_base_url" in config
        assert "ollama_model" in config
        assert "output_dir" in config

    def test_defaults_when_env_not_set(self, monkeypatch):
        monkeypatch.delenv("ALLOWED_BASE_PATH", raising=False)
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        monkeypatch.delenv("OUTPUT_DIR", raising=False)
        config = load_config()
        assert config["ollama_base_url"] == "http://localhost:11434"
        assert config["ollama_model"] == "llama3"
        assert config["output_dir"] == "./output"

    def test_reads_env_variables(self, monkeypatch):
        monkeypatch.setenv("ALLOWED_BASE_PATH", "/tmp/test_base")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "mistral")
        monkeypatch.setenv("OUTPUT_DIR", "/tmp/out")
        config = load_config()
        assert config["allowed_base_path"] == "/tmp/test_base"
        assert config["ollama_base_url"] == "http://custom:11434"
        assert config["ollama_model"] == "mistral"
        assert config["output_dir"] == "/tmp/out"


class TestIsPathAllowed:
    def test_path_inside_base_is_allowed(self, tmp_path):
        base = str(tmp_path)
        child = str(tmp_path / "subdir" / "file.md")
        # The child path doesn't have to exist for the check
        assert is_path_allowed(child, base) is True

    def test_exact_base_path_is_allowed(self, tmp_path):
        base = str(tmp_path)
        assert is_path_allowed(base, base) is True

    def test_path_outside_base_is_denied(self, tmp_path):
        base = str(tmp_path / "allowed")
        outside = str(tmp_path / "other" / "file.md")
        assert is_path_allowed(outside, base) is False

    def test_path_traversal_is_denied(self, tmp_path):
        base = str(tmp_path / "allowed")
        traversal = str(tmp_path / "allowed" / ".." / "secret.md")
        # realpath resolves ".." so it lands outside base
        assert is_path_allowed(traversal, base) is False

    def test_sibling_directory_with_similar_prefix_is_denied(self, tmp_path):
        """Ensure 'allowed_extra' is not accepted when base is 'allowed'."""
        base = str(tmp_path / "allowed")
        sibling = str(tmp_path / "allowed_extra" / "file.md")
        assert is_path_allowed(sibling, base) is False
