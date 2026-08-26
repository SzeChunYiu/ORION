"""P9 exposes one bounded active claim without laundering legacy ledgers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-09-structured-epistemic-learning"
AUTHORITY = PAPER / "P9_ACTIVE_CLAIM_AUTHORITY_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_record() -> dict:
    def reject_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON object key: {key}")
            value[key] = item
        return value

    return json.loads(
        AUTHORITY.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates
    )


def test_p9_active_terminal_is_transcribed_without_authority_upgrade() -> None:
    record = _strict_record()
    assert record["active_terminal"] == "P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED"
    assert record["accounting_terminal"] == "P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN"
    assert record["accounting_survival_verdict"] == "SURVIVES_FULL_ACCOUNTING"
    assert record["provenance"]["kind"] == (
        "LANE_TRANSCRIPTION_PENDING_AUTHOR_DESIGNATION"
    )
    assert record["lifecycle_state"] == "ACTIVE_TRANSCRIBED_NOT_AUTHOR_DESIGNATED"
    assert record["external_validation"] == "CANNOT_CHECK"
    assert record["promotion_allowed"] is False


def test_p9_has_exactly_one_primary_endpoint_and_retains_supporting_mechanism() -> None:
    record = _strict_record()
    endpoint = record["primary_endpoint"]
    assert endpoint["endpoint_id"] == "P9.CAUSAL_DIAGNOSTIC.ACCURACY"
    assert endpoint["role"] == "SOLE_PRIMARY_OUTCOME_IN_CURRENT_MANUSCRIPT"
    assert endpoint["protected_observation"] == {
        "registered_diagnostic": "4/5",
        "generic_compute_escalation": "1/5",
    }
    assert endpoint["supporting_mechanism"]["false_compute_escalations"] == {
        "registered_diagnostic": 0,
        "generic_compute_escalation": 4,
    }
    assert len(record["primary_endpoints"]) == 1
    assert record["primary_endpoints"] == [endpoint["endpoint_id"]]


def test_p9_preserves_adverse_and_resource_incomparable_cells() -> None:
    record = _strict_record()
    adverse = record["retained_outcomes"]["d_a_threshold_transport"]
    assert adverse["diagnostic_prediction"] == "ACCESSIBILITY"
    assert adverse["protected_gold"] == "CANNOT_CHECK"
    assert adverse["probe_quality"] > adverse["registered_target"]
    assert adverse["protected_quality"] < adverse["registered_target"]

    accounting = record["resource_accounting"]
    assert accounting["coordinates"] == [
        "I_sem",
        "A_dim",
        "A_transform",
        "M_state",
        "C_fit",
        "C_infer",
        "C_explicit",
        "R_registered",
    ]
    assert accounting["scalarization"] == "PROHIBITED"
    assert accounting["vector_dominance_contradictions"] == 0
    assert accounting["d_i_cost_ordering"]["disposition"] == (
        "RESOURCE_INCOMPARABLE_NO_SCALARIZATION"
    )
    assert accounting["d_i_cost_ordering"]["registered_cost_favors"] == (
        "INFORMATION"
    )
    assert accounting["d_i_cost_ordering"]["hidden_compute_favors"] == (
        "COMPUTATION"
    )


def test_p9_retains_retired_margin_and_every_open_cannot_check() -> None:
    outcomes = _strict_record()["retained_outcomes"]
    serializer = outcomes["same_information_serializer"]
    assert serializer["historical_headline_margin"] == "+0.50"
    assert serializer["status"] == "RETIRED_AS_TOP_TIER_HEADLINE"
    assert serializer["symbol_remint_accuracy_shift"] == [0.75, 0.5]
    assert serializer["changed_answers"] == "32/128"

    order = outcomes["order_reminting"]
    assert order["outcome"] == "CANNOT_CHECK"
    assert order["reached_arms"] == "0/8"
    assert order["successor_terminal"] == "P9_D1V1_3_PROSPECTIVE_PROTOCOL_FROZEN"
    assert order["successor_positive_authority"] is False

    open_weight = outcomes["open_weight_frontier"]
    assert open_weight["outcome"] == "CANNOT_CHECK"
    assert open_weight["executed_cells"] == "0/1344"
    assert open_weight["terminal"] == "T3_GRID_DECLARED_NO_CELL_EXECUTED"
    assert open_weight["broad_open_weight_claim_allowed"] is False


def test_p9_reader_visible_sources_are_content_bound_and_scoped() -> None:
    record = _strict_record()
    for binding in record["evidence_bindings"].values():
        artifact = ROOT / binding["artifact"]
        assert artifact.is_file(), binding
        assert binding["sha256"] == _sha(artifact), binding

    sources = record["reader_visible_source_status"]
    assert sources["manuscript"]["status"] == "CURRENT_SCIENCE_SOURCE_NOT_FINAL_PACKAGE"
    assert sources["claim_ledger"]["status"] == "LEGACY_PRE_RESULT_INTEGRATION"
    assert sources["readiness"]["status"] == "HISTORICAL_BOUNDED_REVIEW_BRANCH_LEDGER"
    assert sources["claim_ledger"]["may_override_active_authority"] is False
    assert sources["readiness"]["may_override_active_authority"] is False


def test_p9_readme_has_exactly_one_non_stale_pointer_set() -> None:
    text = (PAPER / "README.md").read_text(encoding="utf-8")
    assert text.count("**Current science manuscript:** `manuscript/main.tex`") == 1
    assert text.count(
        "**Current authority:** `P9_ACTIVE_CLAIM_AUTHORITY_V1.json`"
    ) == 1
    assert text.count("**Current readiness:** `JOURNAL_READINESS.md`") == 1
    assert set(re.findall(r"P9_ACTIVE_CLAIM_AUTHORITY_V\d+\.json", text)) == {
        "P9_ACTIVE_CLAIM_AUTHORITY_V1.json"
    }
    assert "historical bounded review-branch ledger" in text

