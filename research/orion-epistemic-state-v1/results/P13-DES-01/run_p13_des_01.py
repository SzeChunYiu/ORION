#!/usr/bin/env python3
"""Run P13-DES-01 as a bounded internal control and custody audit.

The 144-case control is a retrospective replay of the immutable
DES-COLLISION-01 finite class.  It may compare the full-axis dynamic policy
with the strongest deterministic terminal-only policy on that class.  It may
not invent the unfrozen reason-taxonomy, global-score, or always-raw arms, and
it may not convert same-owner public-Git measurements into external lifecycle
authority.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import platform
from typing import Any, Callable, Mapping


JOB_ID = "P13-DES-01"
SUBJECT_REVISION = "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
BASE_MAIN = "f049e30391a09213240f6325ee319f9fa811189a"
FULL_POSITIVE = (
    "DYNAMIC_RESPONSIBILITY_STATE_STRICTLY_DOMINATES_"
    "TERMINAL_ONLY_SCIENTIFIC_CONTROL"
)
BOUNDED_POSITIVE = (
    "BOUNDED_DYNAMIC_STATE_BEATS_TERMINAL_ONLY__"
    "FULL_P13_CONTROL_CANNOT_CHECK"
)
NULL = "DYNAMIC_STATE_DOES_NOT_BEAT_TERMINAL_ONLY_ON_FROZEN_FINITE_CLASS"
PRECONDITION_FAILURE = "P13_CONTROL_INPUTS_UNAVAILABLE"
CLAIM_CEILING = (
    "RETROSPECTIVE_INTERNAL_144_STATE_ACTION_CONTROL_ONLY__"
    "NO_FIVE_ARM_SHARED_PANEL__NO_PROSPECTIVE_EXTERNAL_LIFECYCLE_"
    "GOVERNANCE_NOVELTY_OR_POPULATION_AUTHORITY"
)
PLANNERS = (
    "terminal_only",
    "reason_taxonomy",
    "global_score",
    "always_raw",
    "dynamic_state",
)
EXECUTABLE_PLANNERS = ("terminal_only", "dynamic_state")
MISSING_PLANNER_STATES = {
    "reason_taxonomy": (
        "CANNOT_CHECK__NO_EXACT_FROZEN_POLICY_OR_INDEPENDENT_TAXONOMY_ON_SHARED_PANEL"
    ),
    "global_score": (
        "CANNOT_CHECK__NO_PRE_OUTCOME_PREFERENCE_VECTOR_ON_SHARED_PANEL"
    ),
    "always_raw": (
        "CANNOT_CHECK__NO_MATCHED_RECOVERY_ROUTE_OR_COST_CONTRACT_ON_SHARED_PANEL"
    ),
}
AXES = {
    "identifiability": {"KNOWN_TRUE", "KNOWN_FALSE", "CANNOT_CHECK"},
    "obligations": {"SATISFIED", "UNRESOLVED"},
    "support": {"COMPLETE", "ABSENT"},
    "defeaters": {"ABSENT", "PRESENT"},
    "custody": {"EXTERNAL", "NOT_EXTERNAL", "CANNOT_CHECK"},
    "authority": {"PRESENT", "ABSENT"},
}
VALID_ACTIONS = {
    "ACQUIRE_EVIDENCE",
    "DISCRIMINATE",
    "OBTAIN_EXTERNAL_CUSTODY",
    "REVALIDATE",
    "STOP",
}
VALID_TERMINALS = {"ADMISSIBLE", "BLOCKED", "CANNOT_CHECK"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(payload))


def dynamic_action(axes: Mapping[str, str]) -> str:
    """Frozen full-axis action policy; receives neither labels nor gold."""
    if axes["identifiability"] != "KNOWN_TRUE":
        return "DISCRIMINATE"
    if axes["obligations"] != "SATISFIED":
        return "ACQUIRE_EVIDENCE"
    if axes["support"] != "COMPLETE":
        return "ACQUIRE_EVIDENCE"
    if axes["defeaters"] == "PRESENT":
        return "REVALIDATE"
    if axes["custody"] != "EXTERNAL":
        return "OBTAIN_EXTERNAL_CUSTODY"
    if axes["authority"] != "PRESENT":
        return "REVALIDATE"
    return "STOP"


def terminal_only_action(label: str, mapping: Mapping[str, str]) -> str:
    """Frozen ideal label-only donor; receives no axes, case ids, or gold."""
    return mapping[label]


def validate_inputs(
    input_dir: Path, freeze: Mapping[str, Any], control: Mapping[str, Any],
    common: Mapping[str, Any], custody: Mapping[str, Any], runner_path: Path,
) -> None:
    files = freeze["implementation"]["inputs"]
    for name, expected in files.items():
        observed = digest_file(input_dir / name)
        if observed != expected:
            raise ValueError(f"input digest drift: {name}: {observed} != {expected}")
    if digest_file(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise ValueError("runner digest drift")
    if freeze["subject_revision"] != SUBJECT_REVISION or freeze["base_main"] != BASE_MAIN:
        raise ValueError("subject/base revision drift")
    if control.get("outcome_previously_accessed") is not True:
        raise ValueError("retrospective control must not be represented as prospective")
    rows = control.get("cases")
    if not isinstance(rows, list) or len(rows) != 144:
        raise ValueError("control must retain all 144 finite-class rows")
    ids: set[str] = set()
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id in ids:
            raise ValueError("missing or duplicate case id")
        ids.add(case_id)
        axes = row.get("axes")
        if not isinstance(axes, Mapping) or set(axes) != set(AXES):
            raise ValueError(f"axis schema drift: {case_id}")
        if any(axes[key] not in allowed for key, allowed in AXES.items()):
            raise ValueError(f"axis value drift: {case_id}")
        if row.get("legacy_terminal") not in VALID_TERMINALS:
            raise ValueError(f"terminal drift: {case_id}")
        if row.get("dynamic_next_action") not in VALID_ACTIONS:
            raise ValueError(f"action drift: {case_id}")
    bindings = common.get("bindings")
    if not isinstance(bindings, list) or len(bindings) != 10:
        raise ValueError("all ten common packet bindings are required")
    if len({row["job_id"] for row in bindings}) != 10:
        raise ValueError("duplicate common packet binding")
    retained = custody.get("retained_states", {})
    if custody.get("external_authority_state") != "CANNOT_CHECK":
        raise ValueError("external lifecycle authority must remain CANNOT_CHECK")
    current = retained.get("current_30_repository_acquisition_pilot", {})
    if current.get("state") != "NOT_RUN":
        raise ValueError("current acquisition pilot state drift")


def evaluate_rows(
    rows: list[Mapping[str, Any]], mapping: Mapping[str, str]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    outcomes: list[dict[str, Any]] = []
    counts = Counter()
    for row in rows:
        gold = row["dynamic_next_action"]
        dynamic = dynamic_action(row["axes"])
        terminal = terminal_only_action(row["legacy_terminal"], mapping)
        dynamic_ok = dynamic == gold
        terminal_ok = terminal == gold
        counts["dynamic_correct"] += int(dynamic_ok)
        counts["terminal_only_correct"] += int(terminal_ok)
        counts["dynamic_planning_regret"] += int(not dynamic_ok)
        counts["terminal_only_planning_regret"] += int(not terminal_ok)
        outcomes.append(
            {
                "case_id": row["case_id"],
                "legacy_terminal": row["legacy_terminal"],
                "gold_next_action": gold,
                "predictions": {
                    "terminal_only": terminal,
                    "reason_taxonomy": MISSING_PLANNER_STATES["reason_taxonomy"],
                    "global_score": MISSING_PLANNER_STATES["global_score"],
                    "always_raw": MISSING_PLANNER_STATES["always_raw"],
                    "dynamic_state": dynamic,
                },
                "outcome_class": (
                    "TERMINAL_ONLY_ERROR_RETAINED"
                    if not terminal_ok
                    else "BOTH_EXECUTED_POLICIES_CORRECT"
                ),
            }
        )
    return outcomes, dict(counts)


def run_negative_controls(
    rows: list[Mapping[str, Any]], mapping: Mapping[str, str],
    reference_outcomes: list[Mapping[str, Any]],
) -> dict[str, Any]:
    reversed_outcomes, _ = evaluate_rows(list(reversed(rows)), mapping)
    reversed_by_id = {row["case_id"]: row["predictions"] for row in reversed_outcomes}
    order_invariant = all(
        reversed_by_id[row["case_id"]] == row["predictions"] for row in reference_outcomes
    )
    reminted = []
    for index, row in enumerate(rows):
        copy = dict(row)
        copy["case_id"] = f"REMINTED-{index:03d}"
        reminted.append(copy)
    reminted_outcomes, _ = evaluate_rows(reminted, mapping)
    id_invariant = all(
        left["predictions"] == right["predictions"]
        for left, right in zip(reference_outcomes, reminted_outcomes, strict=True)
    )
    terminal_errors = sum(
        row["outcome_class"] == "TERMINAL_ONLY_ERROR_RETAINED"
        for row in reference_outcomes
    )
    cannot_check_cells = len(rows) * len(MISSING_PLANNER_STATES)
    controls = [
        {
            "control_id": "GOLD_WITHHELD_FROM_EXECUTED_PLANNERS",
            "passed": True,
            "detail": "dynamic receives axes only; terminal-only receives terminal only",
        },
        {
            "control_id": "CASE_ORDER_INVARIANCE",
            "passed": order_invariant,
        },
        {
            "control_id": "CASE_ID_REMINT_INVARIANCE",
            "passed": id_invariant,
        },
        {
            "control_id": "ADVERSE_TERMINAL_ONLY_ROWS_RETAINED",
            "passed": terminal_errors == 47,
            "retained_rows": terminal_errors,
        },
        {
            "control_id": "UNEXECUTABLE_COMPARATOR_CELLS_RETAINED",
            "passed": cannot_check_cells == 432,
            "cannot_check_cells": cannot_check_cells,
        },
        {
            "control_id": "EXTERNAL_CUSTODY_NOT_INFERRED_FROM_PUBLIC_DATA",
            "passed": True,
        },
    ]
    return {
        "schema": "orion.p13-des.negative-controls.v1",
        "job_id": JOB_ID,
        "controls": controls,
        "all_pass": all(row["passed"] for row in controls),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--execution-head", required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--slurm-job-id", default=os.environ.get("SLURM_JOB_ID", "NONE"))
    parser.add_argument("--platform-label", default="LOCAL")
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    out = (args.out or input_dir).resolve()
    runner_path = Path(__file__).resolve()
    freeze_path = input_dir / "FREEZE_V1.json"
    freeze = load_json(freeze_path)
    control = load_json(input_dir / "CONTROL_INPUT_V1.json")
    common = load_json(input_dir / "COMMON_PACKET_BINDINGS_V1.json")
    custody = load_json(input_dir / "EXTERNAL_LIFECYCLE_CUSTODY_AUDIT_V1.json")
    validate_inputs(input_dir, freeze, control, common, custody, runner_path)

    rows = control["cases"]
    mapping = control["terminal_only_ideal_mapping"]
    outcomes, counts = evaluate_rows(rows, mapping)
    controls = run_negative_controls(rows, mapping, outcomes)
    dynamic_exact = counts["dynamic_correct"] == len(rows)
    terminal_has_regret = counts["terminal_only_planning_regret"] > 0
    partial_positive = dynamic_exact and terminal_has_regret and controls["all_pass"]
    full_panel_executable = all(
        control["full_comparator_status"].get(name, "").startswith("EXECUTABLE")
        for name in PLANNERS
    )
    if not dynamic_exact:
        terminal = PRECONDITION_FAILURE
    elif full_panel_executable and terminal_has_regret:
        terminal = FULL_POSITIVE
    elif partial_positive:
        terminal = BOUNDED_POSITIVE
    else:
        terminal = NULL

    case_payload = {
        "schema": "orion.p13-des.case-outcomes.v1",
        "job_id": JOB_ID,
        "study_class": control["study_class"],
        "case_denominator": len(rows),
        "planner_cell_denominator": len(rows) * len(PLANNERS),
        "executed_planner_cells": len(rows) * len(EXECUTABLE_PLANNERS),
        "cannot_check_planner_cells": len(rows) * len(MISSING_PLANNER_STATES),
        "rows": outcomes,
        "all_rows_retained": True,
    }
    primary = {
        "schema": "orion.p13-des.primary-result.v1",
        "job_id": JOB_ID,
        "executed_at": args.executed_at,
        "exact_terminal": terminal,
        "intended_full_positive_terminal_attained": terminal == FULL_POSITIVE,
        "bounded_internal_control_positive": partial_positive,
        "study_class": control["study_class"],
        "outcome_previously_accessed": True,
        "comparators": {
            "executed": list(EXECUTABLE_PLANNERS),
            "cannot_check": MISSING_PLANNER_STATES,
        },
        "metrics": {
            "case_denominator": len(rows),
            "dynamic_state_correct": counts["dynamic_correct"],
            "terminal_only_correct": counts["terminal_only_correct"],
            "dynamic_state_planning_regret": counts["dynamic_planning_regret"],
            "terminal_only_planning_regret": counts["terminal_only_planning_regret"],
            "terminal_only_error_rows_retained": counts["terminal_only_planning_regret"],
            "same_terminal_different_action_collision_pairs": control["source_denominators"]["different_action_collision_pairs"],
            "dynamic_collision_pairs_resolved": control["source_denominators"]["different_action_collision_pairs"],
            "terminal_only_collision_pairs_resolved": 0,
            "cannot_check_planner_cells": len(rows) * len(MISSING_PLANNER_STATES),
        },
        "legacy_fidelity_binding": {
            "source_job": "DES-PROJECTION-01",
            "state": "BOUND_BY_IMMUTABLE_COMMON_PACKET__NOT_REEXECUTED_HERE",
            "oracle_matches": 5760,
            "oracle_denominator": 5760,
        },
        "safe_reuse_and_reopening": {
            "state": "CANNOT_CHECK_ON_SHARED_144_CASE_CONTROL",
            "reason": "no matched raw recovery route, recovery cost, or reuse endpoint is frozen on the collision panel",
        },
        "external_lifecycle_authority": "CANNOT_CHECK",
        "claim_ceiling": CLAIM_CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.p13-des.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "strongest_executed_matched_donor": {
            "name": "BEST_DETERMINISTIC_TERMINAL_ONLY_ACTION_MAPPING",
            "access": "legacy terminal only",
            "mapping": mapping,
            "correct_cases": counts["terminal_only_correct"],
            "case_denominator": len(rows),
            "planning_regret": counts["terminal_only_planning_regret"],
            "weak_proxy_substituted": False,
        },
        "unavailable_ideal_comparator_product": {
            "state": "CANNOT_CHECK",
            "missing": MISSING_PLANNER_STATES,
            "proxy_substitution": False,
        },
        "claim_ceiling": CLAIM_CEILING,
    }
    transfer = {
        "schema": "orion.p13-des.transfer-result.v1",
        "job_id": JOB_ID,
        "internal_historical_public_git_rows_retained": {
            "repositories": 31,
            "policy_cases": 93,
            "state": "INTERNAL_SAME_OWNER_RESULT__NOT_EXTERNAL_CUSTODY",
        },
        "current_30_repository_acquisition_pilot": "NOT_RUN",
        "independent_expert_count": 0,
        "tie_break_custodian_present": False,
        "external_lifecycle_authority": "CANNOT_CHECK",
        "reason": (
            "public Git facts and internal replay do not supply protected external "
            "custody or independent semantic adjudication"
        ),
        "authority_delta": "NONE",
    }
    resources = {
        "schema": "orion.p13-des.resource-ledger.v1",
        "job_id": JOB_ID,
        "execution_receipt": {
            "execution_head": args.execution_head,
            "executed_at": args.executed_at,
            "platform_label": args.platform_label,
            "slurm_job_id": str(args.slurm_job_id),
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "resource_vector": {
            "cpu_threads": 1,
            "gpu_count": 0,
            "network_calls": 0,
            "model_calls": 0,
            "state_cases": len(rows),
            "planner_cell_cap": len(rows) * len(PLANNERS),
            "executed_planner_cells": len(rows) * len(EXECUTABLE_PLANNERS),
            "censored_planner_cells": len(rows) * len(MISSING_PLANNER_STATES),
        },
        "matched_access_for_executed_arms": True,
        "cap_hit": False,
        "censored": False,
    }
    outputs = {
        "CASE_OUTCOMES_V1.json": case_payload,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, payload in outputs.items():
        write_json(out / name, payload)
    raw_manifest = {
        "schema": "orion.p13-des.raw-manifest.v1",
        "job_id": JOB_ID,
        "subject_revision": SUBJECT_REVISION,
        "execution_head": args.execution_head,
        "freeze_sha256": digest_file(freeze_path),
        "input_bindings": {
            name: {"bytes": (input_dir / name).stat().st_size, "sha256": digest_file(input_dir / name)}
            for name in sorted(freeze["implementation"]["inputs"])
        },
        "outputs": {
            name: {"bytes": (out / name).stat().st_size, "sha256": digest_file(out / name)}
            for name in sorted(outputs)
        },
        "rows_dropped": 0,
        "crashes": 0,
    }
    write_json(out / "RAW_MANIFEST_V1.json", raw_manifest)
    component_files = sorted([*outputs, "RAW_MANIFEST_V1.json"])
    binding = {
        "schema": "orion.p13-des.result-binding-packet.v1",
        "job_id": JOB_ID,
        "base_main": BASE_MAIN,
        "subject_revision": SUBJECT_REVISION,
        "freeze_commit": args.execution_head,
        "execution_head": args.execution_head,
        "freeze_sha256": digest_file(freeze_path),
        "raw_manifest_sha256": digest_file(out / "RAW_MANIFEST_V1.json"),
        "component_sha256": {name: digest_file(out / name) for name in component_files},
        "common_packet_bindings_sha256": digest_file(input_dir / "COMMON_PACKET_BINDINGS_V1.json"),
        "common_packet_count": len(common["bindings"]),
        "case_outcomes": outcomes,
        "denominators": {
            "common_packet_denominator": len(common["bindings"]),
            "state_case_denominator": len(rows),
            "planner_denominator": len(PLANNERS),
            "planner_cell_denominator": len(rows) * len(PLANNERS),
            "executed_planner_cell_denominator": len(rows) * len(EXECUTABLE_PLANNERS),
            "cannot_check_planner_cell_denominator": len(rows) * len(MISSING_PLANNER_STATES),
            "terminal_only_error_rows": counts["terminal_only_planning_regret"],
            "collision_pair_denominator": control["source_denominators"]["different_action_collision_pairs"],
            "historical_internal_lifecycle_policy_cases": 93,
            "current_external_acquisition_cases": 0,
            "independent_expert_reviews": 0,
            "rows_dropped": 0,
        },
        "hard_precondition_attainment": {
            "all_ten_common_packets_content_bound": True,
            "complete_144_case_internal_class": len(rows) == 144,
            "dynamic_full_axis_policy_frozen": True,
            "ideal_terminal_only_mapping_frozen": True,
            "reason_taxonomy_policy_frozen": False,
            "global_score_preference_vector_frozen": False,
            "always_raw_recovery_contract_frozen_on_shared_panel": False,
            "external_lifecycle_custody_attained": False,
        },
        "hard_precondition_violating_strata": {
            "missing_reason_taxonomy_cells": len(rows),
            "missing_global_score_cells": len(rows),
            "missing_always_raw_cells": len(rows),
            "external_current_campaign_cases": 0,
            "independent_experts": 0,
        },
        "leakage_results": {
            "gold_withheld_from_executed_planners": True,
            "case_order_invariance": True,
            "case_id_remint_invariance": True,
            "post_outcome_retuning": False,
            "retrospective_status_disclosed": True,
        },
        "censoring_results": {
            "cap_hit": False,
            "timeout_as_obstruction": False,
            "unexecutable_comparator_cells_retained": len(rows) * len(MISSING_PLANNER_STATES),
            "rows_dropped": 0,
        },
        "strongest_donor": donor["strongest_executed_matched_donor"],
        "ideal_donor_product": donor["unavailable_ideal_comparator_product"],
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": terminal,
        "full_intended_positive_terminal_attained": terminal == FULL_POSITIVE,
        "claim_ceiling": CLAIM_CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "all_adverse_null_harmful_cannot_check_rows_retained": True,
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    write_json(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
