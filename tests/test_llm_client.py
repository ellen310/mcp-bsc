"""Tests for llm_client.py — uses httpx mocking to avoid real Ollama calls."""

import json
import pytest

from unittest.mock import MagicMock, patch

from mcp_bsc.llm_client import OllamaClient


ORG_ITEMS = [
    {
        "category": "업무성과",
        "item": "프로젝트 완료율",
        "indicator": "완료 프로젝트 수",
        "target": "90% 이상",
        "weight": "30%",
    }
]

MAPPED_RESPONSE = [
    {
        "category": "업무성과",
        "item": "프로젝트 완료율",
        "indicator": "완료 프로젝트 수",
        "target": "90% 이상",
        "achievement": "92% 달성",
        "evidence": "프로젝트 보고서 2024-Q4",
        "score": "",
    }
]


class TestOllamaClientGenerate:
    def test_returns_response_text(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello from LLM"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response) as mock_post:
            client = OllamaClient(base_url="http://localhost:11434", model="llama3")
            result = client.generate("test prompt")

        assert result == "Hello from LLM"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[1]["json"]["stream"] is False
        assert call_kwargs[1]["json"]["model"] == "llama3"

    def test_raises_on_http_error(self):
        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=MagicMock()
        )

        with patch("httpx.post", return_value=mock_response):
            client = OllamaClient()
            with pytest.raises(httpx.HTTPStatusError):
                client.generate("fail")


class TestOllamaClientAnalyzeAndMap:
    def test_parses_json_array_from_response(self):
        raw_llm_output = f"Here is the result:\n{json.dumps(MAPPED_RESPONSE)}\n"

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": raw_llm_output}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            client = OllamaClient()
            result = client.analyze_and_map(ORG_ITEMS, "some work records text")

        assert isinstance(result, list)
        assert result[0]["achievement"] == "92% 달성"

    def test_raises_when_no_json_array(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "No JSON here."}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response):
            client = OllamaClient()
            with pytest.raises(ValueError, match="valid JSON array"):
                client.analyze_and_map(ORG_ITEMS, "text")
