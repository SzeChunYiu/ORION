"""P5 preserves its no-terminal result and diagnostic-only history."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-05-self-orion"
AUTHORITY = PAPER / "P5_ACTIVE_CLAIM_AUTHORITY_V1.json"


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

    return json.loads(AUTHORITY.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def test_p5_active_terminal_is_the_frozen_no_terminal_result() -> None:
    record = _strict_record()
    assert record["active_terminal"] == "NO_TERMINAL_UNDER_FROZEN_RULES"
    assert record["provenance"]["kind"] == "LANE_TRANSCRIPTION_PENDING_AUTHOR_DESIGNATION"
    assert record["lifecycle_state"] == "ACTIVE_TRANSCRIBED_NOT_AUTHOR_DESIGNATED"
    assert record["external_validation"] == "CANNOT_CHECK"
    assert record["promotion_allowed"] is False
    panel = record["frozen_revision_level_panel"]
    assert panel["cases"] == 96
    assert panel["full_t7_correct"] == 12
    assert panel["frozen_decision_terminals_fired"] == 0
    assert panel["rules_retuned_after_outcome_access"] is False
    assert panel["grants_scientific_authority"] is False


def test_p5_has_one_prospective_primary_endpoint() -> None:
    endpoint = _strict_record()["primary_endpoint"]
    assert endpoint["endpoint_id"] == "P5.H1.PROTECTED_FRESH_TASK_IMPROVEMENT"
    assert endpoint["role"] == "SOLE_PRIMARY_HYPOTHESIS_ENDPOINT"
    assert endpoint["status"] == "CANNOT_CHECK"
    assert endpoint["prospective_absolute_advantage"] == 0.05
    assert endpoint["harmful_transfer_noninferiority_guard"] == 0.02
    assert set(endpoint["companion_measures"]) == {
        "fresh-transfer success",
        "harmful-transfer rate",
    }


def test_p5_retains_21_of_24_and_post_outcome_24_of_24_separately() -> None:
    history = _strict_record()["diagnostic_history"]
    historical = history["historical_hidden_cause_archive"]
    assert historical["score"] == "21/24"
    assert historical["authority"] == "DIAGNOSTIC_ONLY"
    assert historical["retained_errors"] == ["P5-HC-002", "P5-HC-012", "P5-HC-018"]
    instrument = history["post_outcome_public_suite_instrument"]
    assert instrument["control"] == "21/24"
    assert instrument["instrument"] == "24/24"
    assert instrument["authority"] == "POST_OUTCOME_PUBLIC_SUITE_INSTRUMENT_DIAGNOSIS_ONLY"
    assert instrument["preregistration_chronology"] == "CANNOT_CHECK"


def test_p5_h1_h4_and_six_arm_panel_remain_fail_closed() -> None:
    record = _strict_record()
    assert record["general_hypothesis_authority"] == {
        "H1": "CANNOT_CHECK",
        "H2": "CANNOT_CHECK",
        "H3": "CANNOT_CHECK",
        "H4": "CANNOT_CHECK",
    }
    six_arm = record["six_arm_execution_state"]
    assert six_arm["ready_arms"] == 0
    assert six_arm["registered_arms"] == 6
    assert six_arm["status"] == "0/6_READY"
    assert record["readiness"]["current"] == "NOT_PEER_REVIEW_READY"


def test_p5_zero_eligible_des_cells_are_not_zero_improvement() -> None:
    disposition = _strict_record()["p5_des_01_acquisition_boundary"]
    assert disposition["terminal"] == (
        "SWE_BENCH_RIGHTS_AND_PROTECTED_FRESH_ADOPTION_CUSTODY_UNAVAILABLE"
    )
    assert disposition["registered_cases"] == disposition["retained_cannot_check_rows"] == 2228
    assert disposition["planned_run_cells"] == 53472
    assert disposition["executed_run_cells"] == 0
    assert disposition["boundary"] == "Zero eligible cells do not estimate zero improvement."


def test_p5_all_reader_visible_sources_are_content_bound() -> None:
    record = _strict_record()
    for binding in record["evidence_bindings"].values():
        artifact = ROOT / binding["artifact"]
        assert artifact.is_file(), binding
        assert binding["sha256"] == _sha(artifact), binding
    source = record["provenance"]["transcribed_from"]
    assert source["sha256"] == _sha(ROOT / source["artifact"])


def test_p5_readme_has_unambiguous_non_stale_current_pointers() -> None:
    text = (PAPER / "README.md").read_text(encoding="utf-8")
    assert text.count("**Current science manuscript:** `manuscript/main.tex`") == 1
    assert text.count("**Current authority:** `P5_ACTIVE_CLAIM_AUTHORITY_V1.json`") == 1
    assert text.count("**Current readiness:** `JOURNAL_READINESS.md`") == 1
    assert set(re.findall(r"P5_ACTIVE_CLAIM_AUTHORITY_V\d+\.json", text)) == {
        "P5_ACTIVE_CLAIM_AUTHORITY_V1.json"
    }
    status = text.split("## Scoped claim", 1)[0]
    assert "NO_TERMINAL_UNDER_FROZEN_RULES" in status
    assert "not peer-review ready" in status
    assert "`PEER_REVIEW_READY`" not in status
