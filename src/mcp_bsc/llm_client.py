"""Ollama LLM client for performance mapping."""

import json
import re
from typing import List, Dict

import httpx


class OllamaClient:
    """Thin client for the Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str) -> str:
        """Call ``/api/generate`` with *prompt* and return the full response text.

        Uses ``stream: false`` so the entire response is returned in one JSON
        object rather than as a stream of chunks.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        response = httpx.post(url, json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    def analyze_and_map(
        self,
        org_items: List[Dict[str, str]],
        work_records: str,
    ) -> List[Dict[str, str]]:
        """Map work records to org performance items using the LLM.

        Builds a structured prompt and asks the model to return a JSON array
        where each element corresponds to an org item enriched with
        ``achievement`` and ``evidence`` fields derived from the work records.

        Returns:
            A list of dicts with keys: category, item, indicator, target,
            achievement, evidence, score.
        """
        org_items_text = json.dumps(org_items, ensure_ascii=False, indent=2)

        prompt = f"""당신은 직원의 업무기록을 분석하여 성과관리표를 작성하는 전문가입니다.

아래 [조직성과 항목]과 [업무기록]을 참고하여, 각 성과 항목에 대해 달성내용과 근거자료를 작성해주세요.

[조직성과 항목]
{org_items_text}

[업무기록]
{work_records}

다음 JSON 배열 형식으로만 응답하세요. 다른 설명은 필요 없습니다:
[
  {{
    "category": "카테고리명",
    "item": "성과항목명",
    "indicator": "지표",
    "target": "목표치",
    "achievement": "업무기록 기반 달성내용",
    "evidence": "근거자료 (파일명, 날짜 등)",
    "score": ""
  }}
]
"""
        raw = self.generate(prompt)

        # Extract JSON array from the response
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return a valid JSON array. Response:\n{raw}")

        return json.loads(match.group())
