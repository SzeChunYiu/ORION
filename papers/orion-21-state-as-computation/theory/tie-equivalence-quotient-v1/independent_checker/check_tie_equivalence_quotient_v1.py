#!/usr/bin/env python3
"""Independent checker for ORION21.TIE_EQUIVALENCE_QUOTIENT.v1.

Recomputes the headline quantities of RESULTS_V1.json from scratch. It does NOT
import the runner and shares no code with it: the admissible set is obtained
here ONLY by filtering all C(p,r) subsets through the order-consistency
predicate, never by the constructive fixed/tied/need decomposition.

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
    res = []
    for row in rows:
        sc = 0
        for i in s:
            c = corr[i]
            sc += row[i] * ((c > 0) - (c < 0))
        res.append(1 if sc > 0 else 0)
    return tuple(res)


def main() -> int:
    try:
        rec = json.loads(RESULT.read_text(encoding="utf-8"))
        scope = rec["scope"]
        p_values = list(scope["bank_widths_p"])
        alphabet = tuple(scope["correlation_alphabet"])
        enum = rec["enumeration"]
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK", "detail": str(exc)}, indent=2))
        return 3

    states = classes = singleton = nonsingleton = binding = benign = 0
    outcomes = 0
    benign_boundaries: set[int] = set()
    binding_boundaries: set[int] = set()
    refuted = {"support_identity": 0, "signed_correlation_sum": 0,
               "positive_sign_count": 0, "prediction_stream": 0, "accuracy_numerator": 0}
    survivor_broken: list[str] = []

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

                streams = {stream(corr, s, rows) for s in opts}
                if len(streams) == 1:
                    benign += 1
                    benign_boundaries.add(boundary)
                else:
                    binding += 1
                    binding_boundaries.add(boundary)
                    refuted["prediction_stream"] += 1
                    refuted["accuracy_numerator"] += 1

                if len({tuple(s) for s in opts}) > 1:
                    refuted["support_identity"] += 1
                if len({sum(corr[i] for i in s) for s in opts}) > 1:
                    refuted["signed_correlation_sum"] += 1
                if len({sum(1 for i in s if corr[i] > 0) for s in opts}) > 1:
                    refuted["positive_sign_count"] += 1

                # survivors must be constant on the class
                if len({tuple(sorted(absc[i] for i in s)) for s in opts}) > 1:
                    survivor_broken.append(f"abs_correlation_multiset at corr={corr} r={r}")
                if len({sum(absc[i] for i in s) for s in opts}) > 1:
                    survivor_broken.append(f"abs_correlation_sum at corr={corr} r={r}")
                if len({len(s) for s in opts}) > 1:
                    survivor_broken.append(f"support_size at corr={corr} r={r}")

    mism: dict[str, object] = {}
    for key, got in (("states_enumerated", states),
                     ("realized_outcomes_enumerated", outcomes),
                     ("tie_equivalence_classes", classes),
                     ("singleton_classes", singleton), ("nonsingleton_classes", nonsingleton),
                     ("decision_binding_classes", binding), ("decision_benign_classes", benign)):
        if enum.get(key) != got:
            mism[key] = {"recorded": enum.get(key), "recomputed": got}

    # The three counts are distinct quantities; assert the relations that must hold.
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

    for name, cnt in refuted.items():
        rec_cnt = rec["invariants"][name]["classes_refuted"]
        if rec_cnt != cnt:
            mism[f"classes_refuted:{name}"] = {"recorded": rec_cnt, "recomputed": cnt}
        if rec["invariants"][name]["verdict"] != ("REFUTED" if cnt else "SURVIVES"):
            mism[f"verdict:{name}"] = rec["invariants"][name]["verdict"]

    if survivor_broken:
        mism["survivor_constancy_violated"] = survivor_broken[:3]

    # The headline terminal and the two top-level invariant lists were previously
    # echoed into the report but never compared, so a falsified terminal or a doctored
    # list passed the independent check. They are the scientific claim, so they are
    # gated here.
    derived_refuted = sorted(n for n, c in refuted.items() if c)
    derived_surviving = sorted(n for n, c in refuted.items() if not c)
    if sorted(rec.get("refuted_invariants") or []) != derived_refuted:
        mism["refuted_invariants"] = {
            "recorded": sorted(rec.get("refuted_invariants") or []),
            "recomputed": derived_refuted,
        }
    # surviving_invariants may legitimately name invariants outside the refutation
    # panel, so only the panel members are compared - a recorded survivor that this
    # checker recomputed as refuted is the failure worth catching.
    recorded_surviving = set(rec.get("surviving_invariants") or [])
    wrongly_surviving = sorted(recorded_surviving.intersection(derived_refuted))
    if wrongly_surviving:
        mism["surviving_invariants_recomputed_as_refuted"] = wrongly_surviving

    # T1 is certified only when every panel invariant that is decision-determining was
    # refuted and no surviving invariant broke class-constancy.
    derived_terminal = (
        "T1_IMPOSSIBILITY_CERTIFIED"
        if derived_refuted and not survivor_broken
        else "T0_NOT_CERTIFIED"
    )
    if rec.get("terminal") != derived_terminal:
        mism["terminal"] = {
            "recorded": rec.get("terminal"),
            "recomputed": derived_terminal,
        }

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
                        "filtering; result file read as data",
        "recomputed": {
            "states_enumerated": states, "realized_outcomes_enumerated": outcomes,
            "singleton_classes": singleton,
            "nonsingleton_classes": nonsingleton, "decision_binding_classes": binding,
            "decision_benign_classes": benign,
            "benign_boundary_levels": sorted(benign_boundaries),
            "binding_boundary_levels": sorted(binding_boundaries),
            "classes_refuted": refuted,
        },
        "recorded_terminal": rec.get("terminal"),
        "mismatches": mism,
        "status": "PASS" if not mism else "MISMATCH",
    }
    print(json.dumps(report, indent=2))
    return 0 if not mism else 5


if __name__ == "__main__":
    raise SystemExit(main())
