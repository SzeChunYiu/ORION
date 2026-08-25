#!/usr/bin/env python3
"""Frozen SciFact semantic-coordinate execution for P4-DES-01."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import re
import time
from typing import Any


JOB = "P4-DES-01"
CANNOT = "EXTERNAL_PROMOTION_TERMINAL_GOLD_UNAVAILABLE"
CEILING = (
    "SCIFACT_EXTERNAL_SEMANTIC_COORDINATE_AND_INTERNAL_POLICY_DIVERGENCE_ONLY__"
    "NO_INDEPENDENT_PROMOTION_TERMINAL_TRUTH__NO_POLICY_SUPERIORITY"
)
OBLIGATIONS = (
    "claim_scope_conformance",
    "evidence_independence",
    "provenance_and_artifact_version_binding",
    "contamination_defense",
    "scientific_authority_resolution",
)
ARMS = (
    "DYNAMIC_NONCOMPENSATORY",
    "EVIDENCE_ONLY",
    "CONFIDENCE_ONLY",
    "PROVENANCE_ONLY",
    "IDEAL_TYPED_PRODUCT",
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def compose_verdict(evidence: dict[str, Any]) -> str:
    labels = {row.get("label") for rows in evidence.values() for row in rows}
    if not evidence:
        return "NOT_ENOUGH_INFO"
    if "CONTRADICT" in labels:
        return "CONTRADICT"
    if "SUPPORT" in labels:
        return "SUPPORT"
    return "NOT_ENOUGH_INFO"


def obligations_for(claim: dict[str, Any], corpus: set[int], train_text: set[str]) -> dict[str, bool]:
    evidence = claim.get("evidence") or {}
    cited = {str(item) for item in claim.get("cited_doc_ids", [])}
    labels = {row.get("label") for rows in evidence.values() for row in rows}
    return {
        "claim_scope_conformance": set(evidence) <= cited,
        "evidence_independence": len(evidence) >= 2,
        "provenance_and_artifact_version_binding": all(int(item) in corpus for item in cited) if cited else False,
        "contamination_defense": claim["claim"].strip().lower() not in train_text,
        "scientific_authority_resolution": len(labels) <= 1,
    }


def terminal(verdict: str, obligations: dict[str, bool], arm: str) -> str:
    if arm in {"CONFIDENCE_ONLY", "IDEAL_TYPED_PRODUCT"}:
        return "CANNOT_CHECK_ARM_UNAVAILABLE"
    if arm == "PROVENANCE_ONLY":
        return "PROMOTE" if obligations["provenance_and_artifact_version_binding"] else "CANNOT_CHECK"
    if verdict == "CONTRADICT":
        return "BLOCK"
    if verdict == "NOT_ENOUGH_INFO":
        return "CANNOT_CHECK"
    if arm == "EVIDENCE_ONLY":
        return "PROMOTE"
    if arm == "DYNAMIC_NONCOMPENSATORY":
        return "PROMOTE" if all(obligations[name] for name in OBLIGATIONS) else "CANNOT_CHECK"
    raise ValueError(f"unknown arm:{arm}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("invalid execution head")
    start_wall = time.monotonic_ns()
    start_cpu = time.process_time_ns()
    repo = args.repo.resolve()
    bundle = args.bundle.resolve()
    data = args.data_dir.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p4_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_repo_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"frozen repo input drift:{item['path']}")
    for item in freeze["data_inputs"]:
        path = data / item["name"]
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"data input drift:{item['name']}")

    dev = [json.loads(line) for line in (data / "claims_dev.jsonl").open()]
    train = [json.loads(line) for line in (data / "claims_train.jsonl").open()]
    corpus = {json.loads(line)["doc_id"] for line in (data / "corpus.jsonl").open()}
    if len(dev) != freeze["case_denominator"]:
        raise SystemExit("held-out denominator drift")
    train_text = {row["claim"].strip().lower() for row in train}

    rows: list[dict[str, Any]] = []
    for claim in dev:
        verdict = compose_verdict(claim.get("evidence") or {})
        obligations = obligations_for(claim, corpus, train_text)
        arm_rows = {
            arm: {
                "execution_state": "UNAVAILABLE_CANNOT_CHECK" if arm in {"CONFIDENCE_ONLY", "IDEAL_TYPED_PRODUCT"} else "EXECUTED",
                "terminal": terminal(verdict, obligations, arm),
                "external_terminal_score_state": "CANNOT_CHECK__NO_EXTERNAL_PROMOTION_GOLD",
            }
            for arm in ARMS
        }
        rows.append(
            {
                "case_id": claim["id"],
                "semantic_gold": verdict,
                "obligations": obligations,
                "external_promotion_terminal_gold": None,
                "arms": arm_rows,
            }
        )

    summary: dict[str, Any] = {}
    for arm in ARMS:
        outputs = [row["arms"][arm]["terminal"] for row in rows]
        summary[arm] = {
            "terminal_counts": dict(Counter(outputs)),
            "mechanically_executed_cases": 0 if arm in {"CONFIDENCE_ONLY", "IDEAL_TYPED_PRODUCT"} else len(rows),
            "scientifically_scored_against_external_terminal_gold": 0,
            "semantic_false_promotions": sum(
                1 for row in rows if row["arms"][arm]["terminal"] == "PROMOTE" and row["semantic_gold"] != "SUPPORT"
            ),
            "promotions_with_undischarged_obligation": sum(
                1 for row in rows if row["arms"][arm]["terminal"] == "PROMOTE" and not all(row["obligations"].values())
            ),
        }
    metric_states = {
        "false_promotion_against_external_terminal_gold": "CANNOT_CHECK",
        "macro_f1_against_external_terminal_gold": "CANNOT_CHECK",
        "rationale_f1": "CANNOT_CHECK__NO_MODEL_RATIONALE_OUTPUTS",
        "stale_promotion": "CANNOT_CHECK__NO_EPOCH_TRANSITIONS",
        "valid_positive_retention": "CANNOT_CHECK__NO_EXTERNAL_PROMOTION_GOLD",
        "semantic_false_promotion": "DESCRIPTIVE_EXTERNAL_SEMANTIC_COORDINATE_ONLY",
    }
    campaign = {
        "schema": "orion.p4.dynamic-promotion-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "case_denominator": len(rows),
        "arm_denominator": len(ARMS),
        "arm_case_denominator": len(rows) * len(ARMS),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows) * 2,
        "externally_terminal_scored_cases": 0,
        "semantic_gold_counts": dict(Counter(row["semantic_gold"] for row in rows)),
        "metric_states": metric_states,
        "arm_summary": summary,
        "rows": rows,
        "exact_terminal": CANNOT,
        "authority_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": CANNOT,
        "case_denominator": len(rows),
        "arm_case_denominator": len(rows) * len(ARMS),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows) * 2,
        "externally_terminal_scored_cases": 0,
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "MIXED",
        "executed_donors": ["EVIDENCE_ONLY", "PROVENANCE_ONLY"],
        "unavailable_donors": ["CONFIDENCE_ONLY", "IDEAL_TYPED_PRODUCT"],
        "reason": "confidence outputs and an independently specified ideal typed product were not transferred",
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_SELF_DEFINED_TERMINAL_GOLD", "passed": True},
            {"id": "NO_CONFIDENCE_PROXY", "passed": True},
            {"id": "NO_IDEAL_PRODUCT_PROXY", "passed": True},
            {"id": "NO_CONSTANT_ABLATION_AS_MEASURED_NULL", "passed": True},
            {"id": "ALL_CASES_RETAINED", "passed": len(rows) == freeze["case_denominator"]},
        ],
        "all_pass": len(rows) == freeze["case_denominator"],
    }
    elapsed = time.monotonic_ns() - start_wall
    cpu = time.process_time_ns() - start_cpu
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {
            "case_rows": len(rows),
            "arm_cases": len(rows) * len(ARMS),
            "cpu_nanoseconds": cpu,
            "wall_nanoseconds": elapsed,
            "gpu": 0,
            "network_calls": 0,
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "cap_hit": False,
        "censored": False,
    }
    transfer = {"schema": "orion.des.transfer-result.v1", "job_id": JOB, "state": "CANNOT_CHECK", "reason": CANNOT, "authority_delta": "NONE"}
    outputs = {
        "P4_DYNAMIC_PROMOTION_RESULT_V1.json": campaign,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, value in outputs.items():
        write(out / name, value)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": sha(freeze_path),
        "runner_sha256": sha(runner_path),
        "data_inputs": freeze["data_inputs"],
        "outputs": {name: {"bytes": (out / name).stat().st_size, "sha256": sha(out / name)} for name in sorted(outputs)},
    }
    write(out / "RAW_MANIFEST_V1.json", manifest)
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": sha(freeze_path),
        "raw_manifest_sha256": sha(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": len(rows),
        "arm_case_denominator": len(rows) * len(ARMS),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows) * 2,
        "externally_terminal_scored_cases": 0,
        "hard_preconditions": {
            "external_semantic_gold": True,
            "independent_promotion_terminal_gold": False,
            "confidence_outputs": False,
            "ideal_typed_product": False,
            "epoch_transition_cases": False,
            "protected_v2_raw_custody": False,
        },
        "leakage": {"self_defined_terminal_gold": False, "confidence_proxy_substituted": False, "ideal_product_proxy_substituted": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": CANNOT,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={CANNOT} cases={len(rows)} arm_cases={len(rows)*len(ARMS)} executed={len(rows)*3} unavailable={len(rows)*2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
