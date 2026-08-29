#!/usr/bin/env python3
"""Derive the paired-evidence interpretation for ORION-24 P14C and P14E.

This audit does not change either frozen benchmark or its terminal. It exposes
the paired discordance pattern and distinguishes a specification-conformance
count from population-level evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
P14C_CASES = HERE / "P14C_ADJUDICATION_CASES_V1.json"
P14C_RUNNER = HERE / "run_p14c_specification_separated_governance_v1.py"
P14E_RESULT = HERE / "P14E_SUPERIORITY_RESULT_V1.json"
OUT = HERE / "P14_PAIRED_EVIDENCE_INTERPRETATION_V1.json"

SUBJECT = "ORION_RSE_FULL"
COMPARATOR = "MULTI_REVIEW"
DISCRIMINATING_STRATUM = "RETAIN_NEGATIVE"
TERMINAL = (
    "P14_PAIRED_EVIDENCE_INTERPRETATION_COMPLETE__"
    "CONTROLLED_CONFORMANCE_ONLY__NO_POPULATION_SUPERIORITY"
)


def _load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


def exact_two_sided_binomial_p(successes: int, failures: int) -> float:
    """Two-sided exact sign/McNemar p-value for a 0.5 null.

    This is the doubled smaller tail, capped at one. Tied pairs are omitted.
    """
    if successes < 0 or failures < 0:
        raise ValueError("counts must be non-negative")
    n = successes + failures
    if n == 0:
        return 1.0
    lower = min(successes, failures)
    tail = sum(math.comb(n, k) for k in range(lower + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def _p14c() -> dict[str, Any]:
    runner = _load(P14C_RUNNER, "orion_p14c_paired_interpretation")
    payload = json.loads(P14C_CASES.read_text(encoding="utf-8"))
    cases = list(payload["cases"])
    policies: dict[str, Callable[[dict[str, bool]], str]] = {
        SUBJECT: runner.full_policy,
        COMPARATOR: runner.multi_review,
    }

    rows: list[dict[str, Any]] = []
    table = Counter()
    strata: dict[str, Counter[str]] = defaultdict(Counter)
    for case in cases:
        facts = runner.facts_only(case)
        gold = str(case["gold_disposition"])
        correct = {
            arm: policies[arm](facts) == gold
            for arm in (SUBJECT, COMPARATOR)
        }
        if correct[SUBJECT] and correct[COMPARATOR]:
            cell = "both_correct"
        elif correct[SUBJECT]:
            cell = "subject_only_correct"
        elif correct[COMPARATOR]:
            cell = "comparator_only_correct"
        else:
            cell = "both_wrong"
        table[cell] += 1
        strata[str(case["stratum"])][cell] += 1
        rows.append(
            {
                "case_id": str(case["case_id"]),
                "stratum": str(case["stratum"]),
                "gold": gold,
                "subject_prediction": policies[SUBJECT](facts),
                "comparator_prediction": policies[COMPARATOR](facts),
                "paired_cell": cell,
            }
        )

    expected = {
        "both_correct": 24,
        "subject_only_correct": 4,
        "comparator_only_correct": 0,
        "both_wrong": 0,
    }
    observed = {key: table[key] for key in expected}
    if observed != expected:
        raise AssertionError(f"P14C paired table drifted: {observed}")
    discordant = [
        row for row in rows
        if row["paired_cell"] in {"subject_only_correct", "comparator_only_correct"}
    ]
    discordant_strata = sorted({row["stratum"] for row in discordant})
    if discordant_strata != [DISCRIMINATING_STRATUM]:
        raise AssertionError(f"P14C discordance moved: {discordant_strata}")

    stratum_outcomes: dict[str, str] = {}
    for stratum, counts in sorted(strata.items()):
        subject_correct = counts["both_correct"] + counts["subject_only_correct"]
        comparator_correct = counts["both_correct"] + counts["comparator_only_correct"]
        if subject_correct > comparator_correct:
            outcome = "subject_win"
        elif subject_correct < comparator_correct:
            outcome = "comparator_win"
        else:
            outcome = "tie"
        stratum_outcomes[stratum] = outcome

    outcome_counts = Counter(stratum_outcomes.values())
    leave_one_out: dict[str, dict[str, float | int]] = {}
    for held_out in sorted(strata):
        kept = [row for row in rows if row["stratum"] != held_out]
        subject_correct = sum(
            row["paired_cell"] in {"both_correct", "subject_only_correct"}
            for row in kept
        )
        comparator_correct = sum(
            row["paired_cell"] in {"both_correct", "comparator_only_correct"}
            for row in kept
        )
        leave_one_out[held_out] = {
            "n_cases": len(kept),
            "subject_accuracy": subject_correct / len(kept),
            "comparator_accuracy": comparator_correct / len(kept),
            "accuracy_difference": (subject_correct - comparator_correct) / len(kept),
        }

    case_p = exact_two_sided_binomial_p(
        table["subject_only_correct"], table["comparator_only_correct"]
    )
    stratum_p = exact_two_sided_binomial_p(
        outcome_counts["subject_win"], outcome_counts["comparator_win"]
    )
    if case_p != 0.125 or stratum_p != 1.0:
        raise AssertionError((case_p, stratum_p))

    return {
        "benchmark": "P14C",
        "frozen_cases": len(cases),
        "semantic_strata": len(strata),
        "subject": SUBJECT,
        "comparator": COMPARATOR,
        "paired_correctness_table": observed,
        "accuracy_difference": table["subject_only_correct"] / len(cases),
        "discordant_case_ids": [row["case_id"] for row in discordant],
        "discordant_strata": discordant_strata,
        "case_level_exact_mcnemar_two_sided_p": case_p,
        "case_level_test_role": (
            "DIAGNOSTIC_ONLY: the four cases are precedence variants from one "
            "authored stratum, not independent population draws"
        ),
        "stratum_outcomes": stratum_outcomes,
        "stratum_outcome_counts": {
            "subject_wins": outcome_counts["subject_win"],
            "comparator_wins": outcome_counts["comparator_win"],
            "ties": outcome_counts["tie"],
        },
        "stratum_level_exact_sign_two_sided_p": stratum_p,
        "leave_one_stratum_out": leave_one_out,
        "interpretation": (
            "The complete contract matches every registered P14C case while "
            "MULTI_REVIEW misses the four RETAIN_NEGATIVE variants. Removing "
            "that one stratum removes the entire measured advantage. P14C "
            "therefore establishes frozen-specification conformance, not a "
            "population-level superiority effect."
        ),
    }


def _p14e() -> dict[str, Any]:
    result = json.loads(P14E_RESULT.read_text(encoding="utf-8"))
    core = result["core"]
    design = core["design"]
    summary = core["summary"]
    families = list(core["families"])
    per_stratum = core["per_stratum_accuracy"]

    n_families = int(design["n_families"])
    cases_per_stratum = int(design["cases_per_stratum_per_family"])
    strata = list(design["strata"])
    total_cases = int(design["total_cases"])
    differences = [
        float(family["arm_correct"][SUBJECT])
        - float(family["arm_correct"][COMPARATOR])
        for family in families
    ]
    expected_difference = 1.0 / len(strata)
    if n_families != 12 or len(families) != 12:
        raise AssertionError("P14E family count drifted")
    if total_cases != n_families * len(strata) * cases_per_stratum:
        raise AssertionError("P14E case arithmetic drifted")
    if any(abs(value - expected_difference) > 1e-15 for value in differences):
        raise AssertionError(f"P14E family differences are no longer design-fixed: {differences}")

    subject_by_stratum = per_stratum[SUBJECT]
    comparator_by_stratum = per_stratum[COMPARATOR]
    differing_strata = sorted(
        stratum
        for stratum in strata
        if subject_by_stratum[stratum] != comparator_by_stratum[stratum]
    )
    if differing_strata != [DISCRIMINATING_STRATUM]:
        raise AssertionError(f"P14E differing strata drifted: {differing_strata}")

    discordant_per_family = cases_per_stratum
    discordant_total = n_families * discordant_per_family
    return {
        "benchmark": "P14E",
        "total_cases": total_cases,
        "nominal_families": n_families,
        "semantic_strata": len(strata),
        "cases_per_stratum_per_family": cases_per_stratum,
        "subject": SUBJECT,
        "comparator": COMPARATOR,
        "subject_accuracy": float(summary[SUBJECT]["disposition_accuracy"]),
        "comparator_accuracy": float(summary[COMPARATOR]["disposition_accuracy"]),
        "accuracy_difference": float(result["accuracy_gain_vs_strongest"]),
        "differing_strata": differing_strata,
        "subject_only_correct_cases": discordant_total,
        "comparator_only_correct_cases": 0,
        "subject_only_correct_cases_per_family": discordant_per_family,
        "family_accuracy_differences": differences,
        "between_family_standard_deviation": statistics.pstdev(differences),
        "case_level_exact_test": "NOT_APPLICABLE_AS_POPULATION_INFERENCE",
        "reason": (
            "Each family contains exactly the same number of cases in each "
            "semantic stratum, and the complete and partial policies differ "
            "only on the fully pinned RETAIN_NEGATIVE stratum. Nuisance "
            "randomization cannot move this paired correctness contrast. The "
            "960-to-0 discordance is therefore fixed by the benchmark design, "
            "not an estimate from 6,720 independent scientific decisions."
        ),
        "interpretation": (
            "P14E is a larger deterministic stress test of the registered "
            "governance logic. It strengthens implementation and replay "
            "evidence but does not convert internal authored cases into "
            "external scientific-validity or real-agent superiority evidence."
        ),
    }


def derive() -> dict[str, Any]:
    return {
        "schema": "ORION.P14.PairedEvidenceInterpretation.v1",
        "paper_id": "ORION-24",
        "scientific_authority_delta": "NONE",
        "p14c": _p14c(),
        "p14e": _p14e(),
        "claim_ceiling": {
            "authorized": (
                "The complete ORION-RSE implementation conforms to every "
                "registered P14C/P14E governance case while the strongest "
                "partial contract misses the registered retained-negative "
                "stratum."
            ),
            "not_authorized": [
                "population-level superiority",
                "external scientific validity",
                "real-agent superiority",
                "cross-domain generalization",
                "independent external adjudication",
            ],
        },
        "terminal": TERMINAL,
    }


def render() -> str:
    return json.dumps(derive(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rendered = render()
    if args.check:
        committed = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if committed != rendered:
            print(f"stale paired-evidence interpretation: {OUT}", file=sys.stderr)
            return 1
        print(TERMINAL)
        return 0
    if args.write:
        OUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUT}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
