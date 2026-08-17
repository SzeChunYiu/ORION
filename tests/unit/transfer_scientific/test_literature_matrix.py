"""Literature matrix dispositions are frozen from local docs, not live arXiv fetches."""

from __future__ import annotations

from pathlib import Path

from orion.transfer.scientific.literature import (
    DISPOSITIONS,
    REQUIRED_SEARCH_TERMS,
    load_literature_matrix,
)

ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = (
    ROOT
    / "research"
    / "cross-domain-mechanic-transfer-v1"
    / "LITERATURE_MATRIX.md"
)
JSON_PATH = (
    ROOT
    / "research"
    / "cross-domain-mechanic-transfer-v1"
    / "fixtures"
    / "LITERATURE_MATRIX_V1.json"
)


def test_literature_matrix_uses_only_allowed_dispositions() -> None:
    matrix = load_literature_matrix(JSON_PATH)
    assert matrix.source == "local-docs-and-existing-citations"
    assert matrix.arxiv_api_queried is False
    assert set(matrix.dispositions_used) <= set(DISPOSITIONS)
    assert set(DISPOSITIONS) <= set(matrix.dispositions_used)
    for row in matrix.rows:
        assert row.disposition in DISPOSITIONS
        assert row.identifier
        assert row.mechanism


def test_required_search_terms_are_covered_and_stop_rule_recorded() -> None:
    matrix = load_literature_matrix(JSON_PATH)
    covered = set(matrix.search_terms_covered)
    assert set(REQUIRED_SEARCH_TERMS) <= covered
    assert matrix.consecutive_flat_rounds >= 2
    assert matrix.stop_rule == (
        "Stop after two consecutive primary-source/related-work rounds "
        "yield no mechanism changing transfer representation, applicability "
        "test, negative-transfer control or benchmark design."
    )


def test_markdown_matrix_exists_and_matches_json_row_count() -> None:
    text = MATRIX_PATH.read_text(encoding="utf-8")
    matrix = load_literature_matrix(JSON_PATH)
    assert "ADOPT" in text and "REJECT" in text
    for row in matrix.rows:
        assert row.identifier in text
    assert f"{len(matrix.rows)} rows" in text or str(len(matrix.rows)) in text
