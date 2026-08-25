#!/usr/bin/env python3
"""Execute the frozen DES-COLLISION-01 finite collision census.

This runner establishes finite conformance/non-reconstruction witnesses only.
It cannot grant empirical, novelty, journal, or external authority.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any


JOB_ID = "DES-COLLISION-01"
SUBJECT_REVISION = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
BASE_MAIN = "f049e30391a09213240f6325ee319f9fa811189a"
POSITIVE = "DYNAMIC_STATE_STRICTLY_DISTINGUISHES_LEGACY_COLLISIONS"
NEGATIVE = "NO_MINIMAL_LABEL_DECISION_COLLISION_IN_FROZEN_CLASS"
AUTHORITY_CEILING = (
    "FINITE_DECLARED_STATE_CLASS_NONRECONSTRUCTION_WITNESS_ONLY__"
    "NO_EMPIRICAL_SUPERIORITY__NO_EXTERNAL_AUTHORITY"
)
AXES = {
    "identifiability": ("KNOWN_TRUE", "KNOWN_FALSE", "CANNOT_CHECK"),
    "obligations": ("SATISFIED", "UNRESOLVED"),
    "support": ("COMPLETE", "ABSENT"),
    "defeaters": ("ABSENT", "PRESENT"),
    "custody": ("EXTERNAL", "NOT_EXTERNAL", "CANNOT_CHECK"),
    "authority": ("PRESENT", "ABSENT"),
}
ACTION_PRECEDENCE = (
    "DISCRIMINATE_IDENTIFIABILITY",
    "ACQUIRE_UNRESOLVED_OBLIGATION",
    "ACQUIRE_COMPLETE_SUPPORT",
    "REVALIDATE_DEFEATER",
    "OBTAIN_EXTERNAL_CUSTODY",
    "REVALIDATE_AUTHORITY_SCOPE",
    "STOP",
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def write_json(path: Path, payload: Any) -> None:
    path.write_bytes(canonical(payload))


def load_model(root: Path):
    path = root / "src/orion/epistemic_state_v1/model.py"
    spec = importlib.util.spec_from_file_location("des_collision_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen dynamic-state model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def coordinate(model, value: Any, status=None):
    return model.Coordinate(
        value=value,
        status=status or model.Status.KNOWN,
        scope="DES-COLLISION-01:FINITE",
        epoch=0,
        provenance_ids=("freeze:DES-COLLISION-01",),
        estimator_version="des-collision-v1",
    )


def build_state(model, case_id: str, axes: dict[str, str]):
    ident = axes["identifiability"]
    if ident == "CANNOT_CHECK":
        ident_coordinate = coordinate(model, None, model.Status.CANNOT_CHECK)
    else:
        ident_coordinate = coordinate(model, ident == "KNOWN_TRUE")
    obligations = frozenset({"promotion:identified-support"})
    satisfied = obligations if axes["obligations"] == "SATISFIED" else frozenset()
    support = (
        (
            model.SupportFamily(
                "support:complete",
                frozenset({"premise:finite"}),
                obligations,
            ),
        )
        if axes["support"] == "COMPLETE"
        else ()
    )
    custody = {
        "EXTERNAL": True,
        "NOT_EXTERNAL": False,
        "CANNOT_CHECK": None,
    }[axes["custody"]]
    return model.State(
        subject_id=case_id,
        responsibility_id="PROMOTE",
        epoch=0,
        evidence=coordinate(model, Fraction(1, 1)),
        identifiability=ident_coordinate,
        coverage=coordinate(model, Fraction(1, 1)),
        obligations_required=obligations,
        obligations_satisfied=satisfied,
        provenance=coordinate(model, True),
        verification=coordinate(model, True),
        authority_scopes=(
            frozenset({"PROMOTE"}) if axes["authority"] == "PRESENT" else frozenset()
        ),
        support_families=support,
        active_defeaters=(
            frozenset({"defeater:finite"})
            if axes["defeaters"] == "PRESENT"
            else frozenset()
        ),
        custody_external=custody,
        method_reach_ids=frozenset({"method:finite"}),
        knowledge_node_ids=frozenset({"node:finite"}),
        knowledge_edge_ids=frozenset({"edge:finite"}),
    )


def next_action(model, state) -> tuple[str, str]:
    if (
        state.identifiability.status is model.Status.CANNOT_CHECK
        or not bool(state.identifiability.value)
    ):
        return model.Action.DISCRIMINATE.value, ACTION_PRECEDENCE[0]
    if state.unresolved:
        return model.Action.ACQUIRE_EVIDENCE.value, ACTION_PRECEDENCE[1]
    if not state.complete_support():
        return model.Action.ACQUIRE_EVIDENCE.value, ACTION_PRECEDENCE[2]
    if state.active_defeaters:
        return model.Action.REVALIDATE.value, ACTION_PRECEDENCE[3]
    if state.custody_external is not True:
        return model.Action.OBTAIN_EXTERNAL_CUSTODY.value, ACTION_PRECEDENCE[4]
    if "PROMOTE" not in state.authority_scopes:
        return model.Action.REVALIDATE.value, ACTION_PRECEDENCE[5]
    return model.Action.STOP.value, ACTION_PRECEDENCE[6]


def enumerate_rows(model) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keys = tuple(AXES)
    for index, values in enumerate(itertools.product(*(AXES[key] for key in keys))):
        axes = dict(zip(keys, values, strict=True))
        case_id = f"DES-COLLISION-01-{index:03d}"
        state = build_state(model, case_id, axes)
        terminal = model.promotion_policy("PROMOTE").project(state).value
        action, rationale = next_action(model, state)
        rows.append(
            {
                "case_id": case_id,
                "axes": axes,
                "legacy_terminal": terminal,
                "dynamic_next_action": action,
                "action_rationale": rationale,
            }
        )
    return rows


def hamming(left: dict[str, str], right: dict[str, str]) -> int:
    return sum(left[key] != right[key] for key in AXES)


def collision_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    collisions: list[dict[str, Any]] = []
    same_label_pairs = 0
    all_pairs = 0
    for left, right in itertools.combinations(rows, 2):
        all_pairs += 1
        if left["legacy_terminal"] != right["legacy_terminal"]:
            continue
        same_label_pairs += 1
        if left["dynamic_next_action"] == right["dynamic_next_action"]:
            continue
        collisions.append(
            {
                "left_case_id": left["case_id"],
                "right_case_id": right["case_id"],
                "legacy_terminal": left["legacy_terminal"],
                "left_action": left["dynamic_next_action"],
                "right_action": right["dynamic_next_action"],
                "axis_hamming_distance": hamming(left["axes"], right["axes"]),
                "differing_axes": [
                    key for key in AXES if left["axes"][key] != right["axes"][key]
                ],
            }
        )
    collisions.sort(
        key=lambda row: (
            row["axis_hamming_distance"],
            row["legacy_terminal"],
            row["left_action"],
            row["right_action"],
            row["left_case_id"],
            row["right_case_id"],
        )
    )
    return collisions, same_label_pairs, all_pairs


def minimal_witnesses(collisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[tuple[str, tuple[str, str]], dict[str, Any]] = {}
    for row in collisions:
        action_pair = tuple(sorted((row["left_action"], row["right_action"])))
        key = (row["legacy_terminal"], action_pair)
        selected.setdefault(key, row)
    return [selected[key] for key in sorted(selected)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--executed-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / "research/orion-epistemic-state-v1/results" / JOB_ID
    freeze_path = out / "FREEZE_V1.json"
    freeze = json.loads(freeze_path.read_text())
    if freeze["subject_revision"] != SUBJECT_REVISION or freeze["base_main"] != BASE_MAIN:
        raise SystemExit("frozen revision drift")
    model_path = root / freeze["implementation"]["model_path"]
    runner_path = out / "run_des_collision_01.py"
    if digest_file(model_path) != freeze["implementation"]["model_sha256"]:
        raise SystemExit("model digest drift")
    if digest_file(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")

    started = time.monotonic_ns()
    model = load_model(root)
    rows = enumerate_rows(model)
    collisions, same_label_pairs, all_pairs = collision_rows(rows)
    witnesses = minimal_witnesses(collisions)
    elapsed_ns = time.monotonic_ns() - started
    minimum_distance = min((row["axis_hamming_distance"] for row in collisions), default=None)
    terminal = POSITIVE if minimum_distance == 1 else NEGATIVE
    label_actions: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label_actions[row["legacy_terminal"]][row["dynamic_next_action"]] += 1
    ideal_label_only = {
        label: sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        for label, counts in label_actions.items()
    }
    label_only_correct = sum(
        ideal_label_only[row["legacy_terminal"]] == row["dynamic_next_action"]
        for row in rows
    )

    atlas = {
        "schema": "orion.des.label-decision-collision-atlas.v1",
        "job_id": JOB_ID,
        "subject_revision": SUBJECT_REVISION,
        "finite_class": {"axes": AXES, "case_count": len(rows)},
        "denominators": {
            "all_state_pairs": all_pairs,
            "same_legacy_terminal_pairs": same_label_pairs,
            "different_action_collision_pairs": len(collisions),
        },
        "terminal_counts": dict(sorted(Counter(row["legacy_terminal"] for row in rows).items())),
        "action_counts": dict(sorted(Counter(row["dynamic_next_action"] for row in rows).items())),
        "label_action_counts": {
            label: dict(sorted(counts.items())) for label, counts in sorted(label_actions.items())
        },
        "minimum_collision_hamming_distance": minimum_distance,
        "case_rows": rows,
        "collision_rows": collisions,
        "terminal": terminal,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    witnesses_payload = {
        "schema": "orion.des.minimal-collision-witnesses.v1",
        "job_id": JOB_ID,
        "selection_rule": (
            "lexicographically first minimum-Hamming witness per legacy-terminal/"
            "unordered-action-pair"
        ),
        "witness_count": len(witnesses),
        "witnesses": witnesses,
        "terminal": terminal,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "terminal": terminal,
        "case_count": len(rows),
        "minimum_collision_hamming_distance": minimum_distance,
        "collision_pair_count": len(collisions),
        "claim_ceiling": AUTHORITY_CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "donor": "BEST_DETERMINISTIC_LEGACY_LABEL_ONLY_ACTION_POLICY",
        "frozen_objective": "exact_next_action_reconstruction_on_complete_finite_class",
        "tie_break": "lexicographic_action_id",
        "selected_action_by_label": ideal_label_only,
        "correct_cases": label_only_correct,
        "total_cases": len(rows),
        "fully_reconstructs_dynamic_actions": label_only_correct == len(rows),
        "donor_authority": "FINITE_CLASS_CONTROL_ONLY",
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": [
            {
                "control_id": "LABEL_ONLY_NONRECONSTRUCTION",
                "passed": label_only_correct < len(rows),
                "error_cases": len(rows) - label_only_correct,
            },
            {
                "control_id": "ONE_AXIS_MINIMALITY",
                "passed": minimum_distance == 1,
                "minimum_hamming_distance": minimum_distance,
            },
            {
                "control_id": "ADVERSE_ROWS_RETAINED",
                "passed": len(rows) == 144 and len(collisions) > 0,
                "retained_collision_pairs": len(collisions),
            },
        ],
        "all_pass": label_only_correct < len(rows) and minimum_distance == 1,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB_ID,
        "resource_vector": {
            "acquisition": 0,
            "state_cases": len(rows),
            "pair_comparisons": all_pairs,
            "reasoning": "deterministic_finite_enumeration",
            "verification": len(witnesses),
            "recovery": 0,
            "elapsed_monotonic_ns": elapsed_ns,
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "cap_hit": False,
        "censored": False,
    }
    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": JOB_ID,
        "state": "CANNOT_CHECK",
        "reason": "NO_EXTERNAL_OR_NATURALISTIC_TRANSFER_IN_FROZEN_FINITE_CLASS",
        "authority_delta": "NONE",
    }

    outputs = {
        "LABEL_DECISION_COLLISION_ATLAS_V1.json": atlas,
        "MINIMAL_COLLISION_WITNESSES_V1.json": witnesses_payload,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, payload in outputs.items():
        write_json(out / name, payload)
    raw_manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB_ID,
        "subject_revision": SUBJECT_REVISION,
        "freeze_sha256": digest_file(freeze_path),
        "implementation": {
            "model_path": str(model_path.relative_to(root)),
            "model_sha256": digest_file(model_path),
            "runner_path": str(runner_path.relative_to(root)),
            "runner_sha256": digest_file(runner_path),
        },
        "outputs": {
            name: {"bytes": (out / name).stat().st_size, "sha256": digest_file(out / name)}
            for name in sorted(outputs)
        },
    }
    write_json(out / "RAW_MANIFEST_V1.json", raw_manifest)
    execution_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_main": BASE_MAIN,
        "subject_revision": SUBJECT_REVISION,
        "execution_head": execution_head,
        "freeze_sha256": digest_file(freeze_path),
        "raw_manifest_sha256": digest_file(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": len(rows),
        "pair_denominators": atlas["denominators"],
        "hard_preconditions": {
            "exact_subject_revision": True,
            "model_digest_bound": True,
            "runner_digest_bound": True,
            "complete_cartesian_class": len(rows) == 144,
            "violating_and_attaining_strata_present": (
                "ADMISSIBLE" in atlas["terminal_counts"]
                and "BLOCKED" in atlas["terminal_counts"]
                and "CANNOT_CHECK" in atlas["terminal_counts"]
            ),
        },
        "leakage": {
            "generator_label_input": False,
            "filename_input_to_policy": False,
            "post_outcome_retuning": False,
        },
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": terminal,
        "claim_ceiling": AUTHORITY_CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write_json(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(
        f"{JOB_ID}={terminal} cases={len(rows)} collisions={len(collisions)} "
        f"min_hamming={minimum_distance}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
