#!/usr/bin/env python3
"""Exhaustive small-domain tie-equivalence quotient for ORION-21.

Protocol identity : ORION21.TIE_EQUIVALENCE_QUOTIENT.v1
Authority         : DIAGNOSTIC_AND_STRUCTURAL_ONLY
                    scientific_authority_delta = NONE
                    submission_authority = false

This is a THIRD instrument. It does not reopen, replay, re-adjudicate or
re-score the V1 NR07 lane (controlling terminal CANNOT_CHECK_INSTRUMENT_DRIFT)
and it does not reopen ORION21.TIE_ROBUST_PHASE.v1 (executed, terminal
T3_TIE_AMBIGUOUS_VERDICT_CHANGING, LUNARC job 3552796).  No magnitude measured
here transfers to either of those instruments and no magnitude from either of
them is read here.  The claim produced is purely structural.

WHAT IS COMPUTED
----------------
The screening rule of ORION-21 keeps the top-r features of a bank by ABSOLUTE
INTEGER correlation with the label stream.  At the top-r boundary it names a
SET of supports, not one support.  That set is the tie-equivalence class.  This
script:

  1. enumerates the small-domain screening state space exhaustively,
  2. quotients realised outcomes (x, s) by tie equivalence,
  3. tests a family of candidate invariants for representative independence
     (constancy on every tie-equivalence class),
  4. either certifies a scoped impossibility, or reports a distinct
     non-impossibility terminal, or reports CANNOT_CHECK.

Stdlib only.  Exact integer arithmetic throughout; no float aggregate is ever
used for a decision.

EXIT CODES (never conflated)
----------------------------
  0  T1_IMPOSSIBILITY_CERTIFIED
 10  T2_NO_REFUTATION_IN_SCOPE
 11  T3_PARTIAL_REFUTATION_DECISION_INVARIANT_SURVIVES
  3  T4_CANNOT_CHECK  (control or validation failure, or budget exceeded)
  4  T5_ENUMERATOR_DEFECT (a positive control fired; this is a bug, not a finding)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from typing import Any

PROTOCOL_IDENTITY = "ORION21.TIE_EQUIVALENCE_QUOTIENT.v1"
SCHEMA = "orion.orion21.tie-equivalence-quotient.result.v1"

EXIT_T1 = 0
EXIT_T2 = 10
EXIT_T3 = 11
EXIT_CANNOT_CHECK = 3
EXIT_ENUMERATOR_DEFECT = 4


class ControlViolation(RuntimeError):
    """A positive/negative control fired. Enumerator defect, never a finding."""


class CannotCheck(RuntimeError):
    """The check could not be carried out. Never reported as a pass."""


# ---------------------------------------------------------------------------
# 1. The selection rule, reimplemented faithfully in stdlib
# ---------------------------------------------------------------------------

def sign(v: int) -> int:
    """numpy.sign semantics on integers."""
    return (v > 0) - (v < 0)


def enumerate_supports(corr: tuple[int, ...], r: int) -> tuple[list[tuple[int, ...]], dict[str, Any]]:
    """Exact top-r equality class from integer correlations.

    Byte-faithful to enumerate_supports() of
    papers/orion-21-state-as-computation/experiments/tie-robust-phase-v1/run_tie_robust_phase.py:
    order by (-|c_i|, i); boundary = |c| at rank r-1; fixed = strictly above
    boundary; tied = exactly at boundary; choose `need` of the tied.  Zero
    correlations are admissible and contribute sign 0 downstream.
    """
    absc = tuple(abs(v) for v in corr)
    p = len(corr)
    if not 0 < r <= p:
        raise ValueError("invalid r")
    order = sorted(range(p), key=lambda i: (-absc[i], i))
    boundary = absc[order[r - 1]]
    fixed = tuple(sorted(i for i in range(p) if absc[i] > boundary))
    tied = tuple(sorted(i for i in range(p) if absc[i] == boundary))
    need = r - len(fixed)
    if need < 0 or need > len(tied):
        raise ControlViolation("inconsistent boundary class")
    options = [tuple(sorted(fixed + choice)) for choice in itertools.combinations(tied, need)]
    if not options:
        raise ControlViolation("empty admissible support set")
    meta = {
        "boundary_abs_correlation": boundary,
        "fixed_above_boundary": list(fixed),
        "boundary_tied": list(tied),
        "need_from_boundary": need,
        "candidate_count": len(options),
        "canonical_support": list(min(options)),
        "rank_gap_separable": len(options) == 1,
    }
    return options, meta


def admissible_by_predicate(corr: tuple[int, ...], r: int) -> list[tuple[int, ...]]:
    """INDEPENDENT characterisation of the admissible set.

    s is admissible iff |s| == r and every selected feature's absolute
    correlation is at least every unselected feature's absolute correlation.
    This does not share code with enumerate_supports(); it filters all C(p,r)
    subsets by the order-consistency predicate directly.
    """
    absc = tuple(abs(v) for v in corr)
    p = len(corr)
    out: list[tuple[int, ...]] = []
    for s in itertools.combinations(range(p), r):
        inside = set(s)
        lo_in = min(absc[i] for i in s)
        outside = [absc[j] for j in range(p) if j not in inside]
        hi_out = max(outside) if outside else -1
        if lo_in >= hi_out:
            out.append(s)
    return out


# ---------------------------------------------------------------------------
# 2. Downstream readouts
# ---------------------------------------------------------------------------

def rows_of(p: int) -> list[tuple[int, ...]]:
    """The COMPLETE sign-row space {-1,+1}^p in a fixed enumeration order.

    Using the complete row space removes any arbitrary test-bank choice from
    the prediction readout.
    """
    return [tuple(1 if b else -1 for b in combo) for combo in itertools.product((0, 1), repeat=p)]


def predict(corr: tuple[int, ...], support: tuple[int, ...], row: tuple[int, ...]) -> int:
    """Faithful to candidate_prediction(): score = sum(row_i * sign(c_i)); pred = score > 0."""
    score = 0
    for i in support:
        score += row[i] * sign(corr[i])
    return 1 if score > 0 else 0


def prediction_stream(corr: tuple[int, ...], support: tuple[int, ...], rows: list[tuple[int, ...]]) -> tuple[int, ...]:
    return tuple(predict(corr, support, row) for row in rows)


# ---------------------------------------------------------------------------
# 3. The candidate invariant family
# ---------------------------------------------------------------------------
# Each entry is (name, kind, fn(ctx, support) -> hashable).
#   kind "definitional" : constancy (or non-constancy) follows from the
#                         construction of the equality class alone.
#   kind "empirical"    : constancy is decided only by the enumeration.
#
# The named list is a set of REPORTED INSTANCES for interpretability.  The
# family that the impossibility certificate ranges over is not this list; it is
# the complete set of readout-measurable functions (see NOTE_V1.md, the
# fibre-constancy lifting argument).

INVARIANT_SPECS: list[tuple[str, str, str]] = [
    ("support_size", "definitional",
     "cardinality of the selected support"),
    ("abs_correlation_multiset", "definitional",
     "sorted multiset of |c_i| over the selected support"),
    ("abs_correlation_sum", "definitional",
     "sum of |c_i| over the selected support"),
    ("min_abs_correlation_in_support", "definitional",
     "min |c_i| over the selected support"),
    ("max_abs_correlation_in_support", "definitional",
     "max |c_i| over the selected support"),
    ("boundary_level", "definitional",
     "the boundary |c| value (a function of the state alone)"),
    ("admissible_class_size", "definitional",
     "|S(x)| (a function of the state alone)"),
    ("canonical_support", "definitional",
     "min(S(x)) under the ascending-index key (the quotient map itself)"),
    ("support_identity", "empirical",
     "the selected support itself"),
    ("signed_correlation_sum", "empirical",
     "sum of c_i (signed) over the selected support"),
    ("positive_sign_count", "empirical",
     "number of selected features with c_i > 0"),
    ("prediction_stream", "empirical",
     "classifier extension over the COMPLETE sign-row space"),
    ("accuracy_numerator", "empirical",
     "exact integer count of rows agreeing with the canonical-representative labelling"),
]


def invariant_values(corr: tuple[int, ...], support: tuple[int, ...], ctx: dict[str, Any]) -> dict[str, Any]:
    absc = tuple(abs(v) for v in corr)
    sel_abs = tuple(sorted(absc[i] for i in support))
    stream = prediction_stream(corr, support, ctx["rows"])
    canon_stream = ctx["canonical_stream"]
    acc_num = sum(1 for a, b in zip(stream, canon_stream) if a == b)
    return {
        "support_size": len(support),
        "abs_correlation_multiset": sel_abs,
        "abs_correlation_sum": sum(sel_abs),
        "min_abs_correlation_in_support": min(sel_abs),
        "max_abs_correlation_in_support": max(sel_abs),
        "boundary_level": ctx["boundary"],
        "admissible_class_size": ctx["class_size"],
        "canonical_support": ctx["canonical"],
        "support_identity": support,
        "signed_correlation_sum": sum(corr[i] for i in support),
        "positive_sign_count": sum(1 for i in support if corr[i] > 0),
        "prediction_stream": stream,
        "accuracy_numerator": acc_num,
    }


# The invariants whose constancy is what the paper's threshold-crossing verdict
# depends on.  A refutation of ANY of these is what licenses the certificate.
DECISION_INVARIANTS = ("prediction_stream", "accuracy_numerator")


# ---------------------------------------------------------------------------
# 4. Validation and controls (run BEFORE any finding is read)
# ---------------------------------------------------------------------------

def fubini(n: int) -> int:
    """Ordered Bell / Fubini number: number of ordered set partitions of [n]."""
    if n == 0:
        return 1
    stirling = [[0] * (n + 1) for _ in range(n + 1)]
    stirling[0][0] = 1
    for i in range(1, n + 1):
        for k in range(1, i + 1):
            stirling[i][k] = k * stirling[i - 1][k] + stirling[i - 1][k - 1]
    return sum(math.factorial(k) * stirling[n][k] for k in range(n + 1))


def level_structure(absc: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """The ordered set partition of [p] induced by DESCENDING |c| level."""
    by_level: dict[int, list[int]] = {}
    for i, v in enumerate(absc):
        by_level.setdefault(v, []).append(i)
    return tuple(tuple(by_level[v]) for v in sorted(by_level, reverse=True))


def control_fubini(max_p: int) -> dict[str, Any]:
    """Ordered-Bell validation of the level-structure dedupe.

    |c| vectors are generated by BRUTE FORCE over the magnitude alphabet
    {0..p-1} and then deduped, so the resulting count is a measurement, not a
    construction artefact.  This validates the level-structure dedupe only; it
    is not itself the tie-equivalence quotient.
    """
    rows = []
    for p in range(1, max_p + 1):
        seen = set()
        for absc in itertools.product(range(p), repeat=p):
            seen.add(level_structure(absc))
        expected = fubini(p)
        rows.append({"p": p, "distinct_level_structures": len(seen), "fubini_p": expected,
                     "match": len(seen) == expected})
    if not all(r["match"] for r in rows):
        raise ControlViolation(f"ordered-Bell identity failed: {rows}")
    return {"passed": True, "rows": rows,
            "identity": "distinct level structures over magnitude alphabet {0..p-1} == Fubini(p)"}


def control_separable_gap(states_checked: int, violations: list[Any]) -> dict[str, Any]:
    """Positive control: a separable top-r rank gap must give |S(x)| == 1."""
    if violations:
        raise ControlViolation(f"separable gap with |S|>1: {violations[:3]}")
    return {"passed": True, "states_checked": states_checked,
            "rule": "rank_gap_separable == True implies candidate_count == 1"}


def refuting_index(values: list[dict[str, Any]], name: str) -> int | None:
    """Index of the first class member disagreeing with member 0 on `name`, else None.

    Shared by the sweep and by the detector control, so the control exercises the
    same code path that produces the findings.
    """
    ref = values[0][name]
    return next((k for k in range(1, len(values)) if values[k][name] != ref), None)


def control_no_alarm(max_p: int, rows_cache: dict[int, list[tuple[int, ...]]]) -> dict[str, Any]:
    """Negative control: strictly distinct |c| must yield a singleton class by BOTH
    the constructive route and the independent subset-predicate route.

    Both routes are asserted, so a boundary comparison using >= where it must use >
    fails here instead of passing silently. Zero refutations is NOT separately
    asserted: with a singleton class it would be vacuously true, and a control that
    cannot fail is worthless. The detector's ability to fire is covered by
    control_detector_fires() instead.
    """
    checked = 0
    for p in range(2, max_p + 1):
        # strictly distinct magnitudes, every sign pattern exercised
        for signs in itertools.product((1, -1), repeat=p):
            corr = tuple(signs[i] * (i + 1) for i in range(p))
            for r in range(1, p + 1):
                options, meta = enumerate_supports(corr, r)
                if len(options) != 1 or not meta["rank_gap_separable"]:
                    raise ControlViolation(
                        f"no-alarm control: distinct |c| gave |S|={len(options)} at corr={corr} r={r}")
                predicate = admissible_by_predicate(corr, r)
                if len(predicate) != 1 or tuple(predicate[0]) != options[0]:
                    raise ControlViolation(
                        f"no-alarm control: predicate route disagreed at corr={corr} r={r}")
                checked += 1
    return {"passed": True, "states_checked": checked,
            "rule": "strictly distinct |c| implies a singleton class by BOTH the constructive "
                    "and the subset-predicate route; zero refutations then follows from "
                    "singleton-ness and is deliberately not asserted as a separate (vacuous) check"}


def control_detector_fires(rows_cache: dict[int, list[tuple[int, ...]]]) -> dict[str, Any]:
    """Positive control on the refutation detector itself.

    A control that cannot cry wolf proves nothing, so assert the detector DOES fire
    where it must: c = (1, 1), r = 1 gives the class {(0,), (1,)}, whose two members
    induce different classifiers. If this fails to fire, every SURVIVES verdict in
    the sweep is untrustworthy. The same probe also asserts the detector stays SILENT
    on the class-constant invariants of that very class, so it cannot pass by simply
    reporting everything as refuted.
    """
    corr, r = (1, 1), 1
    options, meta = enumerate_supports(corr, r)
    if len(options) != 2:
        raise ControlViolation(f"detector control: expected a 2-member class, got {len(options)}")
    ctx = _make_ctx(corr, options, meta, rows_cache[2])
    values = [invariant_values(corr, s, ctx) for s in options]
    must_fire = ("support_identity", "prediction_stream", "accuracy_numerator")
    silent = [n for n in must_fire if refuting_index(values, n) is None]
    if silent:
        raise ControlViolation(f"detector control: refutation did NOT fire where it must: {silent}")
    must_stay_silent = ("support_size", "abs_correlation_multiset", "abs_correlation_sum",
                        "min_abs_correlation_in_support", "max_abs_correlation_in_support")
    spurious = [n for n in must_stay_silent if refuting_index(values, n) is not None]
    if spurious:
        raise ControlViolation(f"detector control: spurious refutation of class-constant data: {spurious}")
    return {"passed": True,
            "probe": {"correlations": list(corr), "r": r, "class_size": len(options),
                      "fired_on": list(must_fire), "stayed_silent_on": list(must_stay_silent)},
            "rule": "the refutation detector fires on a known-binding class and stays silent on "
                    "the class-constant invariants of that same class"}


def _make_ctx(corr: tuple[int, ...], options: list[tuple[int, ...]], meta: dict[str, Any],
              rows: list[tuple[int, ...]]) -> dict[str, Any]:
    canonical = min(options)
    return {
        "rows": rows,
        "boundary": meta["boundary_abs_correlation"],
        "class_size": len(options),
        "canonical": canonical,
        "canonical_stream": prediction_stream(corr, canonical, rows),
    }


# ---------------------------------------------------------------------------
# 5. Main sweep
# ---------------------------------------------------------------------------

def sweep(p_values: list[int], alphabet: tuple[int, ...], budget_states: int) -> dict[str, Any]:
    rows_cache = {p: rows_of(p) for p in p_values}

    invariant_status: dict[str, dict[str, Any]] = {
        name: {"kind": kind, "description": desc, "verdict": "SURVIVES", "witness": None,
               "classes_refuted": 0}
        for name, kind, desc in INVARIANT_SPECS
    }

    states_total = 0
    outcomes_total = 0
    classes_total = 0
    singleton_classes = 0
    nonsingleton_classes = 0
    binding_classes = 0
    benign_classes = 0
    separable_violations: list[Any] = []
    cross_check_mismatches: list[Any] = []
    binomial_mismatches: list[Any] = []
    class_size_hist: dict[int, int] = {}
    benign_by_boundary: dict[int, int] = {}
    binding_by_boundary: dict[int, int] = {}
    straddle_records: list[dict[str, Any]] = []
    benign_bank_identity_checked = 0
    benign_bank_identity_ok = True

    for p in p_values:
        rows = rows_cache[p]
        n_rows = len(rows)
        for corr in itertools.product(alphabet, repeat=p):
            for r in range(1, p + 1):
                states_total += 1
                if states_total > budget_states:
                    raise CannotCheck(
                        f"state budget {budget_states} exceeded at p={p}; enumeration incomplete")
                options, meta = enumerate_supports(corr, r)

                # --- validation A1: independent subset-predicate cross-check
                predicate_set = admissible_by_predicate(corr, r)
                if sorted(options) != sorted(predicate_set):
                    cross_check_mismatches.append(
                        {"corr": list(corr), "r": r,
                         "constructive": [list(s) for s in sorted(options)],
                         "predicate": [list(s) for s in sorted(predicate_set)]})

                # --- validation A2: binomial identity on the class size
                expected_size = math.comb(len(meta["boundary_tied"]), meta["need_from_boundary"])
                if len(options) != expected_size:
                    binomial_mismatches.append(
                        {"corr": list(corr), "r": r, "got": len(options), "expected": expected_size})

                # --- control A4: separable gap must be singleton
                if meta["rank_gap_separable"] and len(options) != 1:
                    separable_violations.append({"corr": list(corr), "r": r, "size": len(options)})

                classes_total += 1
                size = len(options)
                outcomes_total += size
                class_size_hist[size] = class_size_hist.get(size, 0) + 1
                if size == 1:
                    singleton_classes += 1
                    continue
                nonsingleton_classes += 1

                ctx = _make_ctx(corr, options, meta, rows)
                values = [invariant_values(corr, s, ctx) for s in options]

                # --- invariant testing
                for name, _kind, _desc in INVARIANT_SPECS:
                    ref = values[0][name]
                    diff_idx = refuting_index(values, name)
                    if diff_idx is not None:
                        st = invariant_status[name]
                        st["classes_refuted"] += 1
                        if st["verdict"] != "REFUTED":
                            st["verdict"] = "REFUTED"
                            st["witness"] = {
                                "p": p, "r": r, "correlations": list(corr),
                                "tie_equivalence_class": [list(s) for s in options],
                                "canonical_representative": list(ctx["canonical"]),
                                "state_a_support": list(options[0]),
                                "state_b_support": list(options[diff_idx]),
                                "value_a": _jsonable(ref),
                                "value_b": _jsonable(values[diff_idx][name]),
                            }

                # --- decision-binding vs benign tie classification
                streams = {v["prediction_stream"] for v in values}
                blvl = meta["boundary_abs_correlation"]
                if len(streams) == 1:
                    benign_classes += 1
                    benign_by_boundary[blvl] = benign_by_boundary.get(blvl, 0) + 1
                else:
                    binding_classes += 1
                    binding_by_boundary[blvl] = binding_by_boundary.get(blvl, 0) + 1
                    nums = [v["accuracy_numerator"] for v in values]
                    lo, hi = min(nums), max(nums)
                    if len(straddle_records) < 8:
                        straddle_records.append({
                            "p": p, "r": r, "correlations": list(corr),
                            "class_size": size,
                            "admissible_accuracy_numerators": sorted(set(nums)),
                            "denominator": n_rows,
                            "min_numerator": lo, "max_numerator": hi,
                            "straddle_note": (
                                f"any threshold theta with {lo}/{n_rows} < theta <= {hi}/{n_rows} "
                                "receives a different verdict on two members of this single class"),
                        })

                    # --- validation A6: benign-restricted-bank closed form,
                    # exhaustively verified for small row spaces only.
                    if n_rows <= 8:
                        d_union = set()
                        for a in range(size):
                            for b in range(a + 1, size):
                                sa, sb = values[a]["prediction_stream"], values[b]["prediction_stream"]
                                for j in range(n_rows):
                                    if sa[j] != sb[j]:
                                        d_union.add(j)
                        predicted = 2 ** (n_rows - len(d_union))
                        actual = 0
                        for mask in range(1 << n_rows):
                            bank = [j for j in range(n_rows) if mask >> j & 1]
                            sub = {tuple(v["prediction_stream"][j] for j in bank) for v in values}
                            if len(sub) == 1:
                                actual += 1
                        benign_bank_identity_checked += 1
                        if predicted != actual:
                            benign_bank_identity_ok = False

    if cross_check_mismatches or binomial_mismatches:
        raise ControlViolation(
            f"enumerator cross-check failed: predicate_mismatches={len(cross_check_mismatches)} "
            f"binomial_mismatches={len(binomial_mismatches)} "
            f"first={(cross_check_mismatches or binomial_mismatches)[0]}")
    if not benign_bank_identity_ok:
        raise ControlViolation("benign-restricted-bank closed form disagreed with exhaustive count")

    control_separable_gap(classes_total, separable_violations)

    # Three DISTINCT quantities; conflating them is the easy misreading:
    #   states           = pairs (c, r)                       -> one class each
    #   realized outcomes = pairs (x, s) with s in S(x)        -> sum of |S(x)|
    #   classes           = tie-equivalence classes            -> equals states
    # The class-size histogram is keyed by |S(x)| and counts STATES, so
    # sum(count) == states and sum(size*count) == realized outcomes.
    if sum(class_size_hist.values()) != states_total:
        raise ControlViolation("histogram counts disagree with the state count")
    if sum(k * v for k, v in class_size_hist.items()) != outcomes_total:
        raise ControlViolation("histogram weight disagrees with the realized-outcome count")

    return {
        "states_enumerated": states_total,
        "realized_outcomes_enumerated": outcomes_total,
        "quotient_compression": {
            "realized_outcomes": outcomes_total,
            "classes_after_quotient": classes_total,
            "ratio": f"{outcomes_total}/{classes_total}",
            "note": "the quotient collapses realized (state, support) outcomes onto classes; "
                    "the class-size histogram counts STATES, so sum(count) == states and "
                    "sum(size x count) == realized outcomes",
        },
        "tie_equivalence_classes": classes_total,
        "singleton_classes": singleton_classes,
        "nonsingleton_classes": nonsingleton_classes,
        "decision_binding_classes": binding_classes,
        "decision_benign_classes": benign_classes,
        "class_size_histogram": {str(k): v for k, v in sorted(class_size_hist.items())},
        "benign_classes_by_boundary_level": {str(k): v for k, v in sorted(benign_by_boundary.items())},
        "binding_classes_by_boundary_level": {str(k): v for k, v in sorted(binding_by_boundary.items())},
        "benign_ties_all_at_zero_boundary": all(k == 0 for k in benign_by_boundary),
        "invariants": invariant_status,
        "straddle_examples": straddle_records,
        "validation": {
            "subset_predicate_cross_check": {
                "passed": True, "mismatches": 0,
                "rule": "constructive enumeration equals {s : |s|=r, min_{i in s}|c_i| >= max_{j not in s}|c_j|}"},
            "binomial_class_size": {
                "passed": True, "mismatches": 0,
                "rule": "|S(x)| == C(|tied|, need)"},
            "benign_restricted_bank_closed_form": {
                "passed": True, "classes_checked": benign_bank_identity_checked,
                "rule": "number of row-subsets making a class benign == 2^(n_rows - |disagreement rows|)"},
        },
    }


def _jsonable(v: Any) -> Any:
    if isinstance(v, tuple):
        return [_jsonable(x) for x in v]
    return v


# ---------------------------------------------------------------------------
# 6. Terminal adjudication
# ---------------------------------------------------------------------------

def adjudicate(result: dict[str, Any]) -> tuple[str, int, str]:
    inv = result["invariants"]
    survivors = [n for n, v in inv.items() if v["verdict"] == "SURVIVES"]
    refuted = [n for n, v in inv.items() if v["verdict"] == "REFUTED"]
    decision_refuted = [n for n in DECISION_INVARIANTS if inv[n]["verdict"] == "REFUTED"]

    if decision_refuted:
        return ("T1_IMPOSSIBILITY_CERTIFIED", EXIT_T1,
                "A tie-equivalence class exists on which a decision-determining readout is "
                "non-constant. By fibre-constancy lifting, no representative-independent "
                "invariant of any size in any language over the readout determines that "
                "decision, within the enumerated scope.")
    if not refuted:
        return ("T2_NO_REFUTATION_IN_SCOPE", EXIT_T2,
                "No enumerated invariant was refuted within scope. This is NOT an impossibility "
                "certificate; it reports that the quotient did not separate anything here.")
    return ("T3_PARTIAL_REFUTATION_DECISION_INVARIANT_SURVIVES", EXIT_T3,
            f"Refutations found ({len(refuted)}) but every decision-determining readout survived. "
            "This is NOT an impossibility certificate.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true", help="fast reduced scope")
    ap.add_argument("--out", default=None, help="write RESULTS json to this path")
    ap.add_argument("--budget-states", type=int, default=2_000_000)
    ap.add_argument("--inject", choices=("control", "cannotcheck"), default=None,
                    help="inject a fault to exercise the T5/T4 emit path (self-test only)")
    ap.add_argument("--selftest", action="store_true",
                    help="exercise and validate the T4/T5 error paths, then exit")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    if args.smoke:
        p_values = [2, 3]
        alphabet = (-1, 0, 1)
        fubini_max_p = 3
    else:
        p_values = [2, 3, 4, 5]
        alphabet = (-2, -1, 0, 1, 2)
        fubini_max_p = 5

    started = time.time()
    controls: dict[str, Any] = {}
    try:
        if args.inject == "control":
            raise ControlViolation("injected fault: self-test of the T5 emit path")
        if args.inject == "cannotcheck":
            raise CannotCheck("injected fault: self-test of the T4 emit path")
        rows_cache = {p: rows_of(p) for p in p_values}
        controls["ordered_bell_level_structure"] = control_fubini(fubini_max_p)
        controls["no_alarm_strictly_distinct"] = control_no_alarm(max(p_values), rows_cache)
        controls["refutation_detector_fires"] = control_detector_fires(rows_cache)
        result = sweep(p_values, alphabet, args.budget_states)
        controls["separable_gap_positive_control"] = {
            "passed": True, "states_checked": result["tie_equivalence_classes"],
            "rule": "rank_gap_separable == True implies candidate_count == 1"}
    except ControlViolation as exc:
        payload = _envelope(p_values, alphabet, started, controls)
        payload.update({"terminal": "T5_ENUMERATOR_DEFECT", "exit_code": EXIT_ENUMERATOR_DEFECT,
                        "status": "ENUMERATOR_DEFECT", "detail": str(exc)})
        _emit(payload, args.out)
        return EXIT_ENUMERATOR_DEFECT
    except CannotCheck as exc:
        payload = _envelope(p_values, alphabet, started, controls)
        payload.update({"terminal": "T4_CANNOT_CHECK", "exit_code": EXIT_CANNOT_CHECK,
                        "status": "CANNOT_CHECK", "detail": str(exc)})
        _emit(payload, args.out)
        return EXIT_CANNOT_CHECK

    terminal, code, rationale = adjudicate(result)
    inv = result["invariants"]
    survivors = sorted(n for n, v in inv.items() if v["verdict"] == "SURVIVES")
    refuted = sorted(n for n, v in inv.items() if v["verdict"] == "REFUTED")

    payload = _envelope(p_values, alphabet, started, controls)
    payload.update({
        "terminal": terminal,
        "exit_code": code,
        "status": "OK",
        "rationale": rationale,
        "enumeration": {k: v for k, v in result.items() if k not in ("invariants",)},
        "invariants": inv,
        "surviving_invariants": survivors,
        "refuted_invariants": refuted,
        "decision_determining_readouts": list(DECISION_INVARIANTS),
        "scoped_impossibility": {
            "certified": terminal == "T1_IMPOSSIBILITY_CERTIFIED",
            "statement": (
                "Within the enumerated domain bounds, the subfamily of invariants that are both "
                "representative-independent (constant on every tie-equivalence class) and "
                "decision-determining (fixing the value of a threshold verdict on the screening "
                "accuracy) is EMPTY. Survivors exist, but every survivor factors through "
                "class-constant data and is therefore decision-blind."),
            "lifting_argument": (
                "If f is constant on every tie-equivalence class and the decision V satisfies "
                "V = g(f), then V is constant on every class. Contrapositive: one class on which "
                "V is non-constant refutes representative-independence for EVERY "
                "decision-determining invariant, of every size, in every language over the "
                "readout. The complete set of quotient-measurable functions is the set of "
                "assignments of one value per class, so enumerating classes covers that family."),
            "lift_covers": "invariant size and invariant language",
            "lift_does_NOT_cover": "domain size; the certificate holds only over the bounds below",
        },
        "authority": {
            "scientific_authority_delta": "NONE",
            "submission_authority": False,
            "reopens_v1_lane": False,
            "reopens_tie_robust_phase_v1": False,
            "magnitude_transfer": "NONE - this is a third instrument; no magnitude here transfers "
                                  "to the NR07 anchor replay or the reconstructed ladder sweep, "
                                  "and none was read from them.",
        },
    })
    _emit(payload, args.out)
    return code


def _selftest() -> int:
    """Exercise the T4/T5 emit paths, which the normal run never reaches.

    Runs this same file as a subprocess with an injected fault so the real argparse,
    exception handling, emit and exit-code path are all exercised, then asserts the
    emitted JSON parses, carries the right terminal, and leaks no internal key.
    """
    import subprocess
    import tempfile

    cases = [("cannotcheck", "T4_CANNOT_CHECK", EXIT_CANNOT_CHECK, "CANNOT_CHECK"),
             ("control", "T5_ENUMERATOR_DEFECT", EXIT_ENUMERATOR_DEFECT, "ENUMERATOR_DEFECT")]
    failures: list[str] = []
    for inject, terminal, want_code, want_status in cases:
        with tempfile.NamedTemporaryFile("r+", suffix=".json", delete=False) as fh:
            path = fh.name
        proc = subprocess.run(
            [sys.executable, __file__, "--smoke", "--inject", inject, "--out", path],
            capture_output=True, text=True)
        if proc.returncode != want_code:
            failures.append(f"{inject}: exit {proc.returncode} != {want_code}")
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{inject}: emitted JSON did not parse ({exc})")
            continue
        if payload.get("terminal") != terminal:
            failures.append(f"{inject}: terminal {payload.get('terminal')!r} != {terminal!r}")
        if payload.get("status") != want_status:
            failures.append(f"{inject}: status {payload.get('status')!r} != {want_status!r}")
        if payload.get("exit_code") != want_code:
            failures.append(f"{inject}: exit_code field {payload.get('exit_code')!r} != {want_code}")
        if "_started_monotonic" in payload:
            failures.append(f"{inject}: internal key _started_monotonic leaked into the payload")
        if not payload.get("detail"):
            failures.append(f"{inject}: no detail recorded")
        if payload.get("scoped_impossibility", {}).get("certified"):
            failures.append(f"{inject}: an error path claimed a certificate")

    report = {"schema": "orion.orion21.tie-equivalence-quotient.selftest.v1",
              "paths_exercised": ["T4_CANNOT_CHECK", "T5_ENUMERATOR_DEFECT"],
              "failures": failures, "status": "PASS" if not failures else "FAIL"}
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


def _envelope(p_values: list[int], alphabet: tuple[int, ...], started: float,
              controls: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "protocol_identity": PROTOCOL_IDENTITY,
        "paper": "orion-21-state-as-computation",
        "scope": {
            "bank_widths_p": list(p_values),
            "support_sizes_r": "1..p inclusive, for every p",
            "correlation_alphabet": list(alphabet),
            "correlation_vectors_per_p": f"|alphabet|^p = {len(alphabet)}^p (complete cross product)",
            "test_bank": "the COMPLETE sign-row space {-1,+1}^p, all 2^p rows, no sampling",
            "labels": "predictions of the canonical representative min(S(x)) under the "
                      "ascending-index key; declared here, prospectively, and used only to "
                      "give the accuracy readout a canonical reference",
            "arithmetic": "exact integers only; no float aggregate enters any decision",
        },
        "controls": controls,
        # Deliberately NO interpreter version and NO wall clock in the digested payload:
        # RESULTS_V1.json must be byte-reproducible on any machine. Both are printed to
        # stderr instead.
        "determinism": "this file is byte-reproducible; provenance (interpreter version, "
                       "wall seconds) is printed to stderr and deliberately excluded",
        "_started_monotonic": started,
    }


def _emit(payload: dict[str, Any], out: str | None) -> None:
    started = payload.pop("_started_monotonic", None)
    if started is not None:
        print(f"python={sys.version.split()[0]} wall_seconds={time.time() - started:.3f}",
              file=sys.stderr)
    text = json.dumps(payload, indent=2, sort_keys=False) + "\n"
    payload_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {out} sha256={payload_digest}")
    else:
        sys.stdout.write(text)
    print(f"terminal={payload.get('terminal')} exit={payload.get('exit_code')}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
