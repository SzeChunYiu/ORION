"""Runner for the open-world acquisition successor study.

Executes the six arms of `acq_mechanics` over the constructed world of
`acq_world`, evaluates the six gates the freeze document pre-committed, and
writes one result artifact. It refuses to run if its own parameter block does not
hash to the digest recorded in the freeze document's JSON twin, and it refuses to
report arm numbers over a world that fails the construction preconditions — a
world whose apparatus vocabulary is not actually non-discriminative, or whose gold
is not actually distinguishable, is not a reproduction of the failure under
repair.

Nothing here may be edited to make a gate pass. If a gate fails, the failure is
the result.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import acq_mechanics as mech
from . import acq_world as world_module
from .acq_world import (
    FAMILY_DISTINGUISHABLE,
    FAMILY_NO_BRIDGE,
    FAMILY_ORDER,
    FAMILY_UNDISTINGUISHED,
    FAMILY_VARIANT_GAP,
    FAMILY_WELL_POSED,
    AcquisitionWorld,
    build_acquisition_world,
)
from .corpus import sha256_digest

RESULT_SCHEMA_VERSION = "orion.p2.open-world-acquisition-result.v1"

FREEZE_DOCUMENT = (
    "papers/orion-12-open-world-scientific-discovery/protocol/"
    "P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.md"
)
FREEZE_TWIN = (
    "papers/orion-12-open-world-scientific-discovery/protocol/"
    "P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.json"
)
DEFAULT_OUTPUT = (
    "papers/orion-12-open-world-scientific-discovery/evidence/successor_results/"
    "P2_OPEN_WORLD_ACQUISITION_RESULT_2026-08-22.json"
)

BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED = 20260822

# --------------------------------------------------------------------------
# Pre-committed gates. Thresholds come from the freeze document, section 5.
# --------------------------------------------------------------------------

GATES: dict[str, Any] = {
    "G1_REPRODUCTION": {
        "statement": (
            "on distinguishable: B0 mean recall <= 0.12 and B0 zero-hit fraction "
            ">= 0.60 and B0 mean candidates returned >= 18"
        ),
        "max_baseline_mean_recall": 0.12,
        "min_baseline_zero_hit_fraction": 0.60,
        "min_baseline_candidates_returned": 18.0,
        "reference": (
            "DEV3R archived baseline: mean recall 0.051422, zero-hit 19/24 = 0.7917, "
            "mean_candidates_returned 20.0"
        ),
        "blocking": True,
    },
    "G2_CANDIDATE": {
        "statement": (
            "on distinguishable: S2 - B0 mean recall >= 0.30 and S2 mean recall "
            ">= 0.40 and exact two-sided sign test p < 0.01 and the 95% paired "
            "bootstrap lower bound on the mean difference > 0"
        ),
        "min_absolute_gain": 0.30,
        "min_candidate_mean_recall": 0.40,
        "max_p_value": 0.01,
        "require_bootstrap_lower_bound_above": 0.0,
        "blocking": True,
    },
    "G3_MARGIN_OVER_SHIPPED": {
        "statement": "on distinguishable: S2 - B1 mean recall >= 0.10",
        "min_margin": 0.10,
        "rationale": (
            "B1 is the shipped D1/D2/D3 trio. If the whole repair is already "
            "available from the shipped derivations under a different merge, the "
            "candidate is not a materially stronger mechanism and the freeze commits "
            "to saying so."
        ),
        "blocking": True,
    },
    "G4_NO_HARM": {
        "statement": (
            "on well_posed: S2 mean recall >= max(B0, B1) mean recall - 0.05"
        ),
        "max_allowed_loss": 0.05,
        "vacuity_floor": 0.30,
        "blocking": True,
    },
    "G5_BRIDGE_SPECIFICITY": {
        "statement": "on no_bridge: S2 - A3 mean recall <= 0.10",
        "max_allowed_gain": 0.10,
        "rationale": (
            "A3 is S2 without grounded expansion. Where the corpus contains no "
            "record using both vocabularies, expansion must earn nothing; a gain "
            "here would mean the expansion is fitting something other than a bridge."
        ),
        "blocking": False,
    },
    "G6_UNDISTINGUISHED_CEILING": {
        "statement": "on undistinguished: S2 - B0 mean recall <= 0.10",
        "max_allowed_gain": 0.10,
        "rationale": (
            "The family in which gold is built to be lexically indistinguishable "
            "from adjacent work. No surface-lexical mechanic should lift recall "
            "there. This gate is the study's own boundary: if the live Wide gold is "
            "undistinguished in this sense, no query-derivation upgrade repairs it."
        ),
        "blocking": False,
    },
}

FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P2_OPEN_WORLD_ACQUISITION_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "world": world_module.PARAMETERS,
    "mechanics": mech.MECHANIC_PARAMETERS,
    "gates": GATES,
    "primary_outcome": "mean recall at the 20-candidate cap on the distinguishable family, S2 versus B0",
    "statistic": (
        "exact two-sided sign test on paired per-task recall, plus a 95% percentile "
        f"paired bootstrap ({BOOTSTRAP_RESAMPLES} resamples, seed {BOOTSTRAP_SEED})"
    ),
    "verdict_rule": (
        "MATERIALLY_STRONGER_MECHANISM_ON_CONSTRUCTED_REPRODUCTION iff G1 and G2 and "
        "G3 and G4 all pass"
    ),
    "claim_scope": "CONSTRUCTED_REPRODUCTION_ONLY__DEVELOPMENT_EVIDENCE",
    "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED},
}


def frozen_digest() -> str:
    return sha256_digest(FROZEN_PARAMETERS)


class FreezeViolation(RuntimeError):
    """Raised when the runner's constants no longer match the frozen record."""


def verify_against_twin(repo_root: Path) -> dict[str, Any]:
    """Compare the runner's own parameter digest with the frozen twin's."""

    twin_path = repo_root / FREEZE_TWIN
    if not twin_path.exists():
        raise FreezeViolation(f"freeze twin missing: {twin_path}")
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    recorded = twin.get("parameters_sha256")
    computed = frozen_digest()
    if recorded != computed:
        raise FreezeViolation(
            "runner parameters do not match the frozen record: "
            f"recorded {recorded}, computed {computed}"
        )
    return {"parameters_sha256": computed, "freeze_twin": FREEZE_TWIN}


# --------------------------------------------------------------------------
# World preconditions. Corpus statistics only, evaluated before any query.
# --------------------------------------------------------------------------


def _median(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def world_preconditions(
    world: AcquisitionWorld, index: mech.AcquisitionIndex
) -> dict[str, Any]:
    """Six structural checks, all computed on the corpus and tasks alone.

    None of them runs an arm or looks at an outcome. A world that fails any of
    them is not the constructed reproduction the freeze describes, and the runner
    reports no arm numbers over it.
    """

    scaffold = sorted(
        index.df_fraction(term) for term in world_module.SCAFFOLD_LEXICON
    )
    content = sorted(index.df_fraction(term) for term in world_module.DOMAIN_LEXICON)
    by_id = world.world.by_id

    def terms_of(doc_id: str) -> set[str]:
        document = by_id[doc_id]
        text = f"{document.title} {document.abstract}".lower()
        return set(text.replace(".", " ").split())

    gold_min = min(len(task.gold_doc_ids) for task in world.tasks)
    neighbourhood_min = min(len(task.neighbour_doc_ids) for task in world.tasks)

    coverage_violations: list[str] = []
    apparatus_violations: list[str] = []
    for task in world.tasks_in(FAMILY_DISTINGUISHABLE):
        topic = set(task.content_terms)
        for doc_id in task.gold_doc_ids:
            carried = terms_of(doc_id)
            if len(topic & carried) < world_module.GOLD_TERMS_PER_DOCUMENT:
                coverage_violations.append(doc_id)
            if set(task.scaffold_terms) & carried:
                apparatus_violations.append(doc_id)
        for doc_id in task.neighbour_doc_ids:
            if len(topic & terms_of(doc_id)) > world_module.NEIGHBOUR_TERMS_PER_DOCUMENT:
                coverage_violations.append(doc_id)

    checks = {
        "P1_scaffold_is_high_document_frequency": {
            "min_observed": scaffold[0],
            "median_observed": _median(scaffold),
            "threshold": world_module.MIN_SCAFFOLD_DF_FRACTION,
            "passed": scaffold[0] >= world_module.MIN_SCAFFOLD_DF_FRACTION,
        },
        "P2_content_is_low_document_frequency": {
            "max_observed": content[-1],
            "median_observed": _median(content),
            "threshold": world_module.MAX_CONTENT_DF_FRACTION,
            "passed": content[-1] <= world_module.MAX_CONTENT_DF_FRACTION,
        },
        "P3_every_task_has_multiple_gold": {
            "min_gold_per_task": gold_min,
            "threshold": 2,
            "passed": gold_min >= 2,
        },
        "P4_distinguishable_gold_outcovers_its_neighbourhood": {
            "violations": len(coverage_violations),
            "passed": not coverage_violations,
        },
        "P5_neighbourhood_can_fill_the_result_cap": {
            "min_neighbourhood": neighbourhood_min,
            "threshold": world_module.MIN_NEIGHBOURHOOD_SIZE,
            "passed": neighbourhood_min >= world_module.MIN_NEIGHBOURHOOD_SIZE,
        },
        "P6_distinguishable_gold_carries_no_question_apparatus": {
            "violations": len(apparatus_violations),
            "passed": not apparatus_violations,
        },
    }
    return {
        "documents": index.size,
        "tasks": len(world.tasks),
        "checks": checks,
        "passed": all(item["passed"] for item in checks.values()),
    }


# --------------------------------------------------------------------------
# Campaign
# --------------------------------------------------------------------------


def run_campaign(seed: int = world_module.FROZEN_SEED) -> dict[str, Any]:
    """Build the world, run every arm on every task, evaluate every gate."""

    world = build_acquisition_world(seed)
    index = mech.build_index(world.documents)
    precondition = world_preconditions(world, index)

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P2_OPEN_WORLD_ACQUISITION_RESULT",
        "date": "2026-08-22",
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_sha256": frozen_digest(),
        "claim_scope": "CONSTRUCTED_REPRODUCTION_ONLY__DEVELOPMENT_EVIDENCE",
        "world_content_hash": world.content_hash,
        "world_seed": seed,
        "world_precondition": precondition,
    }

    if not precondition["passed"]:
        payload["verdict"] = "WORLD_PRECONDITION_FAILED"
        payload["interpretation"] = (
            "The generated corpus does not have the structure the freeze specifies, "
            "so it is not a reproduction of the archived acquisition failure. No arm "
            "numbers are reported over it."
        )
        return payload

    scores: dict[str, dict[str, mech.TaskScore]] = {arm: {} for arm in mech.ARM_ORDER}
    runs: dict[str, dict[str, mech.ArmRun]] = {arm: {} for arm in mech.ARM_ORDER}
    for task in world.tasks:
        for arm in mech.ARM_ORDER:
            run = mech.run_arm(arm, task, index)
            runs[arm][task.task_id] = run
            scores[arm][task.task_id] = mech.score_run(run, task.gold_doc_ids)

    by_family: dict[str, dict[str, Any]] = {}
    for family in FAMILY_ORDER:
        task_ids = [task.task_id for task in world.tasks_in(family)]
        by_family[family] = {
            arm: mech.summarize([scores[arm][task_id] for task_id in task_ids])
            for arm in mech.ARM_ORDER
        }
    payload["arms"] = by_family

    def recalls(arm: str, family: str) -> list[float]:
        return [
            scores[arm][task.task_id].recall for task in world.tasks_in(family)
        ]

    main = by_family[FAMILY_DISTINGUISHABLE]
    b0, b1, s2 = main[mech.ARM_B0], main[mech.ARM_B1], main[mech.ARM_S2]

    sign = mech.sign_test_exact(
        recalls(mech.ARM_S2, FAMILY_DISTINGUISHABLE),
        recalls(mech.ARM_B0, FAMILY_DISTINGUISHABLE),
    )
    bootstrap = mech.paired_bootstrap(
        recalls(mech.ARM_S2, FAMILY_DISTINGUISHABLE),
        recalls(mech.ARM_B0, FAMILY_DISTINGUISHABLE),
        resamples=BOOTSTRAP_RESAMPLES,
        seed=BOOTSTRAP_SEED,
    )
    payload["paired_statistics"] = {"sign_test": sign, "bootstrap": bootstrap}

    gain = s2["mean_recall"] - b0["mean_recall"]
    margin = s2["mean_recall"] - b1["mean_recall"]

    g1 = (
        b0["mean_recall"] <= GATES["G1_REPRODUCTION"]["max_baseline_mean_recall"]
        and b0["zero_hit_fraction"]
        >= GATES["G1_REPRODUCTION"]["min_baseline_zero_hit_fraction"]
        and b0["mean_candidates_returned"]
        >= GATES["G1_REPRODUCTION"]["min_baseline_candidates_returned"]
    )
    g2 = (
        gain >= GATES["G2_CANDIDATE"]["min_absolute_gain"]
        and s2["mean_recall"] >= GATES["G2_CANDIDATE"]["min_candidate_mean_recall"]
        and sign["p_value"] < GATES["G2_CANDIDATE"]["max_p_value"]
        and bootstrap["ci_low"]
        > GATES["G2_CANDIDATE"]["require_bootstrap_lower_bound_above"]
    )
    g3 = margin >= GATES["G3_MARGIN_OVER_SHIPPED"]["min_margin"]

    well = by_family[FAMILY_WELL_POSED]
    reference = max(well[mech.ARM_B0]["mean_recall"], well[mech.ARM_B1]["mean_recall"])
    harm_loss = reference - well[mech.ARM_S2]["mean_recall"]
    g4 = harm_loss <= GATES["G4_NO_HARM"]["max_allowed_loss"]
    g4_vacuous = reference < GATES["G4_NO_HARM"]["vacuity_floor"]

    bridge = by_family[FAMILY_NO_BRIDGE]
    bridge_gain = bridge[mech.ARM_S2]["mean_recall"] - bridge[mech.ARM_A3]["mean_recall"]
    g5 = bridge_gain <= GATES["G5_BRIDGE_SPECIFICITY"]["max_allowed_gain"]

    blind = by_family[FAMILY_UNDISTINGUISHED]
    blind_gain = blind[mech.ARM_S2]["mean_recall"] - blind[mech.ARM_B0]["mean_recall"]
    g6 = blind_gain <= GATES["G6_UNDISTINGUISHED_CEILING"]["max_allowed_gain"]

    payload["gate_results"] = {
        "G1_REPRODUCTION": {
            "passed": g1,
            "blocking": True,
            "baseline_mean_recall": b0["mean_recall"],
            "baseline_zero_hit_fraction": b0["zero_hit_fraction"],
            "baseline_mean_candidates_returned": b0["mean_candidates_returned"],
            "archived_reference": GATES["G1_REPRODUCTION"]["reference"],
        },
        "G2_CANDIDATE": {
            "passed": g2,
            "blocking": True,
            "baseline_mean_recall": b0["mean_recall"],
            "candidate_mean_recall": s2["mean_recall"],
            "absolute_gain": gain,
            "sign_test_p_value": sign["p_value"],
            "bootstrap_ci_low": bootstrap["ci_low"],
            "bootstrap_ci_high": bootstrap["ci_high"],
        },
        "G3_MARGIN_OVER_SHIPPED": {
            "passed": g3,
            "blocking": True,
            "shipped_mean_recall": b1["mean_recall"],
            "candidate_mean_recall": s2["mean_recall"],
            "margin": margin,
        },
        "G4_NO_HARM": {
            "passed": g4,
            "blocking": True,
            "vacuous": g4_vacuous,
            "reference_mean_recall_well_posed": reference,
            "candidate_mean_recall_well_posed": well[mech.ARM_S2]["mean_recall"],
            "loss": harm_loss,
        },
        "G5_BRIDGE_SPECIFICITY": {
            "passed": g5,
            "blocking": False,
            "candidate_mean_recall_no_bridge": bridge[mech.ARM_S2]["mean_recall"],
            "no_expansion_mean_recall_no_bridge": bridge[mech.ARM_A3]["mean_recall"],
            "gain": bridge_gain,
        },
        "G6_UNDISTINGUISHED_CEILING": {
            "passed": g6,
            "blocking": False,
            "baseline_mean_recall_undistinguished": blind[mech.ARM_B0]["mean_recall"],
            "candidate_mean_recall_undistinguished": blind[mech.ARM_S2]["mean_recall"],
            "gain": blind_gain,
        },
    }

    if not g1:
        verdict = "REPRODUCTION_FAILED__NO_CANDIDATE_CLAIM"
    elif g2 and g3 and g4:
        verdict = "MATERIALLY_STRONGER_MECHANISM_ON_CONSTRUCTED_REPRODUCTION"
    elif g2 and g4 and not g3:
        verdict = "GAIN_OVER_ARCHIVED_BASELINE_ONLY__NOT_MARGINAL_OVER_SHIPPED"
    elif g2 and not g4:
        verdict = "GAIN_ON_MODE__HARM_OFF_MODE__NO_CANDIDATE_CLAIM"
    else:
        verdict = "CANDIDATE_NOT_VALIDATED__NEGATIVE_STANDS"
    payload["verdict"] = verdict

    payload["variant_gap_summary"] = {
        "candidate_mean_recall": by_family[FAMILY_VARIANT_GAP][mech.ARM_S2]["mean_recall"],
        "no_expansion_mean_recall": by_family[FAMILY_VARIANT_GAP][mech.ARM_A3][
            "mean_recall"
        ],
        "expansion_contribution": (
            by_family[FAMILY_VARIANT_GAP][mech.ARM_S2]["mean_recall"]
            - by_family[FAMILY_VARIANT_GAP][mech.ARM_A3]["mean_recall"]
        ),
        "note": (
            "Descriptive. variant_gap enters no blocking gate; its paired control is "
            "no_bridge under G5."
        ),
    }
    payload["example_tasks"] = _example_tasks(world, index, runs, scores)
    payload["not_licensed"] = [
        "any statement about mean recall on the official AutoResearchBench Wide benchmark",
        "reopening or revising P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18",
        "promotion of L1 P2_EXTERNAL_MECHANISM_SUPPORTED or L2 P2_EXTERNAL_DISCOVERY_SUPPORTED",
        "any claim that D5 was executed against arXiv, OpenAlex or OpenAIRE",
        "any change to the authorized scientific terminal P2_NARROWED",
    ]
    return payload


def _example_tasks(
    world: AcquisitionWorld,
    index: mech.AcquisitionIndex,
    runs: dict[str, dict[str, mech.ArmRun]],
    scores: dict[str, dict[str, mech.TaskScore]],
) -> list[dict[str, Any]]:
    """Worked cases, so a reader can see the mechanism rather than a number."""

    examples: list[dict[str, Any]] = []
    for task in world.tasks_in(FAMILY_DISTINGUISHABLE)[:3]:
        baseline = runs[mech.ARM_B0][task.task_id]
        candidate = runs[mech.ARM_S2][task.task_id]
        by_id = world.world.by_id
        examples.append(
            {
                "task_id": task.task_id,
                "question": task.question,
                "content_terms": list(task.content_terms),
                "scaffold_terms": list(task.scaffold_terms),
                "gold_count": len(task.gold_doc_ids),
                "baseline_queries": [q.rendered() for q in baseline.queries],
                "baseline_top_titles": [
                    by_id[d].title for d in baseline.candidates[:5]
                ],
                "baseline_recall": scores[mech.ARM_B0][task.task_id].recall,
                "candidate_queries": [q.rendered() for q in candidate.queries],
                "candidate_top_titles": [
                    by_id[d].title for d in candidate.candidates[:5]
                ],
                "candidate_recall": scores[mech.ARM_S2][task.task_id].recall,
                "scaffold_df_fractions": {
                    term: index.df_fraction(term) for term in task.scaffold_terms
                },
                "content_df_fractions": {
                    term: index.df_fraction(term) for term in task.content_terms
                },
            }
        )
    return examples


def main(argv: list[str]) -> int:
    """CLI entry point. `argv` is required: there is no implicit run."""

    parser = argparse.ArgumentParser(
        prog="orion-p2-acquisition-successor",
        description=(
            "Run the frozen open-world acquisition successor study on its "
            "constructed world and write the result artifact."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the runner's frozen parameter digest and exit without running",
    )
    args = parser.parse_args(argv)

    if args.print_digest:
        print(frozen_digest())
        return 0

    repo_root: Path = args.repo_root
    provenance = verify_against_twin(repo_root)

    payload = run_campaign()
    payload["freeze_provenance"] = provenance

    output = args.output or (repo_root / DEFAULT_OUTPUT)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"verdict: {payload['verdict']}")
    print(f"written: {output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
