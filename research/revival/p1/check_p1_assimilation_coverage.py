#!/usr/bin/env python3
"""Bind P1 donor coverage to the merged 36-row nearest-work matrix."""

from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COVERAGE = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_COVERAGE_V1.json"
DEFAULT_LEDGER = ROOT / "research" / "revival" / "p1" / "P1_DONOR_ASSIMILATION_LEDGER_V1.json"
DISPOSITIONS = frozenset({"ADOPT", "ADAPT", "COMPOSE", "DEFER", "REJECT"})
ARXIV_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5})", re.IGNORECASE)


def _matrix_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    inside = False
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("| mechanism | nearest work |"):
            inside = True
            continue
        if not inside:
            continue
        if line.startswith("**Disposition counts:"):
            break
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        disposition = cells[3].replace("**", "").strip()
        if disposition not in DISPOSITIONS:
            continue
        rows.append(
            {
                "mechanism": cells[0],
                "source": cells[1],
                "disposition": disposition,
                "arxiv_ids": tuple(match.group(1) for match in ARXIV_RE.finditer(cells[1])),
            }
        )
    return rows


def validate_coverage(coverage: dict, ledger: dict, *, root: Path = ROOT) -> tuple[str, ...]:
    errors: list[str] = []
    if coverage.get("schema_version") != "P1.donor-assimilation-coverage.v1":
        errors.append("schema_version")
    source_rel = str(coverage.get("source_matrix", ""))
    source_path = root / source_rel
    if not source_path.is_file():
        return tuple((*errors, "source_matrix_missing"))

    matrix_rows = _matrix_rows(source_path)
    covered = coverage.get("rows")
    if not isinstance(covered, list):
        return tuple((*errors, "coverage_rows_not_list"))
    expected_total = int(coverage.get("expected_total", -1))
    if len(matrix_rows) != expected_total:
        errors.append(f"matrix_total:{len(matrix_rows)}!={expected_total}")
    if len(covered) != expected_total:
        errors.append(f"coverage_total:{len(covered)}!={expected_total}")

    expected_counts = coverage.get("expected_disposition_counts", {})
    matrix_counts = Counter(str(row["disposition"]) for row in matrix_rows)
    coverage_counts = Counter(str(row.get("disposition", "")) for row in covered if isinstance(row, dict))
    if dict(matrix_counts) != expected_counts:
        errors.append(f"matrix_disposition_counts:{dict(matrix_counts)}!={expected_counts}")
    if dict(coverage_counts) != expected_counts:
        errors.append(f"coverage_disposition_counts:{dict(coverage_counts)}!={expected_counts}")

    ledger_receipts = {
        str(item.get("receipt_id"))
        for item in ledger.get("receipts", [])
        if isinstance(item, dict) and item.get("receipt_id")
    }
    seen_ids: set[str] = set()
    for index, (matrix_row, cover_row) in enumerate(zip(matrix_rows, covered, strict=False), start=1):
        prefix = f"row[{index}]"
        if not isinstance(cover_row, dict):
            errors.append(f"{prefix}:not_object")
            continue
        row_id = str(cover_row.get("id", ""))
        expected_id = f"P1-NW-{index:03d}"
        if row_id != expected_id:
            errors.append(f"{prefix}:id:{row_id}!={expected_id}")
        if row_id in seen_ids:
            errors.append(f"{prefix}:duplicate_id")
        seen_ids.add(row_id)
        if str(cover_row.get("disposition")) != str(matrix_row["disposition"]):
            errors.append(
                f"{prefix}:disposition:{cover_row.get('disposition')}!={matrix_row['disposition']}"
            )
        cover_source = str(cover_row.get("source", "")).lower()
        for arxiv_id in matrix_row["arxiv_ids"]:  # type: ignore[union-attr]
            if str(arxiv_id).lower() not in cover_source:
                errors.append(f"{prefix}:missing_arxiv:{arxiv_id}")
        if not str(cover_row.get("novelty_effect", "")).strip():
            errors.append(f"{prefix}:missing_novelty_effect")
        if not str(cover_row.get("baseline_relevance", "")).strip():
            errors.append(f"{prefix}:missing_baseline_relevance")
        receipt_id = str(cover_row.get("receipt_id", ""))
        if receipt_id and receipt_id not in ledger_receipts:
            errors.append(f"{prefix}:unknown_receipt:{receipt_id}")

    round_state = str(coverage.get("round_state", ""))
    if "ROUND_B_REQUIRED" not in round_state:
        errors.append("round_b_requirement_missing")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text())
    ledger = json.loads(args.ledger.read_text())
    errors = validate_coverage(coverage, ledger)
    print(json.dumps({"valid": not errors, "errors": list(errors)}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
