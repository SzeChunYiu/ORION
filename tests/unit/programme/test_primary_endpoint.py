"""Silence is not uniqueness.

The definition-of-done box asks whether every surviving paper has one unique
primary endpoint. A paper that declares none does not satisfy it by default,
and a checker that returned PASS on an empty field would answer a question it
never asked.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.primary_endpoint import (
    EXIT_CANNOT_CHECK,
    EXIT_NOT_UNIQUE,
    EXIT_PASS,
    EXIT_UNDECLARED,
    audit_repository,
    main,
)


def _tree(tmp_path: Path, terminals: dict[str, str | None]) -> Path:
    for i in range(1, 16):
        d = tmp_path / "papers" / f"paper-{i:02d}-fake"
        d.mkdir(parents=True)
        t = terminals.get(f"paper-{i:02d}")
        if t:
            (d / "P_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text(
                json.dumps({"active_terminal": t})
            )
    return tmp_path


def test_all_declared_and_unique_passes(tmp_path: Path) -> None:
    root = _tree(tmp_path, {f"paper-{i:02d}": f"T{i}" for i in range(1, 16)})
    assert main(["--root", str(root)]) == EXIT_PASS


def test_a_shared_endpoint_is_not_unique(tmp_path: Path) -> None:
    terminals = {f"paper-{i:02d}": f"T{i}" for i in range(1, 16)}
    terminals["paper-02"] = "T1"
    root = _tree(tmp_path, terminals)
    assert main(["--root", str(root)]) == EXIT_NOT_UNIQUE


def test_an_undeclared_paper_does_not_pass(tmp_path: Path) -> None:
    terminals = {f"paper-{i:02d}": f"T{i}" for i in range(1, 16)}
    terminals.pop("paper-07")
    root = _tree(tmp_path, terminals)
    assert main(["--root", str(root)]) == EXIT_UNDECLARED


def test_collision_outranks_silence(tmp_path: Path) -> None:
    """A tree with both problems reports the harder one."""
    terminals = {f"paper-{i:02d}": f"T{i}" for i in range(1, 16)}
    terminals["paper-02"] = "T1"
    terminals.pop("paper-07")
    root = _tree(tmp_path, terminals)
    assert main(["--root", str(root)]) == EXIT_NOT_UNIQUE


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_live_repository_state_is_recorded() -> None:
    """Six declare, nine do not. The box cannot close on this evidence."""
    report = audit_repository()
    assert len(report.endpoints) == 15
    assert report.collisions == {}, "declared endpoints must not collide"
    assert report.undeclared, (
        "if every paper now declares an endpoint, this test should be tightened "
        "to assert PASS rather than left asserting the gap"
    )


def test_endpoint_nested_under_active_claim_is_read(tmp_path: Path) -> None:
    """P14's shape: the endpoint sits at active_claim.scientific_terminal.

    The six papers carrying an authority record do not share a schema. Reading
    only ``active_terminal`` reported P14 as declaring none -- printed
    identically to the nine papers that have no record at all, so a parsing miss
    and a real absence were being counted as the same thing.
    """
    import json

    d = tmp_path / "papers" / "paper-14-fake"
    d.mkdir(parents=True)
    (d / "P14_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text(
        json.dumps({"active_claim": {"scientific_terminal": "P14_NESTED_TERMINAL"}})
    )
    report = audit_repository(tmp_path)
    got = [e for e in report.endpoints if e.terminal == "P14_NESTED_TERMINAL"]
    assert len(got) == 1, [e.terminal for e in report.endpoints]


def test_records_are_ordered_by_version_number_not_filename(tmp_path: Path) -> None:
    """V10 sorts before V9 alphabetically, so the newest stops being read."""
    import json

    d = tmp_path / "papers" / "paper-14-fake"
    d.mkdir(parents=True)
    for v, term in ((9, "OLD"), (10, "NEWEST")):
        (d / f"P14_ACTIVE_CLAIM_AUTHORITY_V{v}.json").write_text(
            json.dumps({"active_terminal": term})
        )
    report = audit_repository(tmp_path)
    got = [e.terminal for e in report.endpoints if e.terminal]
    assert got == ["NEWEST"], got
