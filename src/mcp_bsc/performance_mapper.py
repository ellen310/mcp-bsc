"""Performance mapping logic: combine md files and call LLM."""

from typing import List

from .llm_client import OllamaClient


def map_records_to_performance(
    org_items: List[dict],
    md_contents: List[str],
    llm_client: OllamaClient,
) -> List[dict]:
    """Map multiple md work-record contents to org performance items via LLM.

    Args:
        org_items:   Parsed org performance items (from xlsx_handler).
        md_contents: List of raw markdown strings (one per file).
        llm_client:  An initialised OllamaClient instance.

    Returns:
        A list of personal performance item dicts with achievement/evidence
        fields populated by the LLM.
    """
    combined_records = "\n\n---\n\n".join(md_contents)
    return llm_client.analyze_and_map(org_items, combined_records)
