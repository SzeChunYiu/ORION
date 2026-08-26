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


def test_a_surface_naming_no_authority_is_cannot_check(tmp_path: Path) -> None:
    """Unreadable is not the same as unbound, so it must not fail the gate.

    This asserted MISALIGNED until the rule was checked against the papers. Six
    of seven flags were wrong: P10's manuscript is bound by sha256 *from* the
    authority record, P10 also ships a PDF with no citable text, and P12, P13,
    P15 and P11 each phrase the designation in a way a proximity rule misreads.
    Acting on the P10 flag would have meant editing bytes that record binds by
    digest -- breaking a tamper-evident receipt to satisfy a prose convention.
    """
    root = _paper(tmp_path, CITE, CITE, "No authority named.\n")
    assert main(["--root", str(root)]) == EXIT_CANNOT_CHECK


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
    for name in ("orion-21-state-as-computation", "orion-24-orion-rse"):
        rec = records[name]
        assert not rec.unbound, f"{name} has a free-floating surface: {rec.unbound}"
        assert not rec.disagreeing, f"{name} surfaces disagree: {rec.cited}"


def test_a_superseded_table_row_is_not_an_active_citation() -> None:
    """P15 lists superseded records in a table.

    The heading sits beyond any fixed window for the second row, so a proximity
    rule read a superseded record as active. Scope is the governing heading.
    """
    text = (
        "| Superseded authority | Lifecycle |\n"
        "| --- | --- |\n"
        "| `P15_ACTIVE_CLAIM_AUTHORITY_V2.json` | frozen |\n"
        "| `P15_ACTIVE_CLAIM_AUTHORITY_V1.json` | methods only |\n"
    )
    assert _active_versions(text) == set()


def test_p15_manuscript_and_ledger_agree_on_v3() -> None:
    records = {r.paper: r for r in audit_repository()}
    rec = records["orion-25-orion-research-harness"]
    assert not rec.disagreeing, rec.cited
    assert rec.cited.get("manuscript") == {"3"}


def test_authority_binding_a_surface_by_digest_counts_as_a_citation(tmp_path: Path) -> None:
    """P10's case: the tie runs from the authority record to the manuscript.

    ``P10_ACTIVE_CLAIM_AUTHORITY_V1.json`` binds ``manuscript/main.tex`` by
    sha256. The manuscript names no record, so reading only the prose says it is
    free-floating -- when in fact it carries the strongest tie in the paper, one
    that breaks if either side changes.
    """
    import json

    d = tmp_path / "papers" / "paper-99-fake"
    d.mkdir(parents=True)
    (d / "P99_ACTIVE_CLAIM_AUTHORITY_V1.json").write_text(
        json.dumps(
            {
                "evidence_bindings": {
                    "manuscript": {
                        "artifact": "papers/paper-99-fake/MANUSCRIPT.md",
                        "sha256": "0" * 64,
                    }
                }
            }
        )
    )
    (d / "MANUSCRIPT.md").write_text("This manuscript names no authority record.\n")
    (d / "CLAIM_EVIDENCE_LEDGER.md").write_text(CITE)

    records = audit_repository(tmp_path)
    assert len(records) == 1
    assert records[0].cited["manuscript"] == {"1"}
    assert records[0].reverse_bound == ["manuscript"]
    assert main(["--root", str(tmp_path)]) == EXIT_PASS


def test_no_paper_on_the_live_tree_has_contradictory_authority_language() -> None:
    """CI must fail on contradictory terminal language, not only on named papers.

    The other live-tree assertions here pin P11, P14 and P15 individually, which
    means a contradiction introduced in any other paper passes unnoticed. #1131
    asks for the general property: no paper's reader-facing surfaces may name
    different records as active.

    Scoped to DISAGREE deliberately. A surface whose authority cannot be read is
    CANNOT_CHECK and is not a contradiction -- P10's manuscript is bound by
    sha256 from the authority side and names no record in prose, which is a
    stronger tie than a citation rather than a missing one.
    """
    bad = {
        rec.paper: {k: sorted(v) for k, v in rec.cited.items() if v}
        for rec in audit_repository()
        if rec.disagreeing
    }
    assert not bad, (
        "these papers name different authority records as active on different "
        f"surfaces; at most one can be right: {bad}"
    )
