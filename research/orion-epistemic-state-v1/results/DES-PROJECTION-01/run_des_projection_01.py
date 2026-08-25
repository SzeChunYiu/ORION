"""Execute the prospectively frozen DES-PROJECTION-01 finite replay.

This computation is an internal finite-class replay. It does not edit paper
surfaces or grant scientific, novelty, publication, or external authority.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import fields
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[4]
MODEL_PATH = ROOT / "src" / "orion" / "epistemic_state_v1" / "model.py"
MODEL_SPEC = importlib.util.spec_from_file_location("orion_des_projection_frozen_model", MODEL_PATH)
if MODEL_SPEC is None or MODEL_SPEC.loader is None:
    raise RuntimeError(f"cannot load frozen reference model: {MODEL_PATH}")
MODEL = importlib.util.module_from_spec(MODEL_SPEC)
sys.modules[MODEL_SPEC.name] = MODEL
MODEL_SPEC.loader.exec_module(MODEL)

Action = MODEL.Action
Coordinate = MODEL.Coordinate
ResourceVector = MODEL.ResourceVector
State = MODEL.State
Status = MODEL.Status
SupportFamily = MODEL.SupportFamily
Terminal = MODEL.Terminal
promotion_policy = MODEL.promotion_policy


JOB_ID = "DES-PROJECTION-01"
BASE_SHA = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
FREEZE_COMMIT = "010a0986b5b96248f16a3b1c18cb48b0ba2259b6"
EXPECTED_PYTHON = "3.14.6"
EXPECTED_EXECUTABLE = "/opt/homebrew/opt/python@3.14/bin/python3.14"
EXPECTED_INPUTS = {
    "src/orion/epistemic_state_v1/model.py": (
        "679afd19e39445f7d4d496b2b56df73d908e57a6d8c0ae4ee4e1b86364940e5f"
    ),
    "research/orion-epistemic-state-v1/DYNAMIC_EPISTEMIC_STATE_CALCULUS_V1.md": (
        "2fc2d7ed8d5d415230fce48e7d2c4203f1bb09c79d16f9c934c54553ec9d4e05"
    ),
    "research/orion-epistemic-state-v1/COMPUTE_EXECUTION_BACKLOG_V1.json": (
        "dc41b2059ecb308c2e21d6fe60a616fbe5f3d7463ce2429f3545d8d3b0c13df4"
    ),
    "research/orion-epistemic-state-v1/AI_EXECUTOR_PROMPT_V1.md": (
        "7bfec2efb288225329c48c9bd1be096423e50fb4d4a059943272ca0ed7cbb2ce"
    ),
    "papers/P1_P15_TOP_TIER_DYNAMIC_STATE_PROGRAMME_V1.md": (
        "19a97b88c1ec49d014c6352ec8cd2ae4da0da57851f206589d36dfe9849175ce"
    ),
}
FACTOR_VALUES: tuple[tuple[str, tuple[Any, ...]], ...] = (
    ("responsibility_matches", (True, False)),
    ("identified", ("TRUE", "FALSE", "CANNOT_CHECK")),
    ("obligations_complete", (True, False)),
    ("support_complete", (True, False)),
    ("active_defeater", (False, True)),
    ("custody_external", (True, False, None)),
    ("authority_present", (True, False)),
    (
        "evidence_mode",
        ("KNOWN_TRUE", "KNOWN_FALSE", "PARTIAL", "CANNOT_CHECK", "REVOKED"),
    ),
    ("open_method_gap", (False, True)),
)
EXPECTED_STATE_CASES = 2880
EXPECTED_PROJECTION_ROWS = 5760
OUTPUT_CAP = 52_428_800
MEMORY_CAP_MIB = 512
WALL_CAP_SECONDS = 120


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def rendered_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def factor_cases() -> Iterable[tuple[str, dict[str, Any]]]:
    names = [name for name, _ in FACTOR_VALUES]
    products = itertools.product(*(values for _, values in FACTOR_VALUES))
    for ordinal, values in enumerate(products):
        yield f"DES-PROJECTION-01-CASE-{ordinal:04d}", dict(zip(names, values, strict=True))


def evidence_coordinate(mode: str) -> Coordinate:
    if mode == "KNOWN_TRUE":
        return Coordinate(
            True, Status.KNOWN, "paper:write", 1, ("P:evidence",), "des-projection:v1"
        )
    if mode == "KNOWN_FALSE":
        return Coordinate(
            False, Status.KNOWN, "paper:write", 1, ("P:evidence",), "des-projection:v1"
        )
    if mode == "PARTIAL":
        return Coordinate(
            None, Status.PARTIAL, "paper:write", 1, ("P:evidence",), "des-projection:v1"
        )
    if mode == "CANNOT_CHECK":
        return Coordinate(None, Status.CANNOT_CHECK, "paper:write", 1, (), "des-projection:v1")
    if mode == "REVOKED":
        return Coordinate(
            None, Status.REVOKED, "paper:write", 1, ("P:revoked",), "des-projection:v1"
        )
    raise ValueError(mode)


def identified_coordinate(mode: str) -> Coordinate:
    if mode == "TRUE":
        return Coordinate(
            True, Status.KNOWN, "paper:write", 1, ("P:identified",), "des-projection:v1"
        )
    if mode == "FALSE":
        return Coordinate(
            False, Status.KNOWN, "paper:write", 1, ("P:identified",), "des-projection:v1"
        )
    if mode == "CANNOT_CHECK":
        return Coordinate(None, Status.CANNOT_CHECK, "paper:write", 1, (), "des-projection:v1")
    raise ValueError(mode)


def make_state(factors_map: dict[str, Any]) -> State:
    required = frozenset({"O:claim-support"})
    satisfied = required if factors_map["obligations_complete"] else frozenset()
    support_obligations = required if factors_map["support_complete"] else frozenset({"O:other"})
    support = (
        SupportFamily(
            "SF:complete" if factors_map["support_complete"] else "SF:incomplete",
            frozenset({"P:support"}),
            support_obligations,
        ),
    )
    return State(
        subject_id="DES-PROJECTION-01-SUBJECT",
        responsibility_id=(
            "paper:write" if factors_map["responsibility_matches"] else "paper:other"
        ),
        epoch=1,
        evidence=evidence_coordinate(factors_map["evidence_mode"]),
        identifiability=identified_coordinate(factors_map["identified"]),
        coverage=Coordinate(
            {"lower": "1", "upper": "1", "open_world_residual": False},
            Status.KNOWN,
            "paper:write",
            1,
            ("P:coverage",),
            "des-projection:v1",
        ),
        obligations_required=required,
        obligations_satisfied=satisfied,
        provenance=Coordinate(
            {"bound": True},
            Status.KNOWN,
            "paper:write",
            1,
            ("P:provenance",),
            "des-projection:v1",
        ),
        verification=Coordinate(
            {"internal_replay": True, "external_independence": False},
            Status.KNOWN,
            "paper:write",
            1,
            ("P:verification",),
            "des-projection:v1",
        ),
        authority_scopes=(
            frozenset({"paper:write"}) if factors_map["authority_present"] else frozenset()
        ),
        support_families=support,
        active_defeaters=(
            frozenset({"D:active"}) if factors_map["active_defeater"] else frozenset()
        ),
        custody_external=factors_map["custody_external"],
        method_reach_ids=(
            frozenset({"M:open-local-gap"}) if factors_map["open_method_gap"] else frozenset()
        ),
        knowledge_node_ids=frozenset({"K:subject"}),
        knowledge_edge_ids=frozenset({"G:supports"}),
        resources=ResourceVector(
            acquisition=Fraction(1),
            state=Fraction(1),
            reasoning=Fraction(1),
            verification=Fraction(1),
            recovery=Fraction(1),
            latency=Fraction(1),
        ),
    )


def oracle_promotion(factors_map: dict[str, Any]) -> Terminal:
    if not factors_map["responsibility_matches"]:
        return Terminal.CANNOT_CHECK
    unknown = False
    identified = factors_map["identified"]
    if identified == "CANNOT_CHECK":
        unknown = True
    elif identified == "FALSE":
        return Terminal.BLOCKED
    if not factors_map["obligations_complete"]:
        return Terminal.BLOCKED
    if not factors_map["support_complete"]:
        return Terminal.BLOCKED
    if factors_map["active_defeater"]:
        return Terminal.BLOCKED
    custody = factors_map["custody_external"]
    if custody is None:
        unknown = True
    elif custody is False:
        return Terminal.CANNOT_CHECK
    if not factors_map["authority_present"]:
        return Terminal.BLOCKED
    return Terminal.CANNOT_CHECK if unknown else Terminal.ADMISSIBLE


def readiness_projection(promotion: Terminal, evidence_mode: str) -> Terminal:
    if promotion is not Terminal.ADMISSIBLE:
        return promotion
    if evidence_mode == "KNOWN_TRUE":
        return Terminal.ADMISSIBLE
    if evidence_mode == "PARTIAL":
        return Terminal.PROVISIONAL
    if evidence_mode == "CANNOT_CHECK":
        return Terminal.CANNOT_CHECK
    if evidence_mode in {"KNOWN_FALSE", "REVOKED"}:
        return Terminal.BLOCKED
    raise ValueError(evidence_mode)


def oracle_readiness(factors_map: dict[str, Any]) -> Terminal:
    promotion = oracle_promotion(factors_map)
    if promotion is not Terminal.ADMISSIBLE:
        return promotion
    return {
        "KNOWN_TRUE": Terminal.ADMISSIBLE,
        "PARTIAL": Terminal.PROVISIONAL,
        "CANNOT_CHECK": Terminal.CANNOT_CHECK,
        "KNOWN_FALSE": Terminal.BLOCKED,
        "REVOKED": Terminal.BLOCKED,
    }[factors_map["evidence_mode"]]


def next_action(factors_map: dict[str, Any]) -> Action:
    if not factors_map["responsibility_matches"]:
        return Action.REVALIDATE
    if factors_map["identified"] in {"FALSE", "CANNOT_CHECK"}:
        return Action.DISCRIMINATE
    if not factors_map["obligations_complete"]:
        return Action.ACQUIRE_EVIDENCE
    if not factors_map["support_complete"]:
        return Action.ACQUIRE_EVIDENCE
    if factors_map["active_defeater"]:
        return Action.DISCRIMINATE
    if factors_map["custody_external"] is not True:
        return Action.OBTAIN_EXTERNAL_CUSTODY
    if not factors_map["authority_present"]:
        return Action.REVALIDATE
    if factors_map["evidence_mode"] in {"CANNOT_CHECK", "PARTIAL", "KNOWN_FALSE"}:
        return Action.ACQUIRE_EVIDENCE
    if factors_map["evidence_mode"] == "REVOKED":
        return Action.REVALIDATE
    if factors_map["open_method_gap"]:
        return Action.SEARCH_LOCAL
    return Action.STOP


def coordinate_json(value: Coordinate) -> dict[str, Any]:
    return {
        "value": value.value,
        "status": value.status.value,
        "scope": value.scope,
        "epoch": value.epoch,
        "provenance_ids": list(value.provenance_ids),
        "estimator_version": value.estimator_version,
    }


def state_json(state: State) -> dict[str, Any]:
    return {
        "subject_id": state.subject_id,
        "responsibility_id": state.responsibility_id,
        "epoch": state.epoch,
        "evidence": coordinate_json(state.evidence),
        "identifiability": coordinate_json(state.identifiability),
        "coverage": coordinate_json(state.coverage),
        "obligations_required": sorted(state.obligations_required),
        "obligations_satisfied": sorted(state.obligations_satisfied),
        "provenance": coordinate_json(state.provenance),
        "verification": coordinate_json(state.verification),
        "authority_scopes": sorted(state.authority_scopes),
        "support_families": [
            {
                "family_id": item.family_id,
                "premise_ids": sorted(item.premise_ids),
                "obligation_ids": sorted(item.obligation_ids),
            }
            for item in state.support_families
        ],
        "active_defeaters": sorted(state.active_defeaters),
        "custody_external": state.custody_external,
        "method_reach_ids": sorted(state.method_reach_ids),
        "knowledge_node_ids": sorted(state.knowledge_node_ids),
        "knowledge_edge_ids": sorted(state.knowledge_edge_ids),
        "resources": {
            name: str(getattr(state.resources, name))
            for name in (
                "acquisition",
                "state",
                "reasoning",
                "verification",
                "recovery",
                "latency",
            )
        },
        "revoked_premise_ids": sorted(state.revoked_premise_ids),
        "applied_event_ids": sorted(state.applied_event_ids),
    }


def unresolved_semantics(state: State, factors_map: dict[str, Any]) -> dict[str, Any]:
    unknown = []
    if factors_map["identified"] == "CANNOT_CHECK":
        unknown.append("identifiability")
    if factors_map["custody_external"] is None:
        unknown.append("custody_external")
    if factors_map["evidence_mode"] == "CANNOT_CHECK":
        unknown.append("evidence")
    return {
        "unresolved_obligation_ids": sorted(state.unresolved),
        "active_defeater_ids": sorted(state.active_defeaters),
        "unknown_coordinates": unknown,
        "open_method_gap": factors_map["open_method_gap"],
    }


def evaluate_case(case_id: str, factors_map: dict[str, Any]) -> dict[str, Any]:
    policy = promotion_policy("paper:write")
    state = make_state(factors_map)
    promotion = policy.project(state)
    promotion_oracle = oracle_promotion(factors_map)
    readiness = readiness_projection(promotion, factors_map["evidence_mode"])
    readiness_oracle = oracle_readiness(factors_map)
    return {
        "case_id": case_id,
        "factors": factors_map,
        "state": state_json(state),
        "unresolved_semantics": unresolved_semantics(state, factors_map),
        "next_action": next_action(factors_map).value,
        "projections": {
            "PROMOTION_V1": {
                "reference": promotion.value,
                "oracle": promotion_oracle.value,
                "match": promotion is promotion_oracle,
            },
            "READINESS_V1": {
                "reference": readiness.value,
                "oracle": readiness_oracle.value,
                "match": readiness is readiness_oracle,
            },
        },
        "execution_status": "COMPLETE",
        "exception": None,
    }


def retained_exception_case(
    case_id: str, factors_map: dict[str, Any], error: Exception
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "factors": factors_map,
        "state": None,
        "unresolved_semantics": {
            "unresolved_obligation_ids": (
                [] if factors_map["obligations_complete"] else ["O:claim-support"]
            ),
            "active_defeater_ids": (["D:active"] if factors_map["active_defeater"] else []),
            "unknown_coordinates": [],
            "open_method_gap": factors_map["open_method_gap"],
            "status": "CANNOT_CHECK__STATE_EXECUTION_EXCEPTION",
        },
        "next_action": None,
        "projections": {
            surface: {
                "reference": None,
                "oracle": oracle(factors_map).value,
                "match": False,
            }
            for surface, oracle in (
                ("PROMOTION_V1", oracle_promotion),
                ("READINESS_V1", oracle_readiness),
            )
        },
        "execution_status": "CANNOT_CHECK",
        "exception": {"type": type(error).__name__, "message": str(error)},
    }


def execute_cases(
    cases: Iterable[tuple[str, dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for case_id, factors_map in factor_cases() if cases is None else cases:
        try:
            rows.append(evaluate_case(case_id, factors_map))
        except Exception as error:  # retain prospectively frozen adverse rows
            rows.append(retained_exception_case(case_id, factors_map, error))
    return rows


def hamming(left: dict[str, Any], right: dict[str, Any]) -> int:
    return sum(left[name] != right[name] for name, _ in FACTOR_VALUES)


def witness_pair(
    rows: list[dict[str, Any]], *, require_action_divergence: bool
) -> tuple[dict[str, Any], dict[str, Any], int] | None:
    best = None
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if require_action_divergence and left["next_action"] == right["next_action"]:
                continue
            distance = hamming(left["factors"], right["factors"])
            candidate = (distance, left["case_id"], right["case_id"], left, right)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
                if distance == 1:
                    break
        if best is not None and best[0] == 1:
            break
    if best is None:
        return None
    return best[3], best[4], best[0]


def build_witnesses(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for surface in ("PROMOTION_V1", "READINESS_V1"):
            reference = row["projections"][surface]["reference"]
            if reference is not None:
                groups[(surface, reference)].append(row)
    witnesses = []
    for surface, terminal in sorted(groups):
        group = groups[(surface, terminal)]
        minimal = witness_pair(group, require_action_divergence=False)
        divergent = witness_pair(group, require_action_divergence=True)
        if minimal is None:
            minimal_payload = None
        else:
            left, right, distance = minimal
            minimal_payload = {
                "left_case_id": left["case_id"],
                "right_case_id": right["case_id"],
                "hamming_distance": distance,
                "left_factors": left["factors"],
                "right_factors": right["factors"],
                "left_next_action": left["next_action"],
                "right_next_action": right["next_action"],
            }
        if divergent is None:
            divergent_payload: dict[str, Any] = {
                "status": "CANNOT_CHECK__NO_ACTION_DIVERGENT_PAIR_IN_GROUP"
            }
        else:
            left, right, distance = divergent
            divergent_payload = {
                "status": "FOUND",
                "left_case_id": left["case_id"],
                "right_case_id": right["case_id"],
                "hamming_distance": distance,
                "left_factors": left["factors"],
                "right_factors": right["factors"],
                "left_next_action": left["next_action"],
                "right_next_action": right["next_action"],
            }
        witnesses.append(
            {
                "surface_id": surface,
                "terminal": terminal,
                "preimage_size": len(group),
                "noninjective": len(group) > 1,
                "minimal_state_distinct_pair": minimal_payload,
                "minimal_action_divergent_pair": divergent_payload,
                "inverse_status": "SET_VALUED__NO_FAITHFUL_SINGLE_STATE_INVERSE",
            }
        )
    return {
        "schema": "orion.dynamic-epistemic-state.nonreconstruction-witnesses.v1",
        "job_id": JOB_ID,
        "group_count": len(witnesses),
        "all_reachable_groups_noninjective": all(item["noninjective"] for item in witnesses),
        "groups_with_action_divergence": sum(
            item["minimal_action_divergent_pair"]["status"] == "FOUND" for item in witnesses
        ),
        "witnesses": witnesses,
        "interpretation": "Every reachable legacy label has multiple full-state preimages. A terminal therefore cannot reconstruct the state that produced it; action-divergent witnesses additionally show where retaining the state changes the next move.",
        "authority": "FINITE_REFERENCE_CLASS_INTERNAL_REPLAY_ONLY",
    }


def preconditions(output_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for relative, expected in EXPECTED_INPUTS.items():
        actual = digest_file(ROOT / relative)
        checks.append(
            {
                "id": f"input_sha256:{relative}",
                "passed": actual == expected,
                "expected": expected,
                "actual": actual,
            }
        )
    current = git("rev-parse", "HEAD")
    freeze_parent = git("rev-parse", f"{FREEZE_COMMIT}^")
    checks.extend(
        [
            {
                "id": "base_subject_is_freeze_parent",
                "passed": freeze_parent == BASE_SHA,
                "expected": BASE_SHA,
                "actual": freeze_parent,
            },
            {
                "id": "freeze_commit_is_ancestor_of_execution_head",
                "passed": subprocess.run(
                    ["git", "merge-base", "--is-ancestor", FREEZE_COMMIT, current],
                    cwd=ROOT,
                    check=False,
                ).returncode
                == 0,
                "freeze_commit": FREEZE_COMMIT,
                "execution_head": current,
            },
            {
                "id": "python_version",
                "passed": platform.python_version() == EXPECTED_PYTHON,
                "expected": EXPECTED_PYTHON,
                "actual": platform.python_version(),
            },
            {
                "id": "python_executable",
                "passed": sys.executable == EXPECTED_EXECUTABLE,
                "expected": EXPECTED_EXECUTABLE,
                "actual": sys.executable,
            },
            {
                "id": "factor_denominator",
                "passed": (
                    len(list(factor_cases())) == EXPECTED_STATE_CASES
                    and EXPECTED_STATE_CASES * 2 == EXPECTED_PROJECTION_ROWS
                ),
                "expected_state_cases": EXPECTED_STATE_CASES,
                "expected_projection_rows": EXPECTED_PROJECTION_ROWS,
            },
            {
                "id": "reference_state_field_count",
                "passed": len(fields(State)) == 20,
                "expected": 20,
                "actual": len(fields(State)),
            },
            {
                "id": "no_preexisting_outcome_consumed",
                "passed": not any(
                    (output_dir / name).exists()
                    for name in (
                        "RAW_MANIFEST_V1.json",
                        "PRIMARY_RESULT_V1.json",
                        "IDEAL_DONOR_RESULT_V1.json",
                        "NEGATIVE_CONTROLS_V1.json",
                        "RESOURCE_LEDGER_V1.json",
                        "TRANSFER_RESULT_V1.json",
                        "LEGACY_PROJECTION_CORRESPONDENCE_V1.json",
                        "NONRECONSTRUCTION_WITNESSES_V1.json",
                        "RESULT_BINDING_PACKET_V1.json",
                    )
                ),
            },
        ]
    )
    return checks


def decision_map(rows: Iterable[dict[str, Any]]) -> dict[str, tuple[Any, Any, Any]]:
    return {
        row["case_id"]: (
            row["projections"]["PROMOTION_V1"]["reference"],
            row["projections"]["READINESS_V1"]["reference"],
            row["next_action"],
        )
        for row in rows
    }


def decision_sequence(rows: Iterable[dict[str, Any]]) -> list[tuple[Any, Any, Any]]:
    return [
        (
            row["projections"]["PROMOTION_V1"]["reference"],
            row["projections"]["READINESS_V1"]["reference"],
            row["next_action"],
        )
        for row in rows
    ]


def build_negative_controls(
    rows: list[dict[str, Any]], witnesses: dict[str, Any]
) -> dict[str, Any]:
    original = decision_map(rows)
    case_inputs = [(row["case_id"], row["factors"]) for row in rows]
    reversed_map = decision_map(execute_cases(reversed(case_inputs)))
    renamed_rows = execute_cases(
        (
            f"renamed-{index:04d}",
            row["factors"],
        )
        for index, row in enumerate(rows)
    )
    aliases = {name: f"F{index}" for index, (name, _) in enumerate(FACTOR_VALUES)}
    decoded_rows = []
    for row in rows:
        aliased = {aliases[key]: value for key, value in row["factors"].items()}
        decoded = {
            name: {aliases[key]: value for key, value in row["factors"].items()}[aliases[name]]
            for name, _ in FACTOR_VALUES
        }
        assert aliased == {aliases[key]: value for key, value in decoded.items()}
        decoded_rows.extend(execute_cases([(row["case_id"], decoded)]))
    case_order_passed = original == reversed_map
    case_id_passed = decision_sequence(rows) == decision_sequence(renamed_rows)
    alias_round_trip = original == decision_map(decoded_rows)
    controls = [
        {
            "control_id": "CASE_ORDER_REVERSAL",
            "passed": case_order_passed,
            "reading": "case order does not alter case-ID keyed decisions",
        },
        {
            "control_id": "CASE_ID_RENAMING",
            "passed": case_id_passed,
            "reading": "projection values are unchanged when identity labels are replaced",
        },
        {
            "control_id": "FACTOR_LABEL_ALIAS_ROUND_TRIP",
            "passed": alias_round_trip,
            "reading": "factor names carry no outcome shortcut after frozen inverse decoding",
        },
        {
            "control_id": "LABEL_ONLY_SINGLE_STATE_INVERSE",
            "passed": witnesses["all_reachable_groups_noninjective"],
            "reading": "the negative control fails to reconstruct a unique state for every reachable label, as required by DES-T1",
        },
    ]
    return {
        "schema": "orion.dynamic-epistemic-state.des-projection-negative-controls.v1",
        "job_id": JOB_ID,
        "controls": controls,
        "all_passed": all(item["passed"] for item in controls),
        "leakage_detected": not (case_order_passed and case_id_passed and alias_round_trip),
        "filename_or_case_id_used_by_projection": not case_id_passed,
    }


def serialized_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def artifact_record(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": serialized_path(path),
        "sha256": digest_bytes(payload),
        "bytes": len(payload),
    }


def resident_memory_mib(raw: int | float, *, system: str | None = None) -> float:
    system = platform.system() if system is None else system
    divisor = 1024 * 1024 if system == "Darwin" else 1024
    return float(raw) / divisor


def write_json(path: Path, value: object) -> None:
    payload = rendered_bytes(value)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def run(output_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    checks = preconditions(output_dir)
    if not all(item["passed"] for item in checks):
        raise RuntimeError(
            f"hard precondition failed: {[item for item in checks if not item['passed']]}"
        )

    rows = execute_cases()
    retained_exceptions = [
        {"case_id": row["case_id"], **row["exception"]}
        for row in rows
        if row["exception"] is not None
    ]
    raw = {
        "schema": "orion.dynamic-epistemic-state.des-projection-raw-manifest.v1",
        "job_id": JOB_ID,
        "case_denominator": len(rows),
        "projection_denominator": len(rows) * 2,
        "factor_order": [name for name, _ in FACTOR_VALUES],
        "case_outcomes": rows,
        "dropped_cases": [],
        "exceptions": retained_exceptions,
        "authority": "INTERNAL_FINITE_REFERENCE_REPLAY",
    }
    raw_bytes = rendered_bytes(raw)
    raw_digest = digest_bytes(raw_bytes)

    surface_counts: dict[str, Counter[str]] = {
        "PROMOTION_V1": Counter(),
        "READINESS_V1": Counter(),
    }
    mismatches = []
    semantics_retained = True
    for row in rows:
        for surface in surface_counts:
            result = row["projections"][surface]
            if result["reference"] is not None:
                surface_counts[surface][result["reference"]] += 1
            if not result["match"]:
                mismatches.append(
                    {
                        "case_id": row["case_id"],
                        "surface_id": surface,
                        "reference": result["reference"],
                        "oracle": result["oracle"],
                    }
                )
        semantics = row["unresolved_semantics"]
        factors_map = row["factors"]
        expected_unknown = []
        if factors_map["identified"] == "CANNOT_CHECK":
            expected_unknown.append("identifiability")
        if factors_map["custody_external"] is None:
            expected_unknown.append("custody_external")
        if factors_map["evidence_mode"] == "CANNOT_CHECK":
            expected_unknown.append("evidence")
        semantics_retained &= bool(semantics["unresolved_obligation_ids"]) == (
            not factors_map["obligations_complete"]
        )
        semantics_retained &= (
            bool(semantics["active_defeater_ids"]) == factors_map["active_defeater"]
        )
        semantics_retained &= semantics["unknown_coordinates"] == expected_unknown
        semantics_retained &= semantics["open_method_gap"] == factors_map["open_method_gap"]

    correspondence = {
        "schema": "orion.dynamic-epistemic-state.legacy-projection-correspondence.v1",
        "job_id": JOB_ID,
        "source_raw_manifest_sha256": raw_digest,
        "state_case_denominator": len(rows),
        "projection_row_denominator": len(rows) * 2,
        "matched_projection_rows": len(rows) * 2 - len(mismatches),
        "mismatches": mismatches,
        "surface_results": {
            surface: {
                "terminal_counts": dict(sorted(counts.items())),
                "reachable_terminals": sorted(counts),
            }
            for surface, counts in surface_counts.items()
        },
        "declared_unreachable": {"PROMOTION_V1": ["PROVISIONAL"], "READINESS_V1": []},
        "unresolved_semantics_retained": semantics_retained,
        "dropped_cases": 0,
        "terminal": "LEGACY_PROJECTION_REPLAY_EXACT"
        if not mismatches
        else "LEGACY_PROJECTION_MISMATCH",
        "authority": "INTERNAL_REPLAY_NOT_EXTERNAL_INDEPENDENCE",
    }
    witnesses = build_witnesses(rows)
    controls = build_negative_controls(rows, witnesses)

    observed_sets = {surface: set(counts) for surface, counts in surface_counts.items()}
    expected_sets = {
        "PROMOTION_V1": {"ADMISSIBLE", "BLOCKED", "CANNOT_CHECK"},
        "READINESS_V1": {"ADMISSIBLE", "PROVISIONAL", "BLOCKED", "CANNOT_CHECK"},
    }
    gates = {
        "hard_preconditions": all(item["passed"] for item in checks),
        "state_denominator_2880": len(rows) == EXPECTED_STATE_CASES,
        "projection_denominator_5760": len(rows) * 2 == EXPECTED_PROJECTION_ROWS,
        "all_rows_retained": all(row["execution_status"] == "COMPLETE" for row in rows),
        "promotion_reference_matches_oracle": not any(
            item["surface_id"] == "PROMOTION_V1" for item in mismatches
        ),
        "readiness_reference_matches_oracle": not any(
            item["surface_id"] == "READINESS_V1" for item in mismatches
        ),
        "reachable_terminal_sets_exact": observed_sets == expected_sets,
        "seven_reachable_groups_noninjective": (
            witnesses["group_count"] == 7 and witnesses["all_reachable_groups_noninjective"]
        ),
        "unresolved_semantics_retained": semantics_retained,
        "leakage_controls": controls["all_passed"],
    }
    core_outputs = {
        "RAW_MANIFEST_V1.json": raw,
        "LEGACY_PROJECTION_CORRESPONDENCE_V1.json": correspondence,
        "NONRECONSTRUCTION_WITNESSES_V1.json": witnesses,
        "NEGATIVE_CONTROLS_V1.json": controls,
    }
    projected_bytes = sum(len(rendered_bytes(value)) for value in core_outputs.values())
    usage = resource.getrusage(resource.RUSAGE_SELF)
    maximum_resident_mib = resident_memory_mib(usage.ru_maxrss)
    resource_censored = (
        projected_bytes > OUTPUT_CAP
        or (time.monotonic() - started) > WALL_CAP_SECONDS
        or maximum_resident_mib > MEMORY_CAP_MIB
    )
    gates["resource_caps_not_binding"] = not resource_censored
    positive = all(gates.values())
    terminal = (
        "LEGACY_DECISIONS_REPRODUCED_AND_COLLISIONS_RESOLVED"
        if positive
        else (
            "CANNOT_CHECK__RESOURCE_CENSORED"
            if resource_censored
            else (
                "CANNOT_CHECK__EXECUTION_EXCEPTION_RETAINED"
                if retained_exceptions
                else "LEGACY_DECISION_REPLAY_MISMATCH_OR_RECONSTRUCTION_COUNTEREXAMPLE"
            )
        )
    )

    donor = {
        "schema": "orion.dynamic-epistemic-state.des-projection-ideal-donor.v1",
        "job_id": JOB_ID,
        "strongest_donor": "FROZEN_REFERENCE_PROMOTION_POLICY_PLUS_EXPLICIT_READINESS_RULE",
        "matched_access": True,
        "matched_resource_vector": True,
        "result": "EXACT_REFERENCE_REPLAY",
        "donor_superiority_comparison": "NOT_APPLICABLE__FORMAL_CORRESPONDENCE_JOB",
        "orion_superiority": "CANNOT_CHECK",
        "authority": "NO_DONOR_OR_EMPIRICAL_SUPERIORITY_CLAIM",
    }
    transfer = {
        "schema": "orion.dynamic-epistemic-state.des-projection-transfer.v1",
        "job_id": JOB_ID,
        "status": "CANNOT_CHECK__NO_EXTERNAL_TRANSFER_POPULATION_FROZEN",
        "external_cases": 0,
        "internal_finite_class_exhaustive": True,
        "internal_case_denominator": len(rows),
        "claim_ceiling": "NO_EXTERNAL_TRANSFER_OR_GENERALIZATION",
    }
    primary = {
        "schema": "orion.dynamic-epistemic-state.des-projection-primary-result.v1",
        "job_id": JOB_ID,
        "terminal": terminal,
        "gates": gates,
        "state_case_denominator": len(rows),
        "projection_row_denominator": len(rows) * 2,
        "matched_projection_rows": len(rows) * 2 - len(mismatches),
        "reachable_noninjective_groups": witnesses["group_count"],
        "groups_with_action_divergence": witnesses["groups_with_action_divergence"],
        "unresolved_cases_retained": sum(
            bool(row["unresolved_semantics"]["unresolved_obligation_ids"])
            or bool(row["unresolved_semantics"]["active_defeater_ids"])
            or bool(row["unresolved_semantics"]["unknown_coordinates"])
            or row["unresolved_semantics"]["open_method_gap"]
            for row in rows
        ),
        "dropped_cases": 0,
        "claim_ceiling": "FINITE_REFERENCE_CLASS_INTERNAL_REPLAY_ONLY__NO_EMPIRICAL_SUPERIORITY__NO_EXTERNAL_INDEPENDENCE",
        "paper_authority_delta": "NONE",
    }
    core_outputs.update(
        {
            "IDEAL_DONOR_RESULT_V1.json": donor,
            "TRANSFER_RESULT_V1.json": transfer,
            "PRIMARY_RESULT_V1.json": primary,
        }
    )

    for name, value in core_outputs.items():
        write_json(output_dir / name, value)

    elapsed = time.monotonic() - started
    bound_before_resource = [artifact_record(output_dir / name) for name in sorted(core_outputs)]
    resource_ledger = {
        "schema": "orion.dynamic-epistemic-state.des-projection-resource-ledger.v1",
        "job_id": JOB_ID,
        "frozen_vector": {
            "cpu_processes": 1,
            "threads": 1,
            "gpu_count": 0,
            "network_access": False,
            "external_api_calls": 0,
            "money_usd": 0,
            "wall_seconds_cap": WALL_CAP_SECONDS,
            "resident_memory_mib_cap": MEMORY_CAP_MIB,
            "disk_output_bytes_cap": OUTPUT_CAP,
        },
        "observed": {
            "wall_seconds": round(elapsed, 6),
            "user_cpu_seconds": round(usage.ru_utime, 6),
            "system_cpu_seconds": round(usage.ru_stime, 6),
            "maximum_resident_memory_raw_platform_units": usage.ru_maxrss,
            "maximum_resident_memory_mib": round(maximum_resident_mib, 6),
            "bound_artifact_bytes_excluding_resource_and_binding": sum(
                item["bytes"] for item in bound_before_resource
            ),
        },
        "censored": resource_censored,
        "cap_binding": (
            []
            if not resource_censored
            else [
                name
                for name, bound in (
                    ("wall_seconds_cap", elapsed > WALL_CAP_SECONDS),
                    ("disk_output_bytes_cap", projected_bytes > OUTPUT_CAP),
                    (
                        "resident_memory_mib_cap",
                        maximum_resident_mib > MEMORY_CAP_MIB,
                    ),
                )
                if bound
            ]
        ),
    }
    write_json(output_dir / "RESOURCE_LEDGER_V1.json", resource_ledger)

    freeze_path = output_dir / "FREEZE_V1.json"
    if not freeze_path.exists():
        freeze_path = Path(__file__).with_name("FREEZE_V1.json")
    artifacts = [artifact_record(output_dir / name) for name in sorted(core_outputs)]
    artifacts.append(artifact_record(output_dir / "RESOURCE_LEDGER_V1.json"))
    binding = {
        "schema": "orion.dynamic-epistemic-state.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_subject_sha": BASE_SHA,
        "freeze_commit_sha": FREEZE_COMMIT,
        "execution_head_sha": git("rev-parse", "HEAD"),
        "freeze": {
            "path": serialized_path(freeze_path),
            "sha256": digest_file(freeze_path),
            "bytes": freeze_path.stat().st_size,
        },
        "execution_code": artifact_record(Path(__file__)),
        "frozen_inputs": [
            {
                "path": relative,
                "sha256": digest_file(ROOT / relative),
                "bytes": (ROOT / relative).stat().st_size,
            }
            for relative in EXPECTED_INPUTS
        ],
        "artifacts": artifacts,
        "case_level_outcomes": {
            "path": artifact_record(output_dir / "RAW_MANIFEST_V1.json")["path"],
            "sha256": artifact_record(output_dir / "RAW_MANIFEST_V1.json")["sha256"],
            "state_case_denominator": len(rows),
            "projection_row_denominator": len(rows) * 2,
            "dropped_cases": 0,
            "exceptions": len(retained_exceptions),
        },
        "hard_preconditions": checks,
        "leakage_and_negative_controls": {
            "path": artifact_record(output_dir / "NEGATIVE_CONTROLS_V1.json")["path"],
            "sha256": artifact_record(output_dir / "NEGATIVE_CONTROLS_V1.json")["sha256"],
            "all_passed": controls["all_passed"],
        },
        "censoring": {
            "resource_censored": resource_censored,
            "partial_rows_authorize_positive": False,
        },
        "strongest_donor": donor["strongest_donor"],
        "resource_vector": resource_ledger,
        "transfer": transfer,
        "terminal": terminal,
        "claim_ceiling": primary["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "handoff": [
            "MANUSCRIPT_WRITING_OWNER = P1_P15_REWRITE_LANE",
            "COMPUTATION_SESSION_PAPER_AUTHORITY_DELTA = NONE",
        ],
    }
    write_json(output_dir / "RESULT_BINDING_PACKET_V1.json", binding)
    final_bytes = sum(path.stat().st_size for path in output_dir.glob("*.json"))
    if final_bytes > OUTPUT_CAP:
        raise RuntimeError(f"final output cap exceeded: {final_bytes} > {OUTPUT_CAP}")
    return primary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    args = parser.parse_args(argv)
    result = run(args.output_dir.resolve())
    print(
        f"{result['terminal']} state_cases={result['state_case_denominator']} "
        f"projection_rows={result['projection_row_denominator']} "
        f"noninjective_groups={result['reachable_noninjective_groups']}"
    )
    return 0 if result["terminal"] == "LEGACY_DECISIONS_REPRODUCED_AND_COLLISIONS_RESOLVED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
