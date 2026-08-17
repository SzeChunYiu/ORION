#!/usr/bin/env python3
"""Execute the frozen P1 R3 authority-value campaign on an already-bound holdout."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from orion.study.p1_causal.authority_value_cases import (
    ActionRequest,
    AuthorityValueTask,
    DiagnosisPacket,
    ProtectedAuthorityGold,
    PublicAuthorityView,
    PublicClosure,
    RepairProposal,
    ResponsibilityClass,
    TaskAction,
)
from orion.study.p1_causal.authority_value_policies import MATCHED_ARMS
from orion.study.p1_causal.authority_value_scoring import aggregate_scores, score_task
from orion.study.p1_causal.authority_value_statistics import analyze_campaign

ROOT = Path(__file__).resolve().parents[3]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _public_from_payload(payload: dict[str, Any]) -> PublicAuthorityView:
    diagnosis_raw = payload["diagnosis"]
    diagnosis = DiagnosisPacket(
        responsibility=ResponsibilityClass(diagnosis_raw["responsibility"]),
        intervention_backed=bool(diagnosis_raw["intervention_backed"]),
        diagnosed_coordinate=str(diagnosis_raw["diagnosed_coordinate"]),
        evidence_ids=tuple(str(item) for item in diagnosis_raw["evidence_ids"]),
    )
    proposals = tuple(
        RepairProposal(
            proposal_id=str(item["proposal_id"]),
            requests=tuple(
                ActionRequest(
                    TaskAction(request["action"]),
                    str(request.get("coordinate", "")),
                )
                for request in item["requests"]
            ),
            predicts_root_recovery=bool(item["predicts_root_recovery"]),
        )
        for item in payload["proposals"]
    )
    closures = tuple(
        PublicClosure(
            closure_id=str(item["closure_id"]),
            dependency_coordinates=tuple(str(value) for value in item["dependency_coordinates"]),
            parent_ids=tuple(str(value) for value in item.get("parent_ids", ())),
        )
        for item in payload["closures"]
    )
    return PublicAuthorityView(
        task_id=str(payload["task_id"]),
        surface=str(payload["surface"]),
        diagnosis=diagnosis,
        proposals=proposals,
        closures=closures,
    )


def _gold_from_payload(payload: dict[str, Any]) -> tuple[str, ProtectedAuthorityGold]:
    raw = payload["gold"]
    action_text = str(raw.get("required_action", ""))
    gold = ProtectedAuthorityGold(
        required_action=TaskAction(action_text) if action_text else None,
        required_coordinate=str(raw.get("required_coordinate", "")),
        repair_available=bool(raw["repair_available"]),
        should_block=bool(raw["should_block"]),
        required_reopen_ids=tuple(str(item) for item in raw["required_reopen_ids"]),
        unrelated_verified_closure_ids=tuple(
            str(item) for item in raw["unrelated_verified_closure_ids"]
        ),
        negative_history_required=bool(raw.get("negative_history_required", True)),
    )
    return str(payload["family_id"]), gold


def _load_tasks(holdout_dir: Path) -> tuple[AuthorityValueTask, ...]:
    public_rows = [json.loads(line) for line in (holdout_dir / "PUBLIC_CASES.jsonl").read_text().splitlines()]
    gold_rows = [json.loads(line) for line in (holdout_dir / "PROTECTED_GOLD.jsonl").read_text().splitlines()]
    if [row["task_id"] for row in public_rows] != [row["task_id"] for row in gold_rows]:
        raise ValueError("public/gold row identity mismatch")
    tasks: list[AuthorityValueTask] = []
    for public_raw, gold_raw in zip(public_rows, gold_rows, strict=True):
        public = _public_from_payload(public_raw)
        family, gold = _gold_from_payload(gold_raw)
        tasks.append(AuthorityValueTask(family, public, gold))
    return tuple(tasks)


def _verify_execution_identity(holdout_dir: Path, execution_freeze_path: Path) -> dict[str, Any]:
    freeze = json.loads(execution_freeze_path.read_text())
    holdout_path = holdout_dir / "HOLDOUT_FREEZE.json"
    holdout = json.loads(holdout_path.read_text())
    if freeze.get("arms_executed") is not False or freeze.get("outcome_accessed") is not False:
        raise ValueError("execution freeze already records outcome access")
    if _sha(holdout_path) != freeze.get("holdout_freeze_sha256"):
        raise ValueError("holdout freeze identity mismatch")
    for name, expected in freeze.get("source_sha256", {}).items():
        actual = _sha(ROOT / name)
        if actual != expected:
            raise ValueError(f"execution source drift:{name}")
    if _sha(holdout_dir / "PUBLIC_CASES.jsonl") != freeze.get("public_sha256"):
        raise ValueError("public holdout drift")
    if _sha(holdout_dir / "PROTECTED_GOLD.jsonl") != freeze.get("protected_gold_sha256"):
        raise ValueError("protected gold drift")
    if holdout.get("public_sha256") != freeze.get("public_sha256"):
        raise ValueError("holdout/execution public binding mismatch")
    return freeze


def execute(holdout_dir: Path, execution_freeze_path: Path, outdir: Path) -> dict[str, Any]:
    freeze = _verify_execution_identity(holdout_dir, execution_freeze_path)
    tasks = _load_tasks(holdout_dir)
    if len(tasks) != int(freeze["n"]):
        raise ValueError("task count mismatch")

    raw_rows: list[dict[str, Any]] = []
    scores_by_arm: dict[str, list] = defaultdict(list)
    catastrophic_by_arm: dict[str, int] = defaultdict(int)
    for task in tasks:
        for policy in MATCHED_ARMS:
            outcome = policy(task.public)
            outcome_payload = outcome.to_payload()
            score = score_task(task, outcome_payload)
            scores_by_arm[outcome.arm_id].append(score)
            for request in outcome.applied_requests:
                if request.action in {TaskAction.BROAD_WM_MUTATION, TaskAction.REWRITE_METHOD}:
                    catastrophic_by_arm[outcome.arm_id] += 1
            raw_rows.append(
                {
                    "task_id": task.public.task_id,
                    "family_id": task.family_id,
                    "arm_id": outcome.arm_id,
                    "outcome": outcome_payload,
                    "score": score.to_payload(),
                }
            )

    score_rows = [row["score"] for row in raw_rows]
    params = freeze["decision_parameters"]
    analysis = analyze_campaign(
        score_rows,
        primary_arm=str(freeze["primary_arm"]),
        comparator_arm=str(freeze["primary_comparator"]),
        bootstrap_seed=int(params["paired_bootstrap_seed"]),
        superiority_margin=float(params["scientifically_valid_repair_superiority_margin"]),
        unauthorized_ceiling=float(params["unauthorized_epistemic_mutation_ceiling"]),
        recovery_noninferiority_margin=float(params["root_task_recovery_noninferiority_margin"]),
    )
    primary_catastrophic = catastrophic_by_arm[str(freeze["primary_arm"])]
    catastrophic_gate = primary_catastrophic == 0
    terminal = (
        "P1_AUTHORITY_VALUE_SUPPORTED"
        if bool(analysis["all_primary_gates_pass"]) and catastrophic_gate
        else "P1_AUTHORITY_VALUE_NOT_SUPPORTED"
    )

    arm_summary = {
        arm_id: {
            **aggregate_scores(tuple(scores)),
            "catastrophic_protected_action_count": catastrophic_by_arm[arm_id],
        }
        for arm_id, scores in scores_by_arm.items()
    }
    family_summary: dict[str, dict[str, dict[str, float | int]]] = {}
    for family in sorted({task.family_id for task in tasks}):
        family_summary[family] = {}
        for arm_id in scores_by_arm:
            selected = tuple(
                score for score in scores_by_arm[arm_id] if score.family_id == family
            )
            family_summary[family][arm_id] = aggregate_scores(selected)

    outdir.mkdir(parents=True, exist_ok=True)
    raw_path = outdir / "RAW_RESULTS.jsonl"
    raw_path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in raw_rows)
    )
    result = {
        "schema_version": "P1.authority-value-result.v1",
        "terminal": terminal,
        "n_tasks": len(tasks),
        "n_arms": len(MATCHED_ARMS),
        "raw_results_sha256": _sha(raw_path),
        "execution_freeze_sha256": _sha(execution_freeze_path),
        "analysis": analysis,
        "catastrophic_protected_action_gate": {
            "count": primary_catastrophic,
            "passed": catastrophic_gate,
        },
        "arm_summary": arm_summary,
        "family_summary": family_summary,
        "claim_boundary": "SCOPED_R3_AUTHORITY_VALUE_RESULT__V1_H1_UNCHANGED__NO_GENERAL_DIAGNOSIS_OR_NOVELTY_CLAIM",
    }
    (outdir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--holdout-dir", type=Path, required=True)
    parser.add_argument("--execution-freeze", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.holdout_dir, args.execution_freeze, args.outdir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
