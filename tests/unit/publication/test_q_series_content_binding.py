from pathlib import Path

from orion.programme.q_series_content_binding import (
    BINDING_SCHEMA,
    git_blob_sha1,
    inspect_q_series_content_binding,
    load_q_series_content_binding,
    require_q_series_content_binding,
)
from orion.registry import Q_SERIES_SYNC_EPOCH


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_git_blob_sha1_matches_known_empty_blob():
    assert git_blob_sha1(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_canonical_q_series_publication_bytes_match_recursive_v3_binding():
    report = inspect_q_series_content_binding(REPO_ROOT)
    assert report.sync_epoch == Q_SERIES_SYNC_EPOCH
    assert report.files_bound >= 35
    assert report.drifted_paths == ()
    assert report.missing_paths == ()
    assert report.clean is True
    require_q_series_content_binding(REPO_ROOT)
    payload = report.as_json()
    assert payload["schema"] == BINDING_SCHEMA
    assert payload["grants_scientific_authority"] is False
    assert payload["grants_novelty_authority"] is False
    assert payload["predicts_journal_acceptance"] is False


def test_noncanonical_q1_constraint_rank_draft_is_not_promoted_by_the_binding():
    legacy_path = "papers/archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md"
    canonical_path = "papers/orion-05-tare-expressivity/MANUSCRIPT_V3_REFINED.md"
    bound_paths = {
        str(row["path"]) for row in load_q_series_content_binding(REPO_ROOT)["files"]
    }

    assert canonical_path in bound_paths
    assert legacy_path not in bound_paths

    historical = (REPO_ROOT / legacy_path).read_text(encoding="utf-8")
    assert "HISTORICAL, NON-CANONICAL DRAFT" in historical
    assert "never admitted by the V2/V3 claim ledgers" in historical
    assert "applications beyond frozen R6M are" in historical
    assert "`CANNOT_CHECK`" in historical
    assert "grants no novelty, publication, peer-review" in historical
    assert "not back-ported into Q1" in historical


def test_legacy_publication_tokens_retain_scopes_and_adverse_q3_terminal():
    q1 = (
        REPO_ROOT / "papers/orion-05-tare-expressivity/CLAIM_LEDGER_V2.md"
    ).read_text(encoding="utf-8")
    assert "`PROVEN-ALL-N` **only within the frozen R6M grammar/objective**" in q1
    assert "`PROSPECTIVE-BOUNDED`: one frozen public subject and 15 matchings" in q1
    assert "`REFUTED` **only for uniform support-one sufficiency" in q1
    assert "No internal authority string grants novelty or physical quantum advantage" in q1

    q3 = (
        REPO_ROOT / "papers/orion-07-dual-instrument/CLAIM_LEDGER_V2.md"
    ).read_text(encoding="utf-8")
    terminal = (
        "Q3_PROSPECTIVE_CASE_SERIES_COMPLETE__N3_VALID__"
        "AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED__NO_RELIABILITY_GENERALIZATION"
    )
    q3_normalized = " ".join(q3.split())
    assert terminal in q3
    assert "remain retired as contaminated" in q3_normalized
    assert "no rate, calibration, predictive-validity" in q3
    assert "still-open `>=20`-item cross-programme protocol" in q3_normalized
