#!/usr/bin/env python3
"""Execute the frozen P1 mutation-necessity campaign after both identity freezes."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from orion.study.p1_causal.necessity_cases import (
    NecessityProtectedWorld,
    NecessityPublicWorld,
    NecessityWorld,
    ProbeResponse,
    PublicDependency,
    PublicDiagnosticProbe,
    PublicRepair,
    RepairLevel,
    RepairResponse,
)
from orion.study.p1_causal.necessity_engine import FrozenWorldSession
from orion.study.p1_causal.necessity_policies_v3 import ABLATION_ARMS, RUNNABLE_ARMS
from orion.study.p1_causal.necessity_scoring import (
    aggregate_necessity_scores,
    score_necessity_world,
)
from orion.study.p1_causal.necessity_statistics import analyze_necessity_campaign

ROOT = Path(__file__).resolve().parents[3]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _public(payload: dict[str, Any]) -> NecessityPublicWorld:
    return NecessityPublicWorld(
        task_id=str(payload["task_id"]),
        surface=str(payload["surface"]),
        initial_high_level_confidence=float(payload["initial_high_level_confidence"]),
        repairs=tuple(
            PublicRepair(
                repair_id=str(item["repair_id"]),
                level=RepairLevel(item["level"]),
                coordinate=str(item["coordinate"]),
                declared_cost=float(item["declared_cost"]),
                proposal_confidence=float(item["proposal_confidence"]),
            )
            for item in payload["repairs"]
        ),
        diagnostic_probes=tuple(
            PublicDiagnosticProbe(
                probe_id=str(item["probe_id"]),
                description=str(item["description"]),
                declared_cost=float(item["declared_cost"]),
            )
            for item in payload["diagnostic_probes"]
        ),
        dependencies=tuple(
            PublicDependency(
                closure_id=str(item["closure_id"]),
                parent_ids=tuple(str(value) for value in item["parent_ids"]),
                declared_coordinate=str(item["declared_coordinate"]),
            )
            for item in payload["dependencies"]
        ),
    )


def _protected(payload: dict[str, Any]) -> NecessityProtectedWorld:
    return NecessityProtectedWorld(
        family_id=str(payload["family_id"]),
        true_level=RepairLevel(payload["true_level"]),
        response_by_repair=tuple(
            (
                str(repair_id),
                RepairResponse(
                    target_success=bool(response["target_success"]),
                    protected_sibling_ok=bool(response["protected_sibling_ok"]),
                    observed_invalidated_ids=tuple(
                        str(item) for item in response["observed_invalidated_ids"]
                    ),
                ),
            )
            for repair_id, response in payload["response_by_repair"].items()
        ),
        response_by_probe=tuple(
            (str(probe_id), ProbeResponse(str(response["observation"])))
            for probe_id, response in payload["response_by_probe"].items()
        ),
        gold_minimal_repair_ids=tuple(
            str(item) for item in payload["gold_minimal_repair_ids"]
        ),
        gold_dependency_impact_ids=tuple(
            str(item) for item in payload["gold_dependency_impact_ids"]
        ),
        hidden_shift=bool(payload["hidden_shift"]),
        negative_control=bool(payload["negative_control"]),
    )


def load_worlds(world_dir: Path) -> tuple[NecessityWorld, ...]:
    public_rows = [
        json.loads(line)
        for line in (world_dir / "WORLD_PUBLIC.jsonl").read_text().splitlines()
    ]
    protected_rows = [
        json.loads(line)
        for line in (world_dir / "PROTECTED_RESPONSE_MATRIX.jsonl").read_text().splitlines()
    ]
    if [row["task_id"] for row in public_rows] != [row["task_id"] for row in protected_rows]:
        raise ValueError("public/protected task order mismatch")
    return tuple(
        NecessityWorld(_public(public_raw), _protected(protected_raw["protected"]))
        for public_raw, protected_raw in zip(public_rows, protected_rows, strict=True)
    )


def _verify(world_dir: Path, execution_path: Path) -> dict[str, Any]:
    execution = json.loads(execution_path.read_text())
    world_freeze_path = world_dir / "WORLD_FREEZE.json"
    world_freeze = json.loads(world_freeze_path.read_text())
    if execution.get("arms_executed") is not False or execution.get("outcome_accessed") is not False:
        raise ValueError("execution identity records prior outcome access")
    if _sha(world_freeze_path) != execution.get("world_freeze_sha256"):
        raise ValueError("world freeze identity mismatch")
    if _sha(world_dir / "WORLD_PUBLIC.jsonl") != execution.get("public_sha256"):
        raise ValueError("public world drift")
    if _sha(world_dir / "PROTECTED_RESPONSE_MATRIX.jsonl") != execution.get("protected_response_matrix_sha256"):
        raise ValueError("protected response-matrix drift")
    if world_freeze.get("protocol_chain", {}).get("chain_sha256") != execution.get("protocol_chain_sha256"):
        raise ValueError("protocol chain mismatch")
    for name, expected in execution.get("source_sha256", {}).items():
        if _sha(ROOT / name) != expected:
            raise ValueError(f"execution source drift:{name}")
    return execution


def execute(world_dir: Path, execution_path: Path, outdir: Path) -> dict[str, Any]:
    execution = _verify(world_dir, execution_path)
    worlds = load_worlds(world_dir)
    if len(worlds) != int(execution["n"]):
        raise ValueError("world count mismatch")

    budget = float(execution["intervention_budget_units"])
    raw_rows: list[dict[str, Any]] = []
    primary_scores: list[dict[str, Any]] = []
    by_arm = defaultdict(list)
    for world in worlds:
        for policy in RUNNABLE_ARMS:
            session = FrozenWorldSession(world.public, world.protected, budget=budget)
            outcome = policy(session)
            score = score_necessity_world(world, outcome.to_payload())
            row = {
                "task_id": world.public.task_id,
                "family_id": world.protected.family_id,
                "arm_id": score.arm_id,
                "outcome": outcome.to_payload(),
                "score": score.to_payload(),
            }
            raw_rows.append(row)
            primary_scores.append(score.to_payload())
            by_arm[score.arm_id].append(score)

        for policy in ABLATION_ARMS:
            ablation_budget = (
                99.0
                if policy.__name__ == "orion_with_unlimited_intervention_budget"
                else budget
            )
            session = FrozenWorldSession(
                world.public,
                world.protected,
                budget=ablation_budget,
            )
            outcome = policy(session)
            score = score_necessity_world(world, outcome.to_payload())
            raw_rows.append(
                {
                    "task_id": world.public.task_id,
                    "family_id": world.protected.family_id,
                    "arm_id": score.arm_id,
                    "outcome": outcome.to_payload(),
                    "score": score.to_payload(),
                    "ablation": True,
                }
            )
            by_arm[score.arm_id].append(score)

    analysis = analyze_necessity_campaign(
        primary_scores,
        full_arm="orion_mutation_necessity",
        h1_parents=tuple(str(item) for item in execution["h1_parents"]),
        control_parent=str(execution["control_parent"]),
        parameters=execution["statistics"],
    )
    arm_summary = {
        arm: aggregate_necessity_scores(tuple(scores))
        for arm, scores in by_arm.items()
    }

    outdir.mkdir(parents=True, exist_ok=True)
    raw_path = outdir / "RAW_RESULTS.jsonl"
    raw_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in raw_rows
        )
    )
    terminal = (
        "P1_MUTATION_NECESSITY_SUPPORTED"
        if bool(analysis["all_support_gates_pass"])
        else "P1_MUTATION_NECESSITY_NOT_SUPPORTED"
    )
    result = {
        "schema_version": "P1.epistemic-mutation-necessity-result.v1",
        "terminal": terminal,
        "n_worlds": len(worlds),
        "n_runnable_arms": len(RUNNABLE_ARMS),
        "n_ablation_arms": len(ABLATION_ARMS),
        "execution_freeze_sha256": _sha(execution_path),
        "raw_results_sha256": _sha(raw_path),
        "analysis": analysis,
        "arm_summary": arm_summary,
        "oracle_minimal_valid_ceiling": {
            "protected_root_task_success_rate": 1.0,
            "runnable": False,
            "reason": "host-only protected response matrix / gold minimal repair ids",
        },
        "claim_boundary": (
            "CREDENTIAL_FREE_MECHANICAL_P1_NECESSITY_RESULT_ONLY__"
            "V1_H1_HISTORY_UNCHANGED__NO_MODEL_GENERAL_OR_OPEN_ENDED_SUPERIORITY"
        ),
    }
    (outdir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world-dir", type=Path, required=True)
    parser.add_argument("--execution-freeze", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.world_dir, args.execution_freeze, args.outdir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
