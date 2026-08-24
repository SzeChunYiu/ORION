from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
RESULT = PAPER / "results" / "MATHLIB_TRANSFER_V2_1.json"
NULLS = PAPER / "results" / "MATHLIB_TRANSFER_V2_1_NULL_DISTRIBUTIONS.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_corrected_result_is_bound_to_frozen_inputs() -> None:
    result = json.loads(RESULT.read_text())
    assert result["protocol_sha256"] == sha256(HERE / "MATHLIB_TRANSFER_PROTOCOL_V2_1.json")
    assert result["manifest_sha256"] == sha256(HERE / "MATHLIB_CORPUS_V2_MANIFEST.json")
    assert result["null_distributions_sha256"] == sha256(NULLS)
    assert result["parser_sha256"] == "8f4abdc894c8f409fdfade4398d898f122f3349e26f8224acce163ce9916b013"


def test_corrected_numerical_conditions_do_not_promote_full_gate() -> None:
    result = json.loads(RESULT.read_text())
    gate = result["standalone_gate"]
    blocked = result["leave_top_module_out"]

    assert gate["numerical_conditions_pass"] is True
    assert gate["passes"] is False
    assert blocked["markov_minus_unigram"] >= 0.05
    assert blocked["bootstrap_95_percent_interval"]["interval"][0] > 0.0
    assert gate["native_receipts_condition"] == "PENDING_SEPARATE_NATIVE_REPLAY"
    assert gate["nearest_work_condition"] == "PENDING_CONSTRUCTIVE_SATURATION"


def test_every_frozen_null_is_significant_in_the_lower_tail() -> None:
    result = json.loads(RESULT.read_text())
    for seed in result["null_summary"].values():
        for family in seed.values():
            for ngram in family.values():
                assert ngram["p_two_sided"] <= 0.01
                assert ngram["p_lower"] < ngram["p_upper"]


def test_invalidated_v2_cannot_be_confused_with_v2_1() -> None:
    audit = json.loads((PAPER / "results" / "PARSER_CONTAMINATION_AUDIT_V2.json").read_text())
    assert audit["status"] == "INVALIDATES_MATHLIB_TRANSFER_V2"
    assert audit["contaminated_trajectories"] == 1289
    assert audit["intervening_top_level_boundaries"] == 3903
    assert sha256(RESULT) == "bd3b27849b31b93c0dc7bfe28f5984fac6888aa54141170c3d47999d67cbc24e"
