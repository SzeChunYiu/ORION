"""P1-U R6-DR1 campaign runner.

Executes the arms frozen in ``FREEZE_2026-08-21_DIAGNOSE_REACHABLE_V1.md`` over the
48-episode frozen R5 corpus and emits one receipt with its own identity and digest.

The scoring functions, the comparator, the corpus and every threshold are imported
from the frozen R6 modules rather than re-implemented, so this runner cannot drift
from them. What it adds is the thing the failed campaign lacked: a precondition
gate that refuses to score an arm which never executed ``DIAGNOSE``.

This campaign writes only into its own directory. It edits no artifact of the
campaign it succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
R6 = HERE.parent / "gpt_r6"

CAMPAIGN_ID = "P1U-R6-DR1"
FREEZE_FILENAME = "FREEZE_2026-08-21_DIAGNOSE_REACHABLE_V1.md"
RECEIPT_FILENAME = "P1_R6_DR1_RECEIPT_V1.json"

ARD_ARM = "ORION_NATIVE_ARD_DR1"
BASE_ARM = "ORION_NATIVE_BASE_DR1"


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


REPAIR = _load(HERE / "repaired_root_v1.py", "p1_r6_dr1_repaired_root")
EVAL = _load(R6 / "evaluate_native.py", "p1_r6_dr1_frozen_evaluator")
CORE = EVAL.NATIVE._CORE

from orion.transfer.v2.canonical import content_digest  # noqa: E402
from orion_research_harness.operator_coverage import (  # noqa: E402
    OperatorNotExercised,
    compare_operator_coverage,
)


def freeze_digest() -> str:
    return hashlib.sha256((HERE / FREEZE_FILENAME).read_bytes()).hexdigest()


def _first_sequence(ledger: Any, arm: str) -> list[str]:
    """The operator sequence of this arm's first scored root run."""

    for row in ledger.reports:
        if row["arm"] == arm:
            return list(row["coverage"]["operator_sequence"])
    return []


def _episode_rows(
    pairs: Sequence[Mapping[str, Any]], unresolved: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Flatten the frozen corpus into the 48 scored episodes, in a fixed order."""

    rows: list[dict[str, Any]] = []
    for pair in pairs:
        note = str(pair["pair_evidence"]["source_claim"])
        for member in ("adverse", "control"):
            rows.append(
                {
                    "episode": pair[member],
                    "gold_class": str(pair[member]["gold_class"]),
                    "evidence_note": note,
                    "member": member,
                    "pair_id": str(pair["pair_id"]),
                    "adverse_class": str(pair["adverse_class"]),
                    "actual_domain": str(pair["actual_domain"]),
                }
            )
    for episode in unresolved:
        rows.append(
            {
                "episode": episode,
                "gold_class": EVAL.UNRESOLVED,
                "evidence_note": str(episode["admission_evidence"]["source_claim"]),
                "member": "unresolved",
                "pair_id": None,
                "adverse_class": EVAL.UNRESOLVED,
                "actual_domain": str(episode["actual_domain"]),
            }
        )
    return rows


def run_campaign() -> dict[str, Any]:
    pairs, unresolved = EVAL.fixed_corpus()
    corpus = EVAL.validate_fixed_corpus(pairs, unresolved)
    if not corpus["complete"]:
        return {
            "schema": "P1U.NativeOrionDR1Result.v1",
            "campaign_id": CAMPAIGN_ID,
            "freeze_document": FREEZE_FILENAME,
            "freeze_sha256": freeze_digest(),
            "corpus": corpus,
            "policy_outcomes_generated": False,
            "terminal": "P1_R6_DR1_CANNOT_CHECK_FIXED_CORPUS",
        }

    ledger = REPAIR.RootCoverageLedger()
    rows: list[dict[str, Any]] = []
    ard_minus_b3: list[float] = []
    ard_minus_base: list[float] = []
    base_status_counts: Counter[str] = Counter()
    ard_false_high = b3_false_high = 0
    ard_lower_skip = ard_false_unresolved = control_harm = 0
    base_native_diagnosis_nonempty = 0
    sample_outcomes: dict[str, list[str]] = {}

    try:
        for row in _episode_rows(pairs, unresolved):
            episode = row["episode"]
            gold = row["gold_class"]
            ard = REPAIR.run_ard_dr1(
                CORE, episode, evidence_note=row["evidence_note"], ledger=ledger
            )
            base = REPAIR.run_base_dr1(CORE, episode, ledger=ledger)
            b3 = EVAL._b3(episode)
            EVAL._verify_native_lineage(ard)
            EVAL._verify_native_lineage(base)

            ard_score = EVAL._score(str(ard["choice"]), gold)
            base_score = EVAL._score(str(base["choice"]), gold)
            b3_score = EVAL._score(str(b3["choice"]), gold)

            ard_minus_b3.append(ard_score["grs"] - b3_score["grs"])
            ard_minus_base.append(ard_score["grs"] - base_score["grs"])
            base_status_counts[str(base["responsibility_status"])] += 1
            if list(base["root"]["provider_native_responsibilities"]):
                base_native_diagnosis_nonempty += 1
            ard_false_high += ard_score["false_high_level"]
            b3_false_high += b3_score["false_high_level"]
            ard_lower_skip += ard_score["harmful_lower_level_skip"]
            ard_false_unresolved += ard_score["false_resolution_of_unresolved"]
            if row["member"] == "control":
                control_harm += ard_score["false_high_level"]

            if not sample_outcomes:
                # Cycle-operator names, not `.v1` mechanic ids: `run_operator_coverage`
                # keys off CycleOperator values, and feeding it mechanic ids would
                # report every arm as having executed nothing.
                sample_outcomes = {
                    arm: list(_first_sequence(ledger, arm))
                    for arm in (ARD_ARM, BASE_ARM)
                }

            rows.append(
                {
                    "episode_id": str(episode["id"]),
                    "member": row["member"],
                    "pair_id": row["pair_id"],
                    "adverse_class": row["adverse_class"],
                    "actual_domain": row["actual_domain"],
                    "gold_class": gold,
                    "ard": {"result": ard, "score": ard_score},
                    "base": {"result": base, "score": base_score},
                    "b3": {"result": b3, "score": b3_score},
                }
            )
    except OperatorNotExercised as exc:
        return {
            "schema": "P1U.NativeOrionDR1Result.v1",
            "campaign_id": CAMPAIGN_ID,
            "freeze_document": FREEZE_FILENAME,
            "freeze_sha256": freeze_digest(),
            "corpus": corpus,
            "policy_outcomes_generated": False,
            "episodes_scored_before_stop": len(rows),
            "precondition_failure": str(exc),
            "terminal": "P1_R6_DR1_CANNOT_CHECK_UNREACHABLE_OPERATOR",
        }

    cfg = CORE.PROTOCOL["decision_rule"]
    reps = int(cfg["bootstrap_replicates"])
    interval = float(cfg["stability_interval"])
    primary_seed = int(cfg["bootstrap_seed"])
    attribution_seed = primary_seed + 3

    primary = EVAL._mean(ard_minus_b3)
    primary_lo, primary_hi = EVAL._bootstrap(
        ard_minus_b3, reps=reps, seed=primary_seed, interval=interval
    )
    attribution = EVAL._mean(ard_minus_base)
    attribution_lo, attribution_hi = EVAL._bootstrap(
        ard_minus_base, reps=reps, seed=attribution_seed, interval=interval
    )

    n = len(rows)
    ard_false_high_rate = ard_false_high / n
    b3_false_high_rate = b3_false_high / n
    margin = float(cfg["episode_grs_margin"])

    coverage_comparison = compare_operator_coverage(
        [(ARD_ARM, sample_outcomes[ARD_ARM]), (BASE_ARM, sample_outcomes[BASE_ARM])]
    )

    checks = {
        "primary_margin": primary >= margin,
        "primary_stability_lower_positive": primary_lo > 0,
        "attribution_margin": attribution >= margin,
        "attribution_stability_lower_positive": attribution_lo > 0,
        "base_diagnose_reached_all": ledger.diagnose_reached(BASE_ARM) == n,
        "ard_diagnose_reached_all": ledger.diagnose_reached(ARD_ARM) == n,
        "base_native_diagnosis_nonempty_all": base_native_diagnosis_nonempty == n,
        "false_high_level_guard": ard_false_high_rate <= b3_false_high_rate
        and ard_false_high_rate <= float(cfg["max_false_high_level_rate"]),
        "zero_lower_level_skip": ard_lower_skip
        <= int(cfg["harmful_lower_level_skip_tolerance"]),
        "zero_false_unresolved_resolution": ard_false_unresolved
        <= int(cfg["false_resolution_of_unresolved_tolerance"]),
        "zero_control_high_level_harm": control_harm == 0,
    }

    harm_ok = all(
        checks[name]
        for name in (
            "false_high_level_guard",
            "zero_lower_level_skip",
            "zero_false_unresolved_resolution",
            "zero_control_high_level_harm",
        )
    )
    primary_ok = checks["primary_margin"] and checks["primary_stability_lower_positive"]
    attribution_ok = (
        checks["attribution_margin"] and checks["attribution_stability_lower_positive"]
    )
    if not primary_ok:
        terminal = "P1_R6_DR1_NOT_SUPPORTED"
    elif attribution_ok and harm_ok:
        terminal = "P1_R6_DR1_ATTRIBUTABLE_SUPERIORITY"
    else:
        terminal = "P1_R6_DR1_UNATTRIBUTED_MARGIN"

    payload: dict[str, Any] = {
        "schema": "P1U.NativeOrionDR1Result.v1",
        "campaign_id": CAMPAIGN_ID,
        "freeze_document": FREEZE_FILENAME,
        "freeze_sha256": freeze_digest(),
        "supersedes_no_artifact_of": "P1-U R6 native primary (#723); its record stands unedited",
        "corpus": corpus,
        "policy_outcomes_generated": True,
        "n_episodes": n,
        "operator_precondition": {
            "required": sorted(REPAIR.REQUIRED_ROOT_OPERATORS),
            "enforced_per_episode": True,
            "diagnose_reached": {
                ARD_ARM: ledger.diagnose_reached(ARD_ARM),
                BASE_ARM: ledger.diagnose_reached(BASE_ARM),
            },
            "root_runs_checked": {
                ARD_ARM: ledger.count(ARD_ARM),
                BASE_ARM: ledger.count(BASE_ARM),
            },
            "arm_operator_comparison": coverage_comparison,
            # Freeze section 10: the coverage report for every native root run,
            # not a summary of them. `never_executed` on each row is what makes
            # "this arm did run the mechanism" checkable after the fact.
            "root_operator_coverage_reports": ledger.reports,
        },
        "primary_ard_minus_b3_episode_grs": primary,
        "primary_bootstrap_95_stability": [primary_lo, primary_hi],
        "primary_bootstrap_seed": primary_seed,
        "attribution_ard_minus_base_episode_grs": attribution,
        "attribution_bootstrap_95_stability": [attribution_lo, attribution_hi],
        "attribution_bootstrap_seed": attribution_seed,
        "bootstrap_replicates": reps,
        "stability_interval": interval,
        "margin_threshold": margin,
        "base_responsibility_status_counts": dict(sorted(base_status_counts.items())),
        "base_native_diagnosis_nonempty": base_native_diagnosis_nonempty,
        "ard_false_high_level_rate": ard_false_high_rate,
        "b3_false_high_level_rate": b3_false_high_rate,
        "ard_harmful_lower_level_skips": ard_lower_skip,
        "ard_false_resolution_of_unresolved": ard_false_unresolved,
        "control_high_level_harm": control_harm,
        "checks": checks,
        "terminal": terminal,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "episode_rows": rows,
    }
    payload["digest"] = content_digest(payload)
    return payload


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Run the P1-U R6-DR1 campaign.")
    parser.add_argument("--out", type=Path, default=HERE / RECEIPT_FILENAME)
    args = parser.parse_args(list(argv))
    result = run_campaign()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {
        key: result[key]
        for key in (
            "campaign_id",
            "terminal",
            "n_episodes",
            "primary_ard_minus_b3_episode_grs",
            "primary_bootstrap_95_stability",
            "attribution_ard_minus_base_episode_grs",
            "attribution_bootstrap_95_stability",
            "base_responsibility_status_counts",
            "checks",
            "digest",
        )
        if key in result
    }
    summary["diagnose_reached"] = result.get("operator_precondition", {}).get(
        "diagnose_reached"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
