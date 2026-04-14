"""MCP server entry point with all five tools registered."""

import json
import os
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from .config import load_config, is_path_allowed
from .file_reader import list_md_files, read_md_file
from .xlsx_handler import parse_org_performance_sheet, create_personal_performance_sheet
from .llm_client import OllamaClient
from .performance_mapper import map_records_to_performance

mcp = FastMCP("mcp-bsc")
_config = load_config()


# ---------------------------------------------------------------------------
# Tool 1: list_work_records
# ---------------------------------------------------------------------------
@mcp.tool()
def list_work_records() -> str:
    """Return a JSON list of all .md work-record file paths in the allowed base path."""
    try:
        base = _config["allowed_base_path"]
        files = list_md_files(base)
        return json.dumps(files, ensure_ascii=False, indent=2)
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Tool 2: read_work_record
# ---------------------------------------------------------------------------
@mcp.tool()
def read_work_record(file_path: str) -> str:
    """Read and return the content of a specific .md work-record file.

    Args:
        file_path: Absolute or relative path to the .md file.
    """
    try:
        base = _config["allowed_base_path"]
        return read_md_file(file_path, base)
    except (PermissionError, FileNotFoundError, ValueError) as exc:
        return f"Error: {exc}"
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Tool 3: read_org_performance_sheet
# ---------------------------------------------------------------------------
@mcp.tool()
def read_org_performance_sheet(xlsx_path: str) -> str:
    """Parse an org performance sheet xlsx and return its items as JSON.

    Args:
        xlsx_path: Path to the org performance sheet xlsx file.
    """
    try:
        items = parse_org_performance_sheet(xlsx_path)
        return json.dumps(items, ensure_ascii=False, indent=2)
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Tool 4: generate_personal_performance_sheet
# ---------------------------------------------------------------------------
@mcp.tool()
def generate_personal_performance_sheet(
    org_xlsx_path: str,
    output_path: str = "",
) -> str:
    """Generate a personal performance sheet xlsx from work records and the org sheet.

    Reads all .md files in the allowed base path, maps them to the org
    performance items using the local Ollama LLM, and writes the result to
    an xlsx file.

    Args:
        org_xlsx_path: Path to the org performance sheet xlsx.
        output_path:   Destination path for the generated xlsx.
                       Defaults to OUTPUT_DIR/personal_performance_<timestamp>.xlsx.
    """
    try:
        config = _config
        base = config["allowed_base_path"]

        # Determine output path
        if not output_path:
            output_dir = config["output_dir"]
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                output_dir, f"personal_performance_{timestamp}.xlsx"
            )

        # Read all md files
        md_paths = list_md_files(base)
        if not md_paths:
            return "Error: No .md work-record files found in the allowed base path."

        md_contents = []
        for p in md_paths:
            try:
                md_contents.append(read_md_file(p, base))
            except Exception:
                pass  # skip unreadable files

        # Parse org items
        org_items = parse_org_performance_sheet(org_xlsx_path)
        if not org_items:
            return "Error: No items found in the org performance sheet."

        # Map via LLM
        llm = OllamaClient(
            base_url=config["ollama_base_url"],
            model=config["ollama_model"],
        )
        mapped = map_records_to_performance(org_items, md_contents, llm)

        # Determine template path (next to this package's templates dir)
        pkg_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = os.path.join(pkg_dir, "templates", "personal_performance_template.xlsx")

        saved = create_personal_performance_sheet(template_path, output_path, mapped)
        return f"Personal performance sheet saved to: {saved}"
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Tool 5: analyze_work_records_with_llm
# ---------------------------------------------------------------------------
@mcp.tool()
def analyze_work_records_with_llm(
    work_records_text: str,
    org_items_json: str,
) -> str:
    """Directly analyse work records against org items using Ollama LLM.

    Args:
        work_records_text: Raw work record text (markdown).
        org_items_json:    JSON string of org performance items.
    """
    try:
        org_items = json.loads(org_items_json)
        llm = OllamaClient(
            base_url=_config["ollama_base_url"],
            model=_config["ollama_model"],
        )
        result = llm.analyze_and_map(org_items, work_records_text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        return f"Error: {exc}"


def main() -> None:
    """Run the MCP server (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
