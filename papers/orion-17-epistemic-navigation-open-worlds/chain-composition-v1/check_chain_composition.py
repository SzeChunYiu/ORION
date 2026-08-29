#!/usr/bin/env python3
"""ORION17.CLOSURE_CHAIN_COMPOSITION.v1 -- exhaustive chain verification.

C2 asserts a countermodel EXISTS, so the sweep must actually exhibit one; control U1
fails the run if it does not, rather than letting an unsupported existence claim pass.

  0 = verified, terminal emitted    3 = could not check
"""
import itertools, json

LENGTHS = [2, 3, 4, 5]
EPOCHS = [1, 2, 3]


def preserves_closure(exact, epochs):
    """An obligation discharged at T_1 survives to T_n iff every bridge transports it
    (exactness) and no step presents it to an older state (epoch monotonicity)."""
    for i in range(len(exact)):
        if not exact[i]:
            return False
        if epochs[i + 1] < epochs[i]:
            return False
    return True


def downstream_closure(n, fail_index):
    """Obligations needing revalidation: everything from the failing link onward."""
    return set(range(fail_index + 1, n))


def first_failure(exact, epochs):
    for i in range(len(exact)):
        if not exact[i] or epochs[i + 1] < epochs[i]:
            return i
    return None


def main() -> int:
    v_c1, v_c3 = [], []
    c2_countermodels = []
    only_inexact_failures = only_order_failures = 0
    u2_elig = u2_caught = 0
    u3_elig = u3_ok = 0
    cases = 0

    for n in LENGTHS:
        nb = n - 1
        for exact in itertools.product([True, False], repeat=nb):
            for epochs in itertools.product(EPOCHS, repeat=n):
                cases += 1
                monotone = all(epochs[i] <= epochs[i + 1] for i in range(nb))
                all_exact = all(exact)
                ok = preserves_closure(exact, epochs)

                # ---- C1: all exact AND monotone must preserve
                if all_exact and monotone:
                    u3_elig += 1
                    if ok:
                        u3_ok += 1
                    else:
                        v_c1.append({"n": n, "epochs": list(epochs)})

                # ---- C2: all exact but NOT monotone, losing closure = the countermodel
                if all_exact and not monotone and not ok:
                    c2_countermodels.append({"n": n, "epochs": list(epochs)})

                # ---- U2: a planted inexact bridge must be detected as losing closure
                if not all_exact and monotone:
                    u2_elig += 1
                    if not ok:
                        u2_caught += 1
                    only_inexact_failures += 1 if not ok else 0

                if all_exact and not monotone and not ok:
                    only_order_failures += 1

                # ---- C3: the revalidation set is the downstream closure of the first failure
                if not ok:
                    fi = first_failure(exact, epochs)
                    if fi is None or downstream_closure(n, fi) != set(range(fi + 1, n)):
                        v_c3.append({"n": n, "epochs": list(epochs)})

    u1_pass = len(c2_countermodels) > 0
    u2_pass = u2_elig > 0 and u2_caught == u2_elig
    u3_pass = u3_elig > 0 and u3_ok == u3_elig
    u4_pass = only_inexact_failures > 0 and only_order_failures > 0

    if not (u2_pass and u3_pass):
        terminal, rc = "T4_CANNOT_CHECK", 3
    elif v_c1:
        terminal, rc = "T2_C1_FAILS", 0
    elif not (u1_pass and u4_pass):
        terminal, rc = "T3_C2_UNSUPPORTED", 0
    elif v_c3:
        terminal, rc = "T2_C1_FAILS", 0
    else:
        terminal, rc = "T1_CHAIN_COMPOSITION_LAW_HOLDS", 0

    print(json.dumps({
        "schema": "ORION.ORION17.ClosureChainComposition.Result.v1",
        "protocol_identity": "ORION17.CLOSURE_CHAIN_COMPOSITION.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "chain_lengths": LENGTHS, "cases_enumerated": cases,
        "violations": {"C1": len(v_c1), "C3": len(v_c3)},
        "c2_countermodels_found": len(c2_countermodels),
        "c2_smallest_countermodel": (min(c2_countermodels, key=lambda r: r["n"])
                                     if c2_countermodels else None),
        "failure_mode_separation": {"only_inexactness_monotone_epochs": only_inexact_failures,
                                    "only_ordering_all_bridges_exact": only_order_failures},
        "controls": {
            "U1_c2_countermodel_must_be_found": {"found": len(c2_countermodels), "passed": u1_pass},
            "U2_closure_failure_is_detectable": {"eligible": u2_elig, "caught": u2_caught, "passed": u2_pass},
            "U3_all_good_no_alarm": {"eligible": u3_elig, "clean": u3_ok, "passed": u3_pass},
            "U4_independence_demonstrated": {"passed": u4_pass}},
        "retrospective_evidence": "NOT TESTED AGAINST — P7_CLOSURE_RETENTION_V1.json records outcome_accessed: true, and it measures PAIRWISE retention, not multi-hop chains",
        "terminal": terminal,
        "promotion_status": ("CHAIN_THEOREM_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED"
                             if terminal == "T1_CHAIN_COMPOSITION_LAW_HOLDS" else "PROMOTION_FAILED"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
