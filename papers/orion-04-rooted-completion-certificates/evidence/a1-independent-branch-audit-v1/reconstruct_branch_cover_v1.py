#!/usr/bin/env python3
"""Independent A1 reconstruction of ORION-04's support-14..31 branch cover.

Generation is deliberately separated from comparison. The reconstruction below
uses only the mathematical premises stated in the manuscript: multiplicities
{1,2,4}, the length/support equations, eta(C_5^2)=13, the projective-line local
restriction, and the rank/plane case split. It does not import ORION generators,
C engines, branch tables, fingerprints, or expected branch counts.

Only after the branch set has been generated do ``compare_with_committed`` and the
mutation controls read the checked-in JSON artifacts.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Iterable

SCHEMA = "ORION04.A1.IndependentBranchProofAudit.v1"
TOTAL_LENGTH = 31
SUPPORT_FLOOR = 14
ETA_C5_SQUARED = 13
LINE_MULTIPLICITIES = (0, 1, 2, 4)

# Audit-local names, intentionally different from the production cover labels.
COMMITTED_TO_AUDIT = {
    "MIXED_RANK3": "L.HIGH_SET_RANK3",
    "HIGH4_RANK3": "L.FOUR_SET_RANK3",
    "HIGH4_RANK2_OUTSIDE": "L.THREE_FOURS_PLANE_PLUS_OUTSIDE",
    "HIGH_RANK3": "U.HIGH_SET_RANK3",
    "HIGH_RANK2_SINGLETON_OUTSIDE": "U.HIGH_SET_PLANE_PLUS_SINGLETON",
    "ONE_HIGH_FULL_BASIS": "U.ONE_HIGH_PLUS_TWO_SINGLETONS",
    "ALL_SINGLETON_FULL_BASIS": "U.ALL_SINGLETON_BASIS",
}


def _pattern_key(row: dict) -> tuple[int, int, int, int]:
    return (row["support"], row["a1"], row["b2"], row["c4"])


def _branch_key(row: dict) -> tuple[int, int, int, int, str]:
    return (*_pattern_key(row), row["audit_case"])


def enumerate_patterns(
    total_length: int = TOTAL_LENGTH,
    support_floor: int = SUPPORT_FLOOR,
    support_ceiling: int | None = None,
) -> list[dict]:
    """Solve a1 + 2*b2 + 4*c4 = total_length exactly over nonnegative integers."""
    if support_ceiling is None:
        support_ceiling = total_length
    rows: list[dict] = []
    for c4 in range(total_length // 4 + 1):
        for b2 in range((total_length - 4 * c4) // 2 + 1):
            a1 = total_length - 2 * b2 - 4 * c4
            if a1 < 0:
                continue
            support = a1 + b2 + c4
            if support_floor <= support <= support_ceiling:
                rows.append({"support": support, "a1": a1, "b2": b2, "c4": c4})
    return sorted(rows, key=_pattern_key)


def _contains_short_zero_sum_on_projective_line(counts: tuple[int, int, int, int]) -> bool:
    """Primitive Z/5 check on the nonzero line points x,2x,3x,4x.

    A choice (t1,t2,t3,t4) is a short zero sum exactly when its size is 1..5 and
    t1 + 2*t2 + 3*t3 + 4*t4 == 0 mod 5.
    """
    ranges = [range(m + 1) for m in counts]
    for take in itertools.product(*ranges):
        weight = sum(take)
        if not 1 <= weight <= 5:
            continue
        residue = sum((i + 1) * take[i] for i in range(4)) % 5
        if residue == 0:
            return True
    return False


def reconstruct_projective_line_states() -> list[list[int]]:
    states = [
        list(counts)
        for counts in itertools.product(LINE_MULTIPLICITIES, repeat=4)
        if not _contains_short_zero_sum_on_projective_line(counts)
    ]
    return sorted(states)


def projective_line_consequences(states: Iterable[Iterable[int]]) -> dict:
    rows = [tuple(row) for row in states]
    mult4_isolated = all(
        sum(value > 0 for value in row) == 1
        for row in rows
        if 4 in row
    )
    two_mult2_collinear_forbidden = all(sum(value >= 2 for value in row) <= 1 for row in rows)
    return {
        "mult4_isolated": mult4_isolated,
        "two_mult2_collinear_forbidden": two_mult2_collinear_forbidden,
        "high_points_pairwise_projectively_distinct": (
            mult4_isolated and two_mult2_collinear_forbidden
        ),
    }


def derive_lower_branches(patterns: Iterable[dict], *, plane_split: bool = True) -> list[dict]:
    """Reconstruct supports 14..22 from mass/rank consequences of eta(C5^2)=13."""
    rows: list[dict] = []
    for p in patterns:
        s, b2, c4 = p["support"], p["b2"], p["c4"]
        if not 14 <= s <= 22:
            continue
        high_mass = 2 * b2 + 4 * c4

        if c4 <= 2:
            # Every such pattern has at least eta mass among multiplicity >=2 points.
            # Were those points rank <=2, eta(C5^2)=13 would force a short zero sum.
            if high_mass < ETA_C5_SQUARED:
                raise AssertionError("lower high-set rank forcing premise failed")
            rows.append({**p, "audit_case": "L.HIGH_SET_RANK3"})
        elif c4 == 3:
            # The three 4-points alone have mass 12, just below eta, so their rank
            # genuinely splits. Rank 3 gives a basis. Rank 2 puts them in a plane;
            # any 2-point in that plane would raise plane mass to 14 and contradict
            # eta, so an outside support point supplies the third basis direction.
            rows.append({**p, "audit_case": "L.FOUR_SET_RANK3"})
            if plane_split:
                rows.append({**p, "audit_case": "L.THREE_FOURS_PLANE_PLUS_OUTSIDE"})
        else:
            # Four or more multiplicity-4 points already contribute >=16 terms.
            # Their span therefore cannot have rank <=2.
            if 4 * c4 < ETA_C5_SQUARED:
                raise AssertionError("lower four-set rank forcing premise failed")
            rows.append({**p, "audit_case": "L.FOUR_SET_RANK3"})
    return sorted(rows, key=_branch_key)


def derive_upper_branches(patterns: Iterable[dict], *, eta: int = ETA_C5_SQUARED) -> list[dict]:
    """Reconstruct supports 23..31 by rank of H = {points of multiplicity >1}."""
    rows: list[dict] = []
    for p in patterns:
        s, b2, c4 = p["support"], p["b2"], p["c4"]
        if not 23 <= s <= 31:
            continue
        high_points = b2 + c4
        high_mass = 2 * b2 + 4 * c4

        if high_points >= 3:
            # rank(H)=3 case; pairwise projective distinctness makes a high basis
            # available. Because c4<=2 in this support range, the basis profiles are
            # (2,2,2), (4,2,2), or (4,4,2).
            rows.append({**p, "audit_case": "U.HIGH_SET_RANK3"})
            # rank(H)=2 is possible only while the whole high subsequence stays below
            # eta; otherwise it would already contain a short zero sum in its plane.
            if high_mass < eta:
                rows.append({**p, "audit_case": "U.HIGH_SET_PLANE_PLUS_SINGLETON"})
        elif high_points == 2:
            # The two high points are projectively distinct, hence span a plane.
            if high_mass >= eta:
                raise AssertionError("two-high upper pattern unexpectedly reaches eta")
            rows.append({**p, "audit_case": "U.HIGH_SET_PLANE_PLUS_SINGLETON"})
        elif high_points == 1:
            rows.append({**p, "audit_case": "U.ONE_HIGH_PLUS_TWO_SINGLETONS"})
        else:
            rows.append({**p, "audit_case": "U.ALL_SINGLETON_BASIS"})
    return sorted(rows, key=_branch_key)


def reconstruct() -> dict:
    patterns = enumerate_patterns()
    line_states = reconstruct_projective_line_states()
    line_rules = projective_line_consequences(line_states)
    if not all(line_rules.values()):
        raise AssertionError("primitive projective-line consequences did not follow")
    lower = derive_lower_branches(patterns)
    upper = derive_upper_branches(patterns)
    return {
        "patterns": patterns,
        "line_states": line_states,
        "line_rules": line_rules,
        "lower_branches": lower,
        "upper_branches": upper,
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_with_committed(reconstruction: dict, repo_root: Path) -> dict:
    """Compare only after generation; committed artifacts never feed reconstruction."""
    evidence = repo_root / "papers/orion-04-rooted-completion-certificates/evidence/global-obstruction-v1"
    cover_path = evidence / "FULL_CUBE_COVER.json"
    atlas_path = evidence / "PROJECTIVE_LINE_ATLAS.json"
    cover = _load_json(cover_path)
    atlas = _load_json(atlas_path)

    generated_patterns = {_pattern_key(row) for row in reconstruction["patterns"]}
    committed_patterns = {
        _pattern_key(row)
        for row in [*cover["lower_patterns"], *cover["upper_patterns"]]
    }

    generated_branches = {
        _branch_key(row)
        for row in [*reconstruction["lower_branches"], *reconstruction["upper_branches"]]
    }
    committed_branches = set()
    unknown_labels = set()
    for row in [*cover["lower_branches"], *cover["upper_branches"]]:
        label = COMMITTED_TO_AUDIT.get(row["branch"])
        if label is None:
            unknown_labels.add(row["branch"])
            continue
        committed_branches.add((*_pattern_key(row), label))

    generated_states = {tuple(row) for row in reconstruction["line_states"]}
    committed_states = {tuple(row) for row in atlas["states"]}

    return {
        "cover_path": str(cover_path.relative_to(repo_root)),
        "atlas_path": str(atlas_path.relative_to(repo_root)),
        "generated_pattern_count": len(generated_patterns),
        "committed_pattern_count": len(committed_patterns),
        "patterns_exact": generated_patterns == committed_patterns,
        "generated_lower_branch_count": len(reconstruction["lower_branches"]),
        "generated_upper_branch_count": len(reconstruction["upper_branches"]),
        "generated_branch_count": len(generated_branches),
        "committed_branch_count": len(committed_branches),
        "unknown_committed_labels": sorted(unknown_labels),
        "branches_exact": not unknown_labels and generated_branches == committed_branches,
        "generated_line_state_count": len(generated_states),
        "committed_line_state_count": len(committed_states),
        "line_states_exact": generated_states == committed_states,
        "missing_patterns": sorted(committed_patterns - generated_patterns),
        "extra_patterns": sorted(generated_patterns - committed_patterns),
        "missing_branches": sorted(committed_branches - generated_branches),
        "extra_branches": sorted(generated_branches - committed_branches),
        "missing_line_states": sorted(committed_states - generated_states),
        "extra_line_states": sorted(generated_states - committed_states),
    }


def mutation_controls(reconstruction: dict, comparison: dict) -> dict:
    baseline_branches = [*reconstruction["lower_branches"], *reconstruction["upper_branches"]]
    committed_count = comparison["committed_branch_count"]

    omitted = baseline_branches[1:]
    no_lower_plane = [
        *derive_lower_branches(reconstruction["patterns"], plane_split=False),
        *derive_upper_branches(reconstruction["patterns"]),
    ]
    eta15 = [
        *derive_lower_branches(reconstruction["patterns"]),
        *derive_upper_branches(reconstruction["patterns"], eta=15),
    ]
    total30 = enumerate_patterns(total_length=30, support_floor=SUPPORT_FLOOR, support_ceiling=30)

    controls = {
        "omitted_one_branch": {
            "mutated_branch_count": len(omitted),
            "rejected": len(omitted) != committed_count,
        },
        "altered_multiplicity_equation_total_30": {
            "mutated_pattern_count": len(total30),
            "rejected": len(total30) != comparison["committed_pattern_count"],
        },
        "altered_rank_condition_drop_c4_eq_3_plane_split": {
            "mutated_branch_count": len(no_lower_plane),
            "rejected": len(no_lower_plane) != committed_count,
        },
        "altered_eta_threshold_15": {
            "mutated_branch_count": len(eta15),
            "rejected": len(eta15) != committed_count,
        },
    }
    controls["all_rejected"] = all(row["rejected"] for row in controls.values())
    return controls


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    # .../repo/papers/orion-04.../evidence/a1-independent-branch-audit-v1/script.py
    return here.parents[4]


def build_report(repo_root: Path | None = None) -> dict:
    reconstruction = reconstruct()
    counts = {
        "patterns": len(reconstruction["patterns"]),
        "patterns_support_14_22": sum(14 <= p["support"] <= 22 for p in reconstruction["patterns"]),
        "patterns_support_23_31": sum(23 <= p["support"] <= 31 for p in reconstruction["patterns"]),
        "projective_line_states": len(reconstruction["line_states"]),
        "branches_support_14_22": len(reconstruction["lower_branches"]),
        "branches_support_23_31": len(reconstruction["upper_branches"]),
        "branches_total": len(reconstruction["lower_branches"]) + len(reconstruction["upper_branches"]),
    }
    report = {
        "schema": SCHEMA,
        "status": "DERIVED__COMPARISON_NOT_RUN",
        "method": "equation + primitive projective-line enumeration + eta/rank case analysis",
        "generation_does_not_import": [
            "current branch list",
            "current C engines",
            "current fingerprints",
            "current generator output",
        ],
        "counts": counts,
        "projective_line_consequences": reconstruction["line_rules"],
        "d4_target_execution_performed_by_this_audit": False,
        "external_peer_review_authority": False,
        "scientific_authority_delta": "NONE",
        "limitations": [
            "This reconstructs the finite cover, not the zero-survivor search result.",
            "It does not supply external/human peer-review authority.",
            "It does not test the separate forged-zero-solution-digest mutation control.",
        ],
    }
    if repo_root is not None:
        comparison = compare_with_committed(reconstruction, repo_root)
        mutations = mutation_controls(reconstruction, comparison)
        all_match = (
            comparison["patterns_exact"]
            and comparison["branches_exact"]
            and comparison["line_states_exact"]
        )
        report["comparison_to_committed"] = comparison
        report["mutation_controls"] = mutations
        report["status"] = (
            "PASS__INDEPENDENT_COVER_RECONSTRUCTION_MATCHES_COMMITTED"
            if all_match and mutations["all_rejected"]
            else "FAIL_CLOSED__RECONSTRUCTION_OR_MUTATION_MISMATCH"
        )
    return report


def main() -> int:
    root = _repo_root()
    report = build_report(root)
    out = Path(__file__).with_name("BRANCH_RECONSTRUCTION_RESULT_V1.json")
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "counts": report["counts"],
        "comparison": report.get("comparison_to_committed"),
        "mutation_controls": report.get("mutation_controls"),
    }, indent=2, sort_keys=True))
    return 0 if report["status"].startswith("PASS__") else 1


if __name__ == "__main__":
    raise SystemExit(main())
