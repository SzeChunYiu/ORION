from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFIER_PATH = (
    REPO_ROOT
    / "research"
    / "extensions"
    / "orion-q"
    / "max_r6_exact_tare3_end_to_end_verify.py"
)


def _load_verifier():
    spec = importlib.util.spec_from_file_location("orion_q_exact_tare3_e2e_verify", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _subject(count: int, *, valid: bool = True) -> dict:
    return {
        "selected_top_k": 4,
        "selected_count": count,
        "triples": [{} for _ in range(count)],
        "all_witnesses_valid": valid,
    }


def _positive_result(*, h4_count: int = 4, n2_count: int = 4) -> dict:
    gates = {
        "p10_candidate_generated": True,
        "hostile_exact": True,
        "top_four_panel_complete": True,
        "both_open_subjects_joint_beat_canonical": True,
        "joint_beats_frame_only_strong_on_at_least_one_subject": True,
        "proof_carrying_witnesses": True,
        "fresh_subject_unread": True,
    }
    return {
        "authority": "MAX_R6_EXACT_TARE3_JOINT_DP_SUPPORTED",
        "development_supported": True,
        "protocol_errata": [
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_1",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_2",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_3",
        ],
        "reserved_stretched_n2_accessed": False,
        "p10_replay": {
            "candidate_generated": True,
            "reserved_stretched_n2_accessed": False,
        },
        "gates": gates,
        "subjects": {
            "H4": _subject(h4_count),
            "N2": _subject(n2_count),
        },
    }


def test_complete_positive_panel_is_pre_prospective_ready():
    verifier = _load_verifier()
    receipt = verifier.verify_result(_positive_result())
    assert receipt["software_integrity_pass"] is True
    assert receipt["top_four_panel_complete"] is True
    assert receipt["strict_supported"] is True
    assert receipt["pre_prospective_ready"] is True
    assert receipt["reserved_stretched_n2_accessed"] is False
    assert receipt["underlying_erratum3_listed"] is True
    assert "MAX_R6_EXACT_TARE3_DP_ERRATUM_3" in receipt["bound_errata"]


def test_short_panel_cannot_escape_as_positive():
    verifier = _load_verifier()
    receipt = verifier.verify_result(_positive_result(h4_count=3))
    assert receipt["software_integrity_pass"] is False
    assert receipt["top_four_panel_complete"] is False
    assert receipt["strict_supported"] is False
    assert receipt["pre_prospective_ready"] is False
    assert "declared_top_four_panel_gate_disagrees_with_recomputed_panel" in receipt["errors"]
    assert "positive_underlying_receipt_with_incomplete_top_four_panel" in receipt["errors"]


def test_missing_erratum3_binding_is_integrity_failure():
    verifier = _load_verifier()
    result = _positive_result()
    result["protocol_errata"] = result["protocol_errata"][:-1]
    receipt = verifier.verify_result(result)
    assert receipt["software_integrity_pass"] is False
    assert receipt["pre_prospective_ready"] is False
    assert receipt["underlying_erratum3_listed"] is False
    assert any(
        error.startswith("underlying_receipt_missing_bound_errata:")
        for error in receipt["errors"]
    )


def test_declared_top_four_gate_must_match_recomputed_panel():
    verifier = _load_verifier()
    result = _positive_result()
    result["gates"]["top_four_panel_complete"] = False
    result["development_supported"] = False
    result["authority"] = "MAX_R6_EXACT_TARE3_JOINT_DP_NEGATIVE"
    receipt = verifier.verify_result(result)
    assert receipt["software_integrity_pass"] is False
    assert receipt["top_four_panel_complete"] is True
    assert "declared_top_four_panel_gate_disagrees_with_recomputed_panel" in receipt["errors"]


def test_candidate_negative_path_is_integrity_valid_but_not_ready():
    verifier = _load_verifier()
    gates = {
        "p10_candidate_generated": False,
        "hostile_exact": True,
        "top_four_panel_complete": False,
        "both_open_subjects_joint_beat_canonical": False,
        "joint_beats_frame_only_strong_on_at_least_one_subject": False,
        "proof_carrying_witnesses": False,
        "fresh_subject_unread": True,
    }
    result = {
        "authority": "MAX_R6_EXACT_TARE3_JOINT_DP_NEGATIVE",
        "development_supported": False,
        "protocol_errata": [
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_1",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_2",
            "MAX_R6_EXACT_TARE3_DP_ERRATUM_3",
        ],
        "reserved_stretched_n2_accessed": False,
        "p10_replay": {
            "candidate_generated": False,
            "reserved_stretched_n2_accessed": False,
        },
        "gates": gates,
        "subjects": {},
    }
    receipt = verifier.verify_result(result)
    assert receipt["software_integrity_pass"] is True
    assert receipt["strict_supported"] is False
    assert receipt["pre_prospective_ready"] is False
    assert receipt["reserved_stretched_n2_accessed"] is False
