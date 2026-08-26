"""A README naming several records is fine if it designates one as current."""

from __future__ import annotations

from pathlib import Path

from orion.programme.readme_pointers import (
    EXIT_AMBIGUOUS,
    EXIT_CANNOT_CHECK,
    EXIT_MISSING,
    EXIT_PASS,
    audit_repository,
    main,
)


def _paper(tmp_path: Path, readme: str) -> Path:
    for i in range(1, 16):
        d = tmp_path / "papers" / f"paper-{i:02d}-fake"
        d.mkdir(parents=True)
        (d / "README.md").write_text(readme)
    return tmp_path


ONE_OF_EACH = (
    "See MANUSCRIPT.md, P_ACTIVE_CLAIM_AUTHORITY_V1.json and JOURNAL_READINESS.md.\n"
)


def test_exactly_one_of_each_passes(tmp_path: Path) -> None:
    assert main(["--root", str(_paper(tmp_path, ONE_OF_EACH))]) == EXIT_PASS


def test_two_authorities_with_no_designation_is_ambiguous(tmp_path: Path) -> None:
    readme = ONE_OF_EACH + "Also P_ACTIVE_CLAIM_AUTHORITY_V2.json exists.\n"
    assert main(["--root", str(_paper(tmp_path, readme))]) == EXIT_AMBIGUOUS


def test_two_authorities_with_a_designation_is_not_ambiguous(tmp_path: Path) -> None:
    """Naming a superseded record while designating the current one is good practice.

    A checker that punished this would push papers toward deleting history.
    """
    readme = (
        "**Current authority:** `P_ACTIVE_CLAIM_AUTHORITY_V2.json`\n"
        "Historical: P_ACTIVE_CLAIM_AUTHORITY_V1.json\n"
        "See MANUSCRIPT.md and JOURNAL_READINESS.md.\n"
    )
    assert main(["--root", str(_paper(tmp_path, readme))]) == EXIT_PASS


def test_absent_is_distinct_from_ambiguous(tmp_path: Path) -> None:
    readme = "See MANUSCRIPT.md only.\n"
    assert main(["--root", str(_paper(tmp_path, readme))]) == EXIT_MISSING


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_live_tree_state_is_recorded() -> None:
    records = audit_repository()
    assert len(records) == 15
    exact = [r for r in records if r.readme_exists and not r.ambiguous and not r.absent]
    assert exact, "at least some papers point cleanly"


def test_a_name_marked_historical_does_not_compete_for_currency() -> None:
    """P12 says MANUSCRIPT.md is a historical snapshot; that is clarity, not ambiguity."""
    from orion.programme.readme_pointers import audit_repository

    p12 = next(r for r in audit_repository() if r.paper.startswith("orion-22"))
    assert p12.counts["manuscript"] > 1, "P12 does mention more than one manuscript"
    assert "manuscript" not in p12.ambiguous, "the historical one must not count as competing"


def test_p13_two_active_authorities_are_reported_not_silently_resolved() -> None:
    """V3's record says V2 remains active for the P13B leaf. Two is the design."""
    from orion.programme.readme_pointers import audit_repository

    p13 = next(r for r in audit_repository() if r.paper.startswith("orion-23"))
    assert p13.counts["authority"] == 2
    assert "authority" in p13.ambiguous
