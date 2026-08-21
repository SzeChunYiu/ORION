from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
FIXED_PATH = ROOT.parent / "gpt_r5" / "FIXED_SOURCE_SET_V1.json"
FIXED = json.loads(FIXED_PATH.read_text())

SCHEMA = "P1U.NativeOrionPrimaryAuthority.v1"
SCIENTIFIC_SCHEMA = "P1U.NativeOrionResult.v1"
PASS_TERMINAL = "P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION"
NOT_SUPPORTED_TERMINAL = "P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED"
CANNOT_CHECK_TERMINAL = "P1_R6_NATIVE_PRIMARY_CANNOT_CHECK_ABLATION_IDENTIFICATION"
DIAGNOSE = "DIAGNOSE.v1"
PROTECTED_ADVERSE_FAMILIES = frozenset(str(row["class"]) for row in FIXED["pair_sources"])


def _choice(arm: object) -> str:
    if not isinstance(arm, Mapping):
        raise ValueError("malformed arm result")
    decision = arm.get("result")
    if not isinstance(decision, Mapping):
        raise ValueError("malformed arm decision")
    return str(decision.get("choice", ""))


def _operator_ids(arm: object) -> set[str]:
    if not isinstance(arm, Mapping):
        raise ValueError("malformed arm result")
    decision = arm.get("result")
    if not isinstance(decision, Mapping):
        raise ValueError("malformed arm decision")
    root = decision.get("root")
    if not isinstance(root, Mapping):
        raise ValueError("missing native root lineage")
    operator_ids = root.get("operator_ids")
    if not isinstance(operator_ids, list):
        raise ValueError("malformed native root operator lineage")
    return set(map(str, operator_ids))


def reconstruct_ablation_identification(result: Mapping[str, object]) -> dict[str, object]:
    """Reconstruct the prospectively declared #723 ARD-vs-BASE behavioral gate.

    #723 required ORION_NATIVE_ARD to materially outperform *or* behaviorally differ
    from ORION_NATIVE_BASE on at least one protected adverse family. Earlier R6 code
    operationalized the behavioral branch on the adverse member grouped by the frozen
    class; a later evaluator revision weakened that coordinate to one choice difference
    anywhere in the corpus. No new threshold is introduced here.

    The reconstruction also proves that BASE exercised the repaired native DIAGNOSE
    path. Historical scores, comparators, metrics, margins and source identities remain
    untouched.
    """

    pair_rows = result.get("pair_rows")
    unresolved_rows = result.get("unresolved_rows")
    if not isinstance(pair_rows, list) or not isinstance(unresolved_rows, list):
        raise ValueError("R6 result lacks reconstructible episode rows")

    adverse_differences: Counter[str] = Counter()
    adverse_counts: Counter[str] = Counter()
    seen_families: set[str] = set()
    global_differences = 0
    base_episode_count = 0
    base_diagnose_count = 0

    for row in pair_rows:
        if not isinstance(row, Mapping):
            raise ValueError("malformed pair row")
        family = str(row.get("adverse_class", ""))
        seen_families.add(family)
        if family not in PROTECTED_ADVERSE_FAMILIES:
            raise ValueError(f"unfrozen adverse family: {family}")
        members = row.get("members")
        if not isinstance(members, Mapping):
            raise ValueError("pair row missing members")
        for member_name in ("adverse", "control"):
            member = members.get(member_name)
            if not isinstance(member, Mapping):
                raise ValueError(f"pair row missing {member_name} member")
            native = member.get("native_ard")
            base = member.get("native_base")
            native_choice = _choice(native)
            base_choice = _choice(base)
            base_episode_count += 1
            if DIAGNOSE in _operator_ids(base):
                base_diagnose_count += 1
            if native_choice != base_choice:
                global_differences += 1
                if member_name == "adverse":
                    adverse_differences[family] += 1
            if member_name == "adverse":
                adverse_counts[family] += 1

    for row in unresolved_rows:
        if not isinstance(row, Mapping):
            raise ValueError("malformed unresolved row")
        native = row.get("native_ard")
        base = row.get("native_base")
        native_choice = _choice(native)
        base_choice = _choice(base)
        base_episode_count += 1
        if DIAGNOSE in _operator_ids(base):
            base_diagnose_count += 1
        if native_choice != base_choice:
            global_differences += 1

    reported_global = result.get("native_base_choice_differences")
    if not isinstance(reported_global, int):
        raise ValueError("R6 result lacks integer native_base_choice_differences")

    checks = {
        "exact_frozen_protected_adverse_families": seen_families == PROTECTED_ADVERSE_FAMILIES,
        "base_diagnose_exercised_on_every_episode": base_diagnose_count == base_episode_count,
        "scientific_global_difference_count_reconstructs": global_differences == reported_global,
        "behaviorally_differs_on_at_least_one_protected_adverse_family": any(
            adverse_differences.get(family, 0) > 0 for family in PROTECTED_ADVERSE_FAMILIES
        ),
    }
    return {
        "checks": checks,
        "complete": all(checks.values()),
        "protected_adverse_families": sorted(PROTECTED_ADVERSE_FAMILIES),
        "adverse_episode_counts_by_family": dict(sorted(adverse_counts.items())),
        "ard_vs_base_adverse_choice_differences_by_family": {
            family: adverse_differences.get(family, 0)
            for family in sorted(PROTECTED_ADVERSE_FAMILIES)
        },
        "base_episode_count": base_episode_count,
        "base_diagnose_count": base_diagnose_count,
        "global_choice_differences_reconstructed": global_differences,
        "global_choice_differences_reported": reported_global,
    }


def classify_primary_authority(result: Mapping[str, object]) -> dict[str, object]:
    if str(result.get("schema", "")) != SCIENTIFIC_SCHEMA:
        raise ValueError("unexpected R6 scientific-result schema")
    data = result.get("data")
    if not isinstance(data, Mapping) or data.get("complete") is not True:
        raise ValueError("R6 scientific result is not bound to a complete frozen corpus")
    if result.get("policy_outcomes_generated") is not True:
        raise ValueError("R6 scientific result has no generated policy outcomes")

    scientific_terminal = str(result.get("terminal", ""))
    if scientific_terminal not in {PASS_TERMINAL, NOT_SUPPORTED_TERMINAL}:
        raise ValueError(f"unexpected R6 scientific terminal: {scientific_terminal}")

    reconstruction = reconstruct_ablation_identification(result)
    if scientific_terminal == PASS_TERMINAL and reconstruction["complete"] is True:
        authority_terminal = PASS_TERMINAL
        mechanism_identification = True
        authority_reason = (
            "The protected scientific primary passed, BASE exercised DIAGNOSE on every "
            "episode, and independent reconstruction verifies ARD-vs-BASE behavioral "
            "difference on prospectively frozen adverse families. The primary still cannot "
            "close #649 without the required source-disjoint 2019 replication."
        )
    elif scientific_terminal == PASS_TERMINAL:
        authority_terminal = CANNOT_CHECK_TERMINAL
        mechanism_identification = False
        authority_reason = (
            "The scientific score is preserved, but the predeclared ARD-vs-BASE behavioral "
            "identification coordinate did not reconstruct fail-closed from protected rows."
        )
    else:
        authority_terminal = NOT_SUPPORTED_TERMINAL
        mechanism_identification = False
        authority_reason = (
            "The frozen scientific evaluator did not satisfy its existing primary gates; "
            "this authority classifier adds no positive interpretation."
        )

    return {
        "schema": SCHEMA,
        "scientific_result_schema": SCIENTIFIC_SCHEMA,
        "scientific_terminal_preserved": scientific_terminal,
        "authority_terminal": authority_terminal,
        "authority_reason": authority_reason,
        "criterion_predeclared_before_scientific_outcome": True,
        "verification_performed_after_scientific_outcome": True,
        "new_post_outcome_threshold_introduced": False,
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixed_source_set_sha256": hashlib.sha256(FIXED_PATH.read_bytes()).hexdigest(),
        "ablation_identification_reconstruction": reconstruction,
        "historic_scores_mutated": False,
        "comparator_mutated": False,
        "metrics_mutated": False,
        "thresholds_mutated": False,
        "source_universe_mutated": False,
        "grants_primary_mechanism_identification_authority": mechanism_identification,
        "grants_issue_649_closure_authority": False,
        "grants_replication_closure_authority": False,
        "grants_registry_promotion_authority": False,
        "grants_merge_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = json.loads(args.result.read_text())
    authority = classify_primary_authority(result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n")
    print("P1_R6_PRIMARY_AUTHORITY_TERMINAL=" + str(authority["authority_terminal"]))


if __name__ == "__main__":
    main()
