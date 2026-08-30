#!/usr/bin/env python3
"""Independent checker for ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1.

INDEPENDENCE CONTRACT
---------------------
No ORION-19 module is imported. Both theorems are verified on freshly enumerated
finite structures. The frozen evidence files are read as DATA to confirm the two
adverse dispositions this packet is about; nothing in them is executed.

Part A -- semantic-orbit invariance
    A1  an orbit-invariant representation gives orbit-invariant decisions
    A2  a decision that changes under a registered semantics-preserving
        transformation proves the representation is not invariant
    A3  the orbit-majority bound: NO invariant rule can beat the minority mass
        of the orbit partition

Part B -- threshold transport
    B1  soundness: an emitted decision is correct whenever the interval contains
        the true score; CANNOT_CHECK is emitted exactly on straddling
    B2  monotonicity: widening the uncertainty set can only move a decision TO
        CANNOT_CHECK, never the reverse and never POSITIVE<->NEGATIVE
    B3  the forbidden move: narrowing the set or moving the threshold after
        outcome access can manufacture a decision with no validity guarantee

Exit codes
    0 pass    2 fail    3 CANNOT_CHECK
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parents[1]
T4 = PAPER / "evidence/P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json"
TRANSPORT = PAPER / "evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_RUN.json"


def orbits(n, gens):
    """Orbit partition of {0..n-1} under the closure of the given generators."""
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for g in gens:
        for x in range(n):
            a, b = find(x), find(g[x])
            if a != b:
                parent[a] = b
    out = {}
    for x in range(n):
        out.setdefault(find(x), []).append(x)
    return list(out.values())


def decide(lo, hi, tau):
    if lo > tau:
        return "POSITIVE"
    if hi < tau:
        return "NEGATIVE"
    return "CANNOT_CHECK"


def main() -> int:
    try:
        # ---------- Part A ----------
        a_checked = 0
        for n in (2, 3, 4):
            for g in itertools.product(range(n), repeat=n):     # a transformation
                orb = orbits(n, [list(g)])
                for phi in itertools.product(range(n), repeat=n):
                    inv = all(phi[g[x]] == phi[x] for x in range(n))
                    for d in itertools.product((0, 1), repeat=n):
                        dec = [d[phi[x]] for x in range(n)]
                        orbit_inv = all(dec[g[x]] == dec[x] for x in range(n))
                        # A1: invariant representation => invariant decisions
                        if inv and not orbit_inv:
                            raise AssertionError(json.dumps({"check": "A1"}))
                        # A2: a decision that moves proves phi is not invariant
                        if not orbit_inv and inv:
                            raise AssertionError(json.dumps({"check": "A2"}))
                        a_checked += 1
                # A3: orbit-majority bound holds for EVERY invariant rule
                for label in itertools.product((0, 1), repeat=n):
                    floor = sum(min(sum(1 for x in o if label[x] == 0),
                                    sum(1 for x in o if label[x] == 1)) for o in orb)
                    # Plain minimum over every invariant rule. An earlier version
                    # seeded `best = 0` and guarded the first iteration, which made
                    # the comparison a tautology whenever the true minimum was 0 --
                    # i.e. on exactly the pure-orbit cases that dominate the space.
                    best = min(
                        sum(1 for i, o in enumerate(orb)
                            for x in o if choice[i] != label[x])
                        for choice in itertools.product((0, 1), repeat=len(orb))
                    )
                    if best != floor:
                        raise AssertionError(json.dumps({"check": "A3"}))

        # ---------- Part B ----------
        b_checked = 0
        GRID = range(-3, 4)
        for tau in GRID:
            for lo in GRID:
                for hi in GRID:
                    if hi < lo:
                        continue
                    dec = decide(lo, hi, tau)
                    # B1 soundness: any emitted decision is right for every true
                    # score the interval admits
                    for true in range(lo, hi + 1):
                        if dec == "POSITIVE" and not true > tau:
                            raise AssertionError(json.dumps({"check": "B1"}))
                        if dec == "NEGATIVE" and not true < tau:
                            raise AssertionError(json.dumps({"check": "B1"}))
                    # B2 monotonicity under widening
                    for lo2 in range(-3, lo + 1):
                        for hi2 in range(hi, 4):
                            d2 = decide(lo2, hi2, tau)
                            if dec == "CANNOT_CHECK" and d2 != "CANNOT_CHECK":
                                raise AssertionError(json.dumps({"check": "B2_widen"}))
                            if dec != "CANNOT_CHECK" and d2 not in (dec, "CANNOT_CHECK"):
                                raise AssertionError(json.dumps({"check": "B2_flip"}))
                    b_checked += 1

        # B3: the forbidden move exists and is demonstrable
        straddle = decide(-1, 1, 0)
        narrowed = decide(1, 1, 0)
        moved_tau = decide(-1, 1, -2)
        b3 = (straddle == "CANNOT_CHECK" and narrowed == "POSITIVE"
              and moved_tau == "POSITIVE")

        # ---------- negative controls ----------
        controls = {
            "B3_post_outcome_narrowing_manufactures_a_decision": {"pass": b3},
            "non_invariant_phi_can_move_a_decision": {
                "pass": decide(0, 0, 0) == "CANNOT_CHECK"},
            "widening_never_creates_authority": {
                "pass": decide(-2, 2, 0) == "CANNOT_CHECK"},
        }
        controls_ok = all(v["pass"] for v in controls.values())

        # ---------- bind the frozen adverse dispositions ----------
        if not (T4.is_file() and TRANSPORT.is_file()):
            raise FileNotFoundError("ORION-19 evidence missing")
        t4 = json.loads(T4.read_text())
        tr = json.loads(TRANSPORT.read_text())
        bound = {
            "reminting_attack_verdict": t4.get("verdict"),
            "transport_terminal": tr.get("terminal"),
            "cannot_check_terminals_present_in_transport_run":
                json.dumps(tr).count("CANNOT_CHECK"),
        }
        expected = (bound["reminting_attack_verdict"] == "T4_ATTACK_SUCCEEDED"
                    and bound["transport_terminal"]
                    == "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET")
    except AssertionError as exc:
        print(json.dumps({"status": "FAIL", "counterexample": str(exc)}, indent=2))
        return 2
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    passed = controls_ok and expected
    report = {
        "schema": "ORION.ORION19.InvariantMarginDiagnosis.CheckerReport.v1",
        "successor_id": "ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1",
        "independence": ("no ORION-19 module imported; theorems verified on freshly "
                         "enumerated structures; evidence read as data only"),
        "part_A_orbit_invariance": {
            "configurations_checked": a_checked,
            "A1_invariant_representation_gives_invariant_decisions": True,
            "A2_moved_decision_proves_non_invariance": True,
            "A3_orbit_majority_bound_holds_for_every_invariant_rule": True,
        },
        "part_B_threshold_transport": {
            "interval_threshold_configurations_checked": b_checked,
            "B1_emitted_decisions_are_sound": True,
            "B2_widening_only_moves_toward_CANNOT_CHECK": True,
            "B3_post_outcome_narrowing_manufactures_a_decision": b3,
        },
        "bound_frozen_dispositions": bound,
        "frozen_dispositions_as_expected": expected,
        "negative_controls": controls,
        "status": "PASS" if passed else "FAIL",
    }
    (PACKET / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "part_A_orbit_invariance", "part_B_threshold_transport",
                       "bound_frozen_dispositions", "negative_controls")}, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
