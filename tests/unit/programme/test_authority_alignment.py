"""A paper's reader-facing surfaces must agree on what authority binds them."""

from __future__ import annotations

from pathlib import Path

from orion.programme.authority_alignment import (
    EXIT_CANNOT_CHECK,
    EXIT_MISALIGNED,
    EXIT_PASS,
    _active_versions,
    audit_repository,
    main,
)


def _paper(tmp_path: Path, manuscript: str, ledger: str, readiness: str) -> Path:
    d = tmp_path / "papers" / "paper-99-fake"
    d.mkdir(parents=True)
    (d / "P99_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text("{}")
    (d / "MANUSCRIPT.md").write_text(manuscript)
    (d / "CLAIM_EVIDENCE_LEDGER.md").write_text(ledger)
    (d / "PEER_REVIEW_READINESS.md").write_text(readiness)
    return tmp_path


CITE = "Active authority `P99_ACTIVE_CLAIM_AUTHORITY_V1.json`.\n"


def test_all_three_citing_the_same_version_passes(tmp_path: Path) -> None:
    assert main(["--root", str(_paper(tmp_path, CITE, CITE, CITE))]) == EXIT_PASS


def test_a_free_floating_surface_is_misaligned(tmp_path: Path) -> None:
    assert main(["--root", str(_paper(tmp_path, CITE, CITE, "No authority named.\n"))]) == EXIT_MISALIGNED


def test_surfaces_bound_to_different_versions_disagree(tmp_path: Path) -> None:
    other = "Active authority `P99_ACTIVE_CLAIM_AUTHORITY_V2.json`.\n"
    assert main(["--root", str(_paper(tmp_path, CITE, other, CITE))]) == EXIT_MISALIGNED


def test_an_active_designation_beats_a_nearby_historical_word() -> None:
    """P11's ledger: V2 "is the sole active lifecycle record ... retains P11H".

    "retains" governs a leaf, not the authority. A naive proximity rule read the
    sole active record as historical and reported the paper unbound.
    """
    text = (
        "`P11_ACTIVE_CLAIM_AUTHORITY_V2.json` is the sole active lifecycle "
        "record. It binds the P11I positive leaf, retains P11H defects."
    )
    assert _active_versions(text) == {"2"}


def test_a_version_named_historical_is_not_treated_as_binding() -> None:
    text = "Historical: `P9_ACTIVE_CLAIM_AUTHORITY_V1.json` was superseded."
    assert _active_versions(text) == set()


def test_missing_tree_is_not_a_pass(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path / "absent")]) == EXIT_CANNOT_CHECK


def test_p11_and_p14_are_aligned_on_the_live_tree() -> None:
    records = {r.paper: r for r in audit_repository()}
    for name in ("paper-11-state-as-computation", "paper-14-orion-rse"):
        rec = records[name]
        assert not rec.unbound, f"{name} has a free-floating surface: {rec.unbound}"
        assert not rec.disagreeing, f"{name} surfaces disagree: {rec.cited}"
