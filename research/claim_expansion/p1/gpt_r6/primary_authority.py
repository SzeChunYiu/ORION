from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

SCHEMA = "P1U.NativeOrionPrimaryAuthority.v1"
SCIENTIFIC_SCHEMA = "P1U.NativeOrionResult.v1"
PASS_TERMINAL = "P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION"
NOT_SUPPORTED_TERMINAL = "P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED"
CANNOT_CHECK_TERMINAL = "P1_R6_NATIVE_PRIMARY_CANNOT_CHECK_ABLATION_MATERIALITY_UNDERDEFINED"


def classify_primary_authority(result: Mapping[str, object]) -> dict[str, object]:
    """Classify what the frozen R6 primary result may authorize.

    R6's protected evaluator preserved a useful scientific score, but its native-ARD
    versus native-BASE identification check was only ``choice_differences > 0`` over
    the whole corpus.  Issue #723 requires the claimed successor mechanism to
    materially outperform *or* behaviorally differ from BASE on at least one
    protected adverse family.  The frozen evaluator does not bind a protected-family
    label, direction, effect magnitude, or uncertainty rule for that coordinate.

    The protected outcome is already known, so inventing any of those missing rules
    now would be post-outcome tuning.  This classifier therefore preserves the
    scientific result byte-for-byte and only narrows its authority: an otherwise
    positive R6 primary is CANNOT_CHECK for mechanism-identification authority and
    cannot be promoted or used with a later replication to close #649.
    """

    if str(result.get("schema", "")) != SCIENTIFIC_SCHEMA:
        raise ValueError("unexpected R6 scientific-result schema")
    if result.get("data", {}).get("complete") is not True:  # type: ignore[union-attr]
        raise ValueError("R6 scientific result is not bound to a complete frozen corpus")
    if result.get("policy_outcomes_generated") is not True:
        raise ValueError("R6 scientific result has no generated policy outcomes")

    scientific_terminal = str(result.get("terminal", ""))
    if scientific_terminal not in {PASS_TERMINAL, NOT_SUPPORTED_TERMINAL}:
        raise ValueError(f"unexpected R6 scientific terminal: {scientific_terminal}")

    if scientific_terminal == PASS_TERMINAL:
        authority_terminal = CANNOT_CHECK_TERMINAL
        authority_reason = (
            "The frozen R6 evaluator reduced ARD-vs-BASE identification to at least one "
            "choice difference anywhere in the corpus. It does not bind the required "
            "protected adverse family or a prospective materiality/direction/uncertainty "
            "rule. Outcomes are already known, so those missing gates cannot be invented "
            "retroactively."
        )
    else:
        authority_terminal = NOT_SUPPORTED_TERMINAL
        authority_reason = (
            "The frozen scientific evaluator did not satisfy its existing primary gates; "
            "this authority classifier adds no positive interpretation."
        )

    return {
        "schema": SCHEMA,
        "scientific_result_schema": SCIENTIFIC_SCHEMA,
        "scientific_terminal_preserved": scientific_terminal,
        "authority_terminal": authority_terminal,
        "failure_class": (
            "UNDERDEFINED_ABLATION_MATERIALITY_AUTHORITY"
            if scientific_terminal == PASS_TERMINAL
            else "NONE_ADDED_BY_AUTHORITY_CLASSIFIER"
        ),
        "authority_reason": authority_reason,
        "historic_scores_mutated": False,
        "comparator_mutated": False,
        "metrics_mutated": False,
        "thresholds_mutated": False,
        "source_universe_mutated": False,
        "grants_primary_superiority_authority": False,
        "grants_replication_closure_authority": False,
        "grants_registry_promotion_authority": False,
        "grants_merge_authority": False,
        "requires_prospective_successor_for_mechanism_identification": (
            scientific_terminal == PASS_TERMINAL
        ),
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
