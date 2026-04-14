"""xlsx parsing and generation for org / personal performance sheets."""

import os
from typing import List, Dict

import openpyxl
from openpyxl import load_workbook, Workbook


# ---------------------------------------------------------------------------
# Column indices (1-based) expected in the org performance sheet
# ---------------------------------------------------------------------------
_ORG_COL_CATEGORY = 1   # 카테고리
_ORG_COL_ITEM = 2       # 성과항목
_ORG_COL_INDICATOR = 3  # 지표
_ORG_COL_TARGET = 4     # 목표치
_ORG_COL_WEIGHT = 5     # 가중치

# Column indices expected in the personal performance sheet template
_PERSONAL_COL_CATEGORY = 1    # 카테고리
_PERSONAL_COL_ITEM = 2        # 성과항목
_PERSONAL_COL_INDICATOR = 3   # 지표
_PERSONAL_COL_TARGET = 4      # 목표치
_PERSONAL_COL_ACHIEVEMENT = 5 # 달성내용
_PERSONAL_COL_EVIDENCE = 6    # 근거자료
_PERSONAL_COL_SCORE = 7       # 점수


def parse_org_performance_sheet(xlsx_path: str) -> List[Dict[str, str]]:
    """Parse an org performance sheet and return a list of item dicts.

    Expected columns (row 1 = header, rows 2+ = data):
        1: 카테고리, 2: 성과항목, 3: 지표, 4: 목표치, 5: 가중치

    Returns:
        A list of dicts with keys: category, item, indicator, target, weight.
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active

    results: List[Dict[str, str]] = []
    first_row = True
    for row in ws.iter_rows(values_only=True):
        if first_row:
            first_row = False
            continue  # skip header row
        if not any(row):
            continue  # skip empty rows
        results.append(
            {
                "category": str(row[_ORG_COL_CATEGORY - 1] or ""),
                "item": str(row[_ORG_COL_ITEM - 1] or ""),
                "indicator": str(row[_ORG_COL_INDICATOR - 1] or ""),
                "target": str(row[_ORG_COL_TARGET - 1] or ""),
                "weight": str(row[_ORG_COL_WEIGHT - 1] or ""),
            }
        )
    wb.close()
    return results


def create_personal_performance_sheet(
    template_path: str,
    output_path: str,
    data: List[Dict[str, str]],
) -> str:
    """Fill a personal performance sheet template and save to *output_path*.

    Args:
        template_path: Path to the personal performance template xlsx.
        output_path:   Destination file path for the generated xlsx.
        data:          List of dicts with keys: category, item, indicator,
                       target, achievement, evidence, score.

    Returns:
        The absolute path to the saved file.
    """
    wb = load_workbook(template_path)
    ws = wb.active

    # Find the first empty data row (skip header row 1)
    start_row = 2
    for i, item in enumerate(data):
        row_idx = start_row + i
        ws.cell(row=row_idx, column=_PERSONAL_COL_CATEGORY).value = item.get("category", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_ITEM).value = item.get("item", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_INDICATOR).value = item.get("indicator", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_TARGET).value = item.get("target", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_ACHIEVEMENT).value = item.get("achievement", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_EVIDENCE).value = item.get("evidence", "")
        ws.cell(row=row_idx, column=_PERSONAL_COL_SCORE).value = item.get("score", "")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)
    wb.close()
    return os.path.abspath(output_path)
