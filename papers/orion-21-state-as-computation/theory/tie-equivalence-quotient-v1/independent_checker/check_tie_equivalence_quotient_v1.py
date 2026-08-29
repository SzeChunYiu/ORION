#!/usr/bin/env python3
"""Independent checker for ORION21.TIE_EQUIVALENCE_QUOTIENT.v1.

Recomputes the recorded result from scratch and gates the ENTIRE claim, not just
the enumeration counts. It does NOT import the runner and shares no code with it:
the admissible set is obtained here ONLY by filtering all C(p,r) subsets through
the order-consistency predicate, never by the constructive fixed/tied/need
decomposition, and every invariant is re-derived from its definition.

Everything below is recomputed and diffed against the recorded file:
  - the enumeration counts and the relations that must hold between them
  - the per-class value of ALL 13 invariants, hence each verdict and its
    classes_refuted count
  - the surviving / refuted invariant SETS (compared as sets, so ordering cannot
    create a spurious mismatch)
  - the TERMINAL, re-derived from this checker's own verdicts
  - the recorded exit_code and scoped_impossibility.certified flag

Reads RESULTS_V1.json as DATA ONLY.

Exit codes:
  0  PASS
  5  MISMATCH  (recomputation disagrees with the recorded result)
  3  CANNOT_CHECK (result file unreadable / missing required fields)
"""
from __future__ import annotations

import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
RESULT = HERE.parent / "RESULTS_V1.json"

DECISION_INVARIANTS = ("prediction_stream", "accuracy_numerator")
ALL_INVARIANTS = (
    "support_size", "abs_correlation_multiset", "abs_correlation_sum",
    "min_abs_correlation_in_support", "max_abs_correlation_in_support",
    "boundary_level", "admissible_class_size", "canonical_support",
    "support_identity", "signed_correlation_sum", "positive_sign_count",
    "prediction_stream", "accuracy_numerator",
)
# Terminal -> exit code, mirroring the runner's published contract.
TERMINAL_EXIT = {
    "T1_IMPOSSIBILITY_CERTIFIED": 0,
    "T2_NO_REFUTATION_IN_SCOPE": 10,
    "T3_PARTIAL_REFUTATION_DECISION_INVARIANT_SURVIVES": 11,
}


def admissible(corr, r):
    """s admissible iff |s| == r and every selected |c| >= every unselected |c|."""
    absc = [abs(v) for v in corr]
    p = len(corr)
    out = []
    for s in itertools.combinations(range(p), r):
        ins = set(s)
        outside = [absc[j] for j in range(p) if j not in ins]
        if min(absc[i] for i in s) >= (max(outside) if outside else -1):
            out.append(s)
    return out


def stream(corr, s, rows):
    """score = sum(row_i * sign(c_i)) over the support; prediction is score > 0."""
    res = []
    for row in rows:
        sc = 0
        for i in s:
            c = corr[i]
            sc += row[i] * ((c > 0) - (c < 0))
        res.append(1 if sc > 0 else 0)
    return tuple(res)


def invariants_of(corr, s, rows, class_size, canon, canon_stream, boundary):
    """All 13 invariants for one class member, re-derived from their definitions."""
    absc = [abs(v) for v in corr]
    sel = tuple(sorted(absc[i] for i in s))
    st = stream(corr, s, rows)
    return {
        "support_size": len(s),
        "abs_correlation_multiset": sel,
        "abs_correlation_sum": sum(sel),
        "min_abs_correlation_in_support": min(sel),
        "max_abs_correlation_in_support": max(sel),
        "boundary_level": boundary,
        "admissible_class_size": class_size,
        "canonical_support": canon,
        "support_identity": tuple(s),
        "signed_correlation_sum": sum(corr[i] for i in s),
        "positive_sign_count": sum(1 for i in s if corr[i] > 0),
        "prediction_stream": st,
        "accuracy_numerator": sum(1 for a, b in zip(st, canon_stream) if a == b),
    }


def main() -> int:
    try:
        rec = json.loads(RESULT.read_text(encoding="utf-8"))
        scope = rec["scope"]
        p_values = list(scope["bank_widths_p"])
        alphabet = tuple(scope["correlation_alphabet"])
        enum = rec["enumeration"]
        rec_inv = rec["invariants"]
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK", "detail": str(exc)}, indent=2))
        return 3

    states = classes = singleton = nonsingleton = binding = benign = outcomes = 0
    benign_boundaries: set[int] = set()
    binding_boundaries: set[int] = set()
    refuted_count = {n: 0 for n in ALL_INVARIANTS}

    for p in p_values:
        rows = [tuple(1 if b else -1 for b in c) for c in itertools.product((0, 1), repeat=p)]
        for corr in itertools.product(alphabet, repeat=p):
            absc = [abs(v) for v in corr]
            for r in range(1, p + 1):
                states += 1
                classes += 1
                opts = sorted(admissible(corr, r))
                outcomes += len(opts)
                if len(opts) == 1:
                    singleton += 1
                    continue
                nonsingleton += 1
                canon = opts[0]
                canon_stream = stream(corr, canon, rows)
                boundary = min(absc[i] for i in canon)
                vals = [invariants_of(corr, s, rows, len(opts), canon, canon_stream, boundary)
                        for s in opts]

                for name in ALL_INVARIANTS:
                    first = vals[0][name]
                    if any(v[name] != first for v in vals[1:]):
                        refuted_count[name] += 1

                if len({v["prediction_stream"] for v in vals}) == 1:
                    benign += 1
                    benign_boundaries.add(boundary)
                else:
                    binding += 1
                    binding_boundaries.add(boundary)

    # ---- recomputed verdicts, sets and terminal -----------------------------
    verdict = {n: ("REFUTED" if refuted_count[n] else "SURVIVES") for n in ALL_INVARIANTS}
    my_refuted = {n for n in ALL_INVARIANTS if verdict[n] == "REFUTED"}
    my_surviving = {n for n in ALL_INVARIANTS if verdict[n] == "SURVIVES"}
    if any(verdict[n] == "REFUTED" for n in DECISION_INVARIANTS):
        my_terminal = "T1_IMPOSSIBILITY_CERTIFIED"
    elif not my_refuted:
        my_terminal = "T2_NO_REFUTATION_IN_SCOPE"
    else:
        my_terminal = "T3_PARTIAL_REFUTATION_DECISION_INVARIANT_SURVIVES"
    my_certified = my_terminal == "T1_IMPOSSIBILITY_CERTIFIED"

    mism: dict[str, object] = {}

    # ---- counts -------------------------------------------------------------
    for key, got in (("states_enumerated", states),
                     ("realized_outcomes_enumerated", outcomes),
                     ("tie_equivalence_classes", classes),
                     ("singleton_classes", singleton), ("nonsingleton_classes", nonsingleton),
                     ("decision_binding_classes", binding), ("decision_benign_classes", benign)):
        if enum.get(key) != got:
            mism[key] = {"recorded": enum.get(key), "recomputed": got}

    if states != classes:
        mism["states_vs_classes"] = {"states": states, "classes": classes}
    if singleton + nonsingleton != classes:
        mism["class_partition"] = {"singleton": singleton, "nonsingleton": nonsingleton}
    hist = {int(k): v for k, v in enum.get("class_size_histogram", {}).items()}
    if sum(hist.values()) != states:
        mism["histogram_counts_states"] = {"sum_counts": sum(hist.values()), "states": states}
    if sum(k * v for k, v in hist.items()) != outcomes:
        mism["histogram_weight_is_outcomes"] = {
            "sum_size_times_count": sum(k * v for k, v in hist.items()), "outcomes": outcomes}

    # ---- per-invariant verdicts and counts, for ALL 13 ----------------------
    for name in ALL_INVARIANTS:
        entry = rec_inv.get(name)
        if not isinstance(entry, dict):
            mism[f"invariant_missing:{name}"] = True
            continue
        if entry.get("verdict") != verdict[name]:
            mism[f"verdict:{name}"] = {"recorded": entry.get("verdict"),
                                       "recomputed": verdict[name]}
        if entry.get("classes_refuted") != refuted_count[name]:
            mism[f"classes_refuted:{name}"] = {"recorded": entry.get("classes_refuted"),
                                               "recomputed": refuted_count[name]}
    extra = set(rec_inv) - set(ALL_INVARIANTS)
    if extra:
        mism["unexpected_invariants_recorded"] = sorted(extra)

    # ---- the headline claim: sets, terminal, exit code, certified flag ------
    if set(rec.get("surviving_invariants", [])) != my_surviving:
        mism["surviving_invariants"] = {"recorded": sorted(rec.get("surviving_invariants", [])),
                                        "recomputed": sorted(my_surviving)}
    if set(rec.get("refuted_invariants", [])) != my_refuted:
        mism["refuted_invariants"] = {"recorded": sorted(rec.get("refuted_invariants", [])),
                                      "recomputed": sorted(my_refuted)}
    if rec.get("terminal") != my_terminal:
        mism["terminal"] = {"recorded": rec.get("terminal"), "recomputed": my_terminal}
    if rec.get("exit_code") != TERMINAL_EXIT.get(my_terminal):
        mism["exit_code"] = {"recorded": rec.get("exit_code"),
                             "recomputed": TERMINAL_EXIT.get(my_terminal)}
    if bool(rec.get("scoped_impossibility", {}).get("certified")) != my_certified:
        mism["scoped_impossibility.certified"] = {
            "recorded": rec.get("scoped_impossibility", {}).get("certified"),
            "recomputed": my_certified}
    if set(rec.get("decision_determining_readouts", [])) != set(DECISION_INVARIANTS):
        mism["decision_determining_readouts"] = {
            "recorded": sorted(rec.get("decision_determining_readouts", [])),
            "recomputed": sorted(DECISION_INVARIANTS)}

    # ---- benign/binding structural characterisation -------------------------
    benign_zero = benign_boundaries == {0} if benign_boundaries else True
    if enum.get("benign_ties_all_at_zero_boundary") != benign_zero:
        mism["benign_ties_all_at_zero_boundary"] = {
            "recorded": enum.get("benign_ties_all_at_zero_boundary"), "recomputed": benign_zero}
    if binding_boundaries & {0}:
        mism["binding_at_zero_boundary"] = sorted(binding_boundaries)

    report = {
        "schema": "orion.orion21.tie-equivalence-quotient.checker.v1",
        "protocol_identity": "ORION21.TIE_EQUIVALENCE_QUOTIENT.v1",
        "independence": "no runner import; admissible set obtained ONLY by subset-predicate "
                        "filtering; all 13 invariants re-derived from their definitions; "
                        "terminal re-derived from this checker's own verdicts; "
                        "result file read as data",
        "recomputed": {
            "states_enumerated": states, "realized_outcomes_enumerated": outcomes,
            "singleton_classes": singleton, "nonsingleton_classes": nonsingleton,
            "decision_binding_classes": binding, "decision_benign_classes": benign,
            "benign_boundary_levels": sorted(benign_boundaries),
            "binding_boundary_levels": sorted(binding_boundaries),
            "classes_refuted": refuted_count,
            "surviving_invariants": sorted(my_surviving),
            "refuted_invariants": sorted(my_refuted),
            "terminal": my_terminal,
            "exit_code": TERMINAL_EXIT.get(my_terminal),
            "certified": my_certified,
        },
        "recorded_terminal": rec.get("terminal"),
        "mismatches": mism,
        "status": "PASS" if not mism else "MISMATCH",
    }
    print(json.dumps(report, indent=2))
    return 0 if not mism else 5


if __name__ == "__main__":
    raise SystemExit(main())
