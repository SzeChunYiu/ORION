#!/usr/bin/env python3
"""Focused integrity and denominator verifier for P2-DES-01."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED = (
    "FREEZE_V1.json",
    "RAW_MANIFEST_V1.json",
    "RAW_POLICY_OUTCOMES_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "RESULT_BINDING_PACKET_V1.json",
)
TOPICS = {str(index) for index in range(1, 51)}
POLICIES = {
    "BM25_QUESTION",
    "LOCAL_MULTIFORM_RRF",
    "DIVERSIFIED_ROUND_ROBIN",
    "LOCAL_SATURATION_STOP",
    "RANDOM_REMOTE",
    "ANALOGY_PRF",
    "STRUCTURAL_JUMP",
    "IDEAL_DONOR_PRODUCT_RRF",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    root = args.result_dir.resolve()
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    assert not missing, f"missing required artifacts: {missing}"

    freeze = load(root / "FREEZE_V1.json")
    manifest = load(root / "RAW_MANIFEST_V1.json")
    raw = load(root / "RAW_POLICY_OUTCOMES_V1.json")
    primary = load(root / "PRIMARY_RESULT_V1.json")
    donor = load(root / "IDEAL_DONOR_RESULT_V1.json")
    controls = load(root / "NEGATIVE_CONTROLS_V1.json")
    resources = load(root / "RESOURCE_LEDGER_V1.json")
    transfer = load(root / "TRANSFER_RESULT_V1.json")
    packet = load(root / "RESULT_BINDING_PACKET_V1.json")

    assert freeze["job_id"] == "P2-DES-01"
    assert freeze["outcomes_accessed_before_freeze"] is False
    assert primary["exact_terminal"] == packet["exact_terminal"]
    assert packet["exact_terminal"] == "CANNOT_CHECK_STRONG_DONOR_OR_TRANSFER_BINDING_UNAVAILABLE"
    assert packet["computation_session_paper_authority_delta"] == "NONE"
    assert packet["manuscript_writing_owner"] == "P1_P15_REWRITE_LANE"
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert donor["material_donor"]["proxy_substitution"] is False
    assert transfer["licensed_review_world"]["status"] == "CANNOT_CHECK"
    assert transfer["reminted_cross_domain_world"]["status"] == "CANNOT_CHECK"
    assert resources["censoring"]["status"] == "NOT_CENSORED"
    assert controls["label_leakage_probe"]["status"] == "PASS_INTERNAL_CONFORMANCE"

    rows = raw["case_policy_rows"]
    assert len(rows) == 400
    keys = {(row["topic_id"], row["policy_id"]) for row in rows}
    assert len(keys) == 400
    assert {topic for topic, _ in keys} == TOPICS
    assert {policy for _, policy in keys} == POLICIES
    assert all(row["status"] == "SCORED" for row in rows)
    assert all(0.0 <= row["recall_at_100_budget"] <= 1.0 for row in rows)
    assert all(0.0 <= row["qrels_bounded_residual_fraction"] <= 1.0 for row in rows)
    assert all(row["unique_documents_returned"] == row["returned_depth"] for row in rows)
    assert all(row["returned_depth"] <= 100 for row in rows)
    assert all(row["registered_query_calls"] <= 4 for row in rows)

    denominators = packet["denominators"]
    assert denominators["frozen_topics"] == 50
    assert denominators["scored_topics"] == 50
    assert denominators["case_policy_rows_expected"] == 400
    assert denominators["case_policy_rows_retained"] == 400
    assert denominators["dropped_topics"] == 0
    assert denominators["dropped_case_policy_rows"] == 0
    assert denominators["crashed_case_policy_rows"] == 0

    pre_score = root / "PRE_SCORE_POLICY_OUTPUTS_V1.json"
    assert pre_score.is_file()
    assert manifest["input_bindings"]["qrels_opened_only_after_pre_score_policy_outputs_sha256"] == digest(pre_score)
    bound = {entry["path"]: entry["sha256"] for entry in packet["digests"]["artifacts"]}
    for name, expected in bound.items():
        assert digest(root / name) == expected, f"digest mismatch: {name}"
    assert packet["digests"]["freeze_sha256"] == digest(root / "FREEZE_V1.json")
    assert packet["digests"]["raw_sha256"] == digest(root / "RAW_POLICY_OUTCOMES_V1.json")
    assert len(packet["case_level_outcomes"]) == 400

    print(
        "P2_DES_01_FOCUSED_VERIFICATION_PASS "
        f"topics=50 policies=8 rows=400 terminal={packet['exact_terminal']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

