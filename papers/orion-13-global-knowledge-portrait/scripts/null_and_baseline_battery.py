#!/usr/bin/env python3
"""Null-and-baseline battery for the ORION-13 confirmatory mapping result.

The published confirmatory claim is a paired comparison on a frozen 32-case
public-reference holdout: coordinate-governed mapping false-merges 0.0 where flat
predicate canonicalization false-merges 0.1875, paired difference -0.1875, 95%
percentile bootstrap interval [-0.34375, -0.0625].

That comparison is real but it is reported without the context a referee needs to
size it. This battery computes four things the manuscript did not report, all from
committed artifacts and the committed deterministic mechanism:

B1  Reproduction check. Recompute per-item predictions for all three systems and
    assert the published aggregate rates reproduce exactly. Every later item is
    void if this fails, so it is checked first and hard-fails.

B2  Baseline degeneracy. `flat_predicate_baseline` returns COMPATIBLE iff the two
    projections share a predicate. Census how many of the holdout's cases are
    predicate-equal. If all of them are, flat is a constant "always merge"
    predictor on this corpus and its false-merge rate is identically the base rate
    of non-mergeable cases -- a quantity that carries no information about the
    baseline's design.

B3  Discordance and exact test. The paired bootstrap interval is computed over a
    difference vector that is mostly zeros. Report the McNemar discordance counts
    and the exact two-sided test, which states how many cases actually separate
    the two systems.

B4  Coordinate-sufficiency census. `compare_meaning` consults ten coordinates in a
    fixed cascade. For each branch, count how many of the holdout's cases it
    actually decides. A branch that never fires cannot be supported by this
    corpus. Then evaluate the minimal rule using only the branches that do fire.

The battery adds analysis. It changes no threshold, no comparator, no corpus and
no success gate, and it does not alter any committed result.

Usage::

    .venv/bin/python papers/orion-13-global-knowledge-portrait/scripts/null_and_baseline_battery.py

Writes ``evidence/null-and-baseline-battery-v1/BATTERY_V1.json``.
"""

from __future__ import annotations

import json
import os
import sys
from math import comb
from pathlib import Path

PAPER = Path(os.environ.get("ORION13_PAPER_DIR", Path(__file__).resolve().parents[1]))
REPO = PAPER.parents[1]
# Output root, overridable so the battery can be regenerated without writing into a
# checkout shared with other processes. Defaults to the paper directory.
OUT = Path(os.environ.get("ORION13_OUT_DIR", PAPER))
sys.path.insert(0, str(REPO / "src"))

from orion.knowledge.semantics import (  # noqa: E402
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
)
from orion.study.p3_public_reference import (  # noqa: E402
    evaluate_case,
    exact_coordinate_baseline,
    flat_predicate_baseline,
    projection_from_dict,
)

GOLD_SETS = {
    "confirmatory": PAPER
    / "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl",
    "initial": PAPER / "gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl",
}

# Published aggregates to reproduce (from evidence/public-reference-v1.1-confirmatory/
# CONFIRMATORY_ANALYSIS.json, pooled). B1 hard-fails if these do not reproduce.
PUBLISHED_CONFIRMATORY = {
    "orion": {"false_merge_rate": 0.0, "abstention_rate": 0.0},
    "flat_predicate_canonicalization": {"false_merge_rate": 0.1875, "abstention_rate": 0.0},
    "exact_coordinate_conservative": {"false_merge_rate": 0.0, "abstention_rate": 0.1875},
}

# The cascade order in orion.knowledge.semantics.compare_meaning. This is the
# mechanism's own order of consultation, fixed before any outcome was seen; it is
# not a post-hoc ordering chosen to produce a result.
CASCADE = [
    "unresolved_ambiguities",
    "predicate",
    "referent_ids",
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
    "attribution_id",
    "discourse_relation",
    "assumption_ids",
    "modality",
    "polarity",
]


def _same_or_empty(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    return not left or not right or left == right


def deciding_branch(left: ScientificMeaningProjection, right: ScientificMeaningProjection) -> str:
    """Return the cascade branch that decides this pair, mirroring compare_meaning.

    Kept structurally parallel to the mechanism so that a divergence shows up as a
    reproduction failure in B1 rather than passing silently.
    """
    if left.unresolved_ambiguities or right.unresolved_ambiguities:
        return "unresolved_ambiguities"
    if left.predicate != right.predicate:
        return "predicate"
    if left.referent_ids and right.referent_ids and left.referent_ids != right.referent_ids:
        return "referent_ids"
    if left.construct_ids and right.construct_ids and left.construct_ids != right.construct_ids:
        return "construct_ids"
    if (
        left.measurement_ids
        and right.measurement_ids
        and left.measurement_ids != right.measurement_ids
    ):
        return "measurement_ids"
    # The contextual block is evaluated as a group by the mechanism; report the
    # first contributing coordinate so the census is per-coordinate.
    if not _same_or_empty(left.temporal_context_ids, right.temporal_context_ids):
        return "temporal_context_ids"
    if left.attribution_id and right.attribution_id and left.attribution_id != right.attribution_id:
        return "attribution_id"
    if (
        left.discourse_relation
        and right.discourse_relation
        and left.discourse_relation != right.discourse_relation
    ):
        return "discourse_relation"
    if left.assumption_ids and right.assumption_ids and left.assumption_ids != right.assumption_ids:
        return "assumption_ids"
    if left.modality != right.modality:
        return "modality"
    if (
        left.polarity is not Polarity.UNKNOWN
        and right.polarity is not Polarity.UNKNOWN
        and left.polarity != right.polarity
    ):
        return "polarity"
    return "fallthrough_compatible"


def minimal_rule(case: dict) -> MeaningRelation:
    """Predicate + modality + polarity only. Drops the seven identity/context coordinates.

    This is the falsifying comparator for the coordinate-governance claim: if it
    matches the full mechanism on the holdout, the remaining coordinates are not
    supported by this corpus.
    """
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    if left.unresolved_ambiguities or right.unresolved_ambiguities:
        return MeaningRelation.UNRESOLVED
    if left.predicate != right.predicate:
        return MeaningRelation.UNRESOLVED
    if left.modality != right.modality:
        return MeaningRelation.CONTEXTUAL_DIFFERENCE
    if (
        left.polarity is not Polarity.UNKNOWN
        and right.polarity is not Polarity.UNKNOWN
        and left.polarity != right.polarity
    ):
        if left.modality is Modality.ASSERTED and right.modality is Modality.ASSERTED:
            return MeaningRelation.CONTRADICTORY
        return MeaningRelation.CONTEXTUAL_DIFFERENCE
    return MeaningRelation.COMPATIBLE


def rates(expected: list[MeaningRelation], predicted: list[MeaningRelation]) -> dict[str, float]:
    n = len(expected)
    merge_like = MeaningRelation.COMPATIBLE
    false_merge = sum(
        1 for g, p in zip(expected, predicted) if p is merge_like and g is not merge_like
    )
    false_split = sum(
        1
        for g, p in zip(expected, predicted)
        if g is merge_like and p is not merge_like and p is not MeaningRelation.UNRESOLVED
    )
    abstain = sum(1 for p in predicted if p is MeaningRelation.UNRESOLVED)
    correct = sum(1 for g, p in zip(expected, predicted) if g is p)
    return {
        "accuracy": correct / n,
        "false_merge_rate": false_merge / n,
        "false_split_rate": false_split / n,
        "abstention_rate": abstain / n,
        "n": n,
    }


def exact_mcnemar_two_sided(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value over the b+c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


TABLE_TARGET = OUT / "manuscript" / "tables" / "coordinate_branch_census.tex"

# Human-readable coordinate names, short enough for a plain booktabs tabular
# (this manuscript does not load tabularx).
BRANCH_LABEL = {
    "unresolved_ambiguities": "unresolved ambiguity gate",
    "predicate": "predicate",
    "referent_ids": "referent",
    "construct_ids": "construct",
    "measurement_ids": "measurement",
    "temporal_context_ids": "temporal context",
    "attribution_id": "attribution",
    "discourse_relation": "discourse relation",
    "assumption_ids": "assumption context",
    "modality": "modality",
    "polarity": "polarity",
    "fallthrough_compatible": "no branch fired (compatible)",
}


def emit_table(out: dict) -> None:
    conf = out["sets"]["confirmatory"]
    init = out["sets"]["initial"]
    cc, ci = conf["cascade_branch_census"], init["cascade_branch_census"]
    lines = [
        "% Generated by papers/orion-13-global-knowledge-portrait/scripts/"
        "null_and_baseline_battery.py",
        "% Source: evidence/null-and-baseline-battery-v1/BATTERY_V1.json. Do not edit by hand.",
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Which comparison coordinates the two public-reference holdouts actually "
        "exercise. Each cell counts the cases decided by that branch of the "
        "\\texttt{compare\\_meaning} cascade, in the mechanism's own order of consultation. "
        "Nine of the ten coordinates never differ between the two projections in either "
        "holdout, so they decide no case. This is a statement "
        "about the coverage of these corpora, not evidence that the coordinates are "
        "dispensable in general.}",
        "  \\label{tab:coordinate-branch-census}",
        "  \\small",
        "  \\begin{tabular}{lcc}",
        "    \\toprule",
        "    Coordinate branch & Confirmatory ($n=32$) & Initial ($n=32$) \\\\",
        "    \\midrule",
    ]
    for key in CASCADE + ["fallthrough_compatible"]:
        lines.append(f"    {BRANCH_LABEL[key]} & {cc[key]} & {ci[key]} \\\\")
    lines += [
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
    ]
    TABLE_TARGET.parent.mkdir(parents=True, exist_ok=True)
    TABLE_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")

def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def analyze(name: str, cases: list[dict]) -> dict:
    expected = [MeaningRelation(c["expected"]["meaning_relation"]) for c in cases]
    orion = [MeaningRelation(evaluate_case(c).predicted) for c in cases]
    flat = [flat_predicate_baseline(c) for c in cases]
    exact = [exact_coordinate_baseline(c) for c in cases]
    minimal = [minimal_rule(c) for c in cases]

    # B2: baseline degeneracy census.
    pairs = [
        (projection_from_dict(c["left_projection"]), projection_from_dict(c["right_projection"]))
        for c in cases
    ]
    predicate_equal = sum(1 for lft, rgt in pairs if lft.predicate == rgt.predicate)
    flat_always_merge = all(p is MeaningRelation.COMPATIBLE for p in flat)
    non_merge_base_rate = sum(1 for g in expected if g is not MeaningRelation.COMPATIBLE) / len(cases)

    # B3: discordance on the headline metric (false merge), orion vs flat.
    def is_false_merge(g: MeaningRelation, p: MeaningRelation) -> bool:
        return p is MeaningRelation.COMPATIBLE and g is not MeaningRelation.COMPATIBLE

    b = sum(
        1
        for g, o, f in zip(expected, orion, flat)
        if is_false_merge(g, f) and not is_false_merge(g, o)
    )
    c_ = sum(
        1
        for g, o, f in zip(expected, orion, flat)
        if is_false_merge(g, o) and not is_false_merge(g, f)
    )
    concordant = len(cases) - b - c_

    # B4: which cascade branches ever decide a case.
    census: dict[str, int] = {key: 0 for key in CASCADE}
    census["fallthrough_compatible"] = 0
    for lft, rgt in pairs:
        census[deciding_branch(lft, rgt)] += 1
    never_fires = [k for k in CASCADE if census[k] == 0]

    return {
        "case_count": len(cases),
        "systems": {
            "orion": rates(expected, orion),
            "flat_predicate_canonicalization": rates(expected, flat),
            "exact_coordinate_conservative": rates(expected, exact),
            "minimal_predicate_modality_polarity": rates(expected, minimal),
        },
        "baseline_degeneracy": {
            "predicate_equal_cases": predicate_equal,
            "predicate_equal_fraction": predicate_equal / len(cases),
            "flat_is_constant_always_merge": flat_always_merge,
            "non_merge_base_rate": non_merge_base_rate,
            "flat_false_merge_equals_base_rate": abs(
                rates(expected, flat)["false_merge_rate"] - non_merge_base_rate
            )
            < 1e-12,
        },
        "discordance_orion_vs_flat_false_merge": {
            "b_flat_only_false_merge": b,
            "c_orion_only_false_merge": c_,
            "concordant": concordant,
            "exact_mcnemar_two_sided_p": exact_mcnemar_two_sided(b, c_),
        },
        "cascade_branch_census": census,
        "coordinates_that_never_differ": never_fires,
        "minimal_rule_matches_full_mechanism": minimal == orion,
    }


def main() -> int:
    out: dict[str, object] = {
        "schema": "ORION.P3.NullAndBaselineBattery.v1",
        "scientific_authority_delta": "NONE",
        "purpose": (
            "Reports the baseline degeneracy, discordance count, and coordinate "
            "sufficiency behind the published confirmatory mapping comparison. "
            "Adds analysis only; changes no threshold, comparator, corpus or gate."
        ),
        "sets": {},
    }

    for name, path in GOLD_SETS.items():
        out["sets"][name] = analyze(name, load(path))  # type: ignore[index]

    # Directional consistency across the two disjoint holdouts.
    #
    # NO POOLED SIGNIFICANCE FIGURE IS COMPUTED HERE, deliberately. The paper's own
    # confirmatory protocol states that the strata are "reported descriptively and
    # not pooled with the initial 32 cases to inflate the confirmatory sample size"
    # (manuscript/sections/06-results.tex). Computing a pooled exact test over the
    # 64 cases would do exactly what that sentence declines to do, whichever figure
    # were reported first. What is recorded instead is a replication observation:
    # whether every discordant pair across both frozen holdouts falls the same way.
    # That is a statement about direction, not about sample size, and needs no
    # p-value to stand.
    total_b = sum(
        out["sets"][s_]["discordance_orion_vs_flat_false_merge"]["b_flat_only_false_merge"]  # type: ignore[index]
        for s_ in GOLD_SETS
    )
    total_c = sum(
        out["sets"][s_]["discordance_orion_vs_flat_false_merge"]["c_orion_only_false_merge"]  # type: ignore[index]
        for s_ in GOLD_SETS
    )
    out["directional_consistency_across_holdouts"] = {
        "sets": sorted(GOLD_SETS),
        "disjoint": True,
        "disjointness_source": (
            "evidence/coordinate-obstruction-v2/PHASE_A_VERIFICATION.json "
            "(case_id_overlap_count: 0)"
        ),
        "discordant_pairs_total": total_b + total_c,
        "favouring_coordinate_governed": total_b,
        "favouring_flat": total_c,
        "all_discordant_pairs_same_direction": total_c == 0,
        "pooled_significance_test": "NOT_COMPUTED_BY_PROTOCOL",
        "note": (
            "Per-set exact tests are the significance evidence: confirmatory p=0.031, "
            "initial p=0.125 (not significant alone). This block reports only that the "
            "discordant pairs agree in direction across two disjoint frozen holdouts. "
            "It is not a confirmatory sample-size claim and must not be read as one."
        ),
    }

    # B1: hard reproduction check against the published confirmatory aggregates.
    conf = out["sets"]["confirmatory"]["systems"]  # type: ignore[index]
    failures = []
    for system, expect in PUBLISHED_CONFIRMATORY.items():
        for metric, want in expect.items():
            got = conf[system][metric]
            if abs(got - want) > 1e-12:
                failures.append(f"{system}.{metric}: published {want}, recomputed {got}")
    out["reproduction_check"] = {
        "published_source": "evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json",
        "status": "REPRODUCED" if not failures else "FAILED",
        "mismatches": failures,
    }
    if failures:
        print("REPRODUCTION FAILED -- battery is void:", file=sys.stderr)
        for line in failures:
            print("  " + line, file=sys.stderr)
        return 1

    target_dir = OUT / "evidence" / "null-and-baseline-battery-v1"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "BATTERY_V1.json"
    target.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    emit_table(out)

    conf_set = out["sets"]["confirmatory"]  # type: ignore[index]
    deg = conf_set["baseline_degeneracy"]
    dis = conf_set["discordance_orion_vs_flat_false_merge"]
    try:
        shown = target.relative_to(REPO)
    except ValueError:
        shown = target
    print(f"wrote {shown}")
    print(f"B1 reproduction: {out['reproduction_check']['status']}")
    print(
        f"B2 predicate-equal {deg['predicate_equal_cases']}/{conf_set['case_count']}; "
        f"flat constant always-merge = {deg['flat_is_constant_always_merge']}; "
        f"flat FM == non-merge base rate = {deg['flat_false_merge_equals_base_rate']}"
    )
    print(
        f"B3 discordance b={dis['b_flat_only_false_merge']} c={dis['c_orion_only_false_merge']} "
        f"concordant={dis['concordant']} exact two-sided p={dis['exact_mcnemar_two_sided_p']:.5f}"
    )
    print(f"B4 coordinates that never differ: {conf_set['coordinates_that_never_differ']}")
    dc = out["directional_consistency_across_holdouts"]
    print(
        f"DIRECTION across disjoint holdouts: {dc['favouring_coordinate_governed']}"
        f"/{dc['discordant_pairs_total']} discordant pairs favour coordinate-governed; "
        f"same direction = {dc['all_discordant_pairs_same_direction']}; "
        f"pooled significance = {dc['pooled_significance_test']}"
    )
    print(
        f"B4 minimal rule accuracy: "
        f"{conf_set['systems']['minimal_predicate_modality_polarity']['accuracy']:.4f}; "
        f"matches full mechanism = {conf_set['minimal_rule_matches_full_mechanism']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
