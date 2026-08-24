"""Adverse evidence must be citable by identifier, and gaps must be reachable."""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.adverse_integration import (
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    EXIT_UNINTEGRATED,
    adverse_leaves,
    audit_repository,
    citable_identifiers,
    main,
)

LEAF = {
    "authority": "BINDING_NEGATIVE_BOUNDARY",
    "claim_id": "P99.SECRET.NEGATIVE.V1",
    "terminal": "P99_SECRET_NEGATIVE_EXECUTED",
}


def _tree(tmp_path: Path, readme: str) -> Path:
    paper = tmp_path / "papers" / "paper-99-fake"
    paper.mkdir(parents=True)
    (paper / "P99_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text(
        json.dumps({"paper_id": "P99", "leaf": LEAF})
    )
    (paper / "README.md").write_text(readme)
    return tmp_path


def test_buried_negative_is_a_gap(tmp_path: Path) -> None:
    root = _tree(tmp_path, "# P99\n\nEverything went well.\n")
    assert main(["--root", str(root)]) == EXIT_UNINTEGRATED


def test_cited_negative_passes(tmp_path: Path) -> None:
    root = _tree(tmp_path, "# P99\n\nThe P99_SECRET_NEGATIVE_EXECUTED negative stands.\n")
    assert main(["--root", str(root)]) == EXIT_PASS


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_class_label_alone_does_not_count_as_citation(tmp_path: Path) -> None:
    """The regression that made the first version of this checker wrong.

    Naming the shared authority class is not integrating the finding; naming
    the claim or terminal is.
    """
    root = _tree(tmp_path, "# P99\n\nWe note a BINDING_NEGATIVE_BOUNDARY somewhere.\n")
    assert main(["--root", str(root)]) == EXIT_UNINTEGRATED


def test_negative_controls_are_a_method_not_an_outcome() -> None:
    assert adverse_leaves({"authority": "NEGATIVE_CONTROLS_APPLIED"}) == []
    assert adverse_leaves({"authority": "BINDING_NEGATIVE_BOUNDARY"})


def test_identifiers_are_what_a_document_can_name() -> None:
    assert citable_identifiers(LEAF) == (
        "P99.SECRET.NEGATIVE.V1",
        "P99_SECRET_NEGATIVE_EXECUTED",
    )


def test_repository_has_no_unintegrated_adverse_evidence() -> None:
    report = audit_repository()
    assert report.papers_scanned > 0
    assert report.unintegrated == []
