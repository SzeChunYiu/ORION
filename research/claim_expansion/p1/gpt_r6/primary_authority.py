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
CANNOT_CHECK_TERMINAL = "P1_R6_NATIVE_PRIMARY_CANNOT_CHECK_ABLATION_AUTHORITY_UNBOUND"
DIAGNOSE = "DIAGNOSE.v1"
FROZEN_CLASSES = frozenset(str(row["class"]) for row in FIXED["pair_sources"])


def _decision(arm: object) -> Mapping[str, object]:
    if not isinstance(arm, Mapping):
        raise ValueError("malformed arm result")
    decision = arm.get("result")
    if not isinstance(decision, Mapping):
        raise ValueError("malformed arm decision")
    return decision


def diagnostic_reconstruction(result: Mapping[str, object]) -> dict[str, object]:
    """Reconstruct observed ARD/BASE behavior without granting scientific authority.

    The frozen issue text asked for material outperformance *or* behavioral difference
    on a protected adverse family, but the protected 2020 evaluator bound only a single
    corpus-wide choice-difference count.  No pre-outcome authority receipt binds what a
    "protected adverse family" is or how its behavioral/materiality branch is scored.
    Therefore these diagnostics may localize the gap but must not repair it post hoc.
    """
    pair_rows = result.get("pair_rows")
    unresolved_rows = result.get("unresolved_rows")
    if not isinstance(pair_rows, list) or not isinstance(unresolved_rows, list):
        raise ValueError("R6 result lacks reconstructible episode rows")

    adverse_differences: Counter[str] = Counter()
    adverse_counts: Counter[str] = Counter()
    seen_classes: set[str] = set()
    global_differences = 0
    base_episode_count = 0
    base_diagnose_count = 0

    for row in pair_rows:
        if not isinstance(row, Mapping):
            raise ValueError("malformed pair row")
        family = str(row.get("adverse_class", ""))
        if family not in FROZEN_CLASSES:
            raise ValueError(f"unfrozen adverse class: {family}")
        seen_classes.add(family)
        members = row.get("members")
        if not isinstance(members, Mapping):
            raise ValueError("pair row missing members")
        for member_name in ("adverse", "control"):
            member = members.get(member_name)
            if not isinstance(member, Mapping):
                raise ValueError(f"pair row missing {member_name} member")
            native = _decision(member.get("native_ard"))
            base = _decision(member.get("native_base"))
            native_choice = str(native.get("choice", ""))
            base_choice = str(base.get("choice", ""))
            base_episode_count += 1
            root = base.get("root")
            if not isinstance(root, Mapping):
                raise ValueError("missing BASE root lineage")
            ops = root.get("operator_ids")
            if not isinstance(ops, list):
                raise ValueError("malformed BASE operator lineage")
            if DIAGNOSE in set(map(str, ops)):
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
        native = _decision(row.get("native_ard"))
        base = _decision(row.get("native_base"))
        base_episode_count += 1
        root = base.get("root")
        if not isinstance(root, Mapping):
            raise ValueError("missing BASE root lineage")
        ops = root.get("operator_ids")
        if not isinstance(ops, list):
            raise ValueError("malformed BASE operator lineage")
        if DIAGNOSE in set(map(str, ops)):
            base_diagnose_count += 1
        if str(native.get("choice", "")) != str(base.get("choice", "")):
            global_differences += 1

    reported = result.get("native_base_choice_differences")
    if not isinstance(reported, int):
        raise ValueError("R6 result lacks integer native_base_choice_differences")

    checks = {
        "exact_frozen_adverse_classes_observed": seen_classes == FROZEN_CLASSES,
        "base_diagnose_exercised_on_every_episode": base_diagnose_count == base_episode_count,
        "scientific_global_difference_count_reconstructs": global_differences == reported,
    }
    return {
        "diagnostic_only_no_authority": True,
        "checks": checks,
        "complete": all(checks.values()),
        "frozen_adverse_classes": sorted(FROZEN_CLASSES),
        "adverse_episode_counts_by_class": dict(sorted(adverse_counts.items())),
        "ard_vs_base_adverse_choice_differences_by_class": {
            family: adverse_differences.get(family, 0) for family in sorted(FROZEN_CLASSES)
        },
        "base_episode_count": base_episode_count,
        "base_diagnose_count": base_diagnose_count,
        "global_choice_differences_reconstructed": global_differences,
        "global_choice_differences_reported": reported,
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

    diagnostic = diagnostic_reconstruction(result)
    if scientific_terminal == PASS_TERMINAL:
        authority_terminal = CANNOT_CHECK_TERMINAL
        reason = (
            "The frozen scientific primary is preserved as a positive score, and post-outcome "
            "diagnostics can reconstruct BASE lineage and class-bucketed behavior. However, "
            "the protected 2020 evaluator did not prospectively bind the protected-family "
            "identity/materiality operationalization required for mechanism attribution. "
            "Post-outcome diagnostics cannot mint that missing authority."
        )
    else:
        authority_terminal = NOT_SUPPORTED_TERMINAL
        reason = "The frozen scientific evaluator did not satisfy its existing primary gates."

    return {
        "schema": SCHEMA,
        "scientific_result_schema": SCIENTIFIC_SCHEMA,
        "scientific_terminal_preserved": scientific_terminal,
        "authority_terminal": authority_terminal,
        "authority_reason": reason,
        "authority_verifier_bound_before_scientific_outcome": False,
        "post_outcome_diagnostic_reconstruction": diagnostic,
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixed_source_set_sha256": hashlib.sha256(FIXED_PATH.read_bytes()).hexdigest(),
        "historic_scores_mutated": False,
        "comparator_mutated": False,
        "metrics_mutated": False,
        "thresholds_mutated": False,
        "source_universe_mutated": False,
        "grants_primary_mechanism_identification_authority": False,
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
