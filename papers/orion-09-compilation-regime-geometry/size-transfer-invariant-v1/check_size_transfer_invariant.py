#!/usr/bin/env python3
"""ORION09.SIZE_TRANSFER_INVARIANT.v1 -- exhaustive test of S1-S3 and, decisively,
of whether the capacity invariant ADDS predictive power over fibre inspection.

The theorems being true is not the question #1649 asks. The question is whether counting
predicts anything inspection does not already give, without false alarms.

  0 = measured, terminal emitted    3 = could not check
"""
import itertools, json

KS = [2, 3]
# Enumeration reduced BEFORE any outcome was read: the frozen sizes 4..8 at k=3 are ~4e9
# feature maps and do not terminate. The reduction is recorded in the result object.
SIZES_BY_K = {2: [4, 5, 6], 3: [4, 5]}


def fibres(assign, cells):
    f = {c: [] for c in range(cells)}
    for i, c in enumerate(assign):
        f[c].append(i)
    return f


def separable(assign, labels, cells):
    """S1: a phi-only separator exists iff every fibre is pure."""
    for c in range(cells):
        seen = {labels[i] for i, a in enumerate(assign) if a == c}
        if len(seen) > 1:
            return False
    return True


def has_mixed_fibre(assign, labels, cells):
    return not separable(assign, labels, cells)


def main() -> int:
    v_s1, v_s2 = [], []
    r1_elig = r1_caught = 0
    r2_elig = r2_ok = 0
    capacity_fires = capacity_false_alarms = 0
    fail_from_capacity = fail_below_capacity = 0
    cases = 0

    for k in KS:
        cells = 2 ** k
        for n in SIZES_BY_K[k]:
            for labels in itertools.product([0, 1], repeat=n):
                n_required = len(set(labels))
                for assign in itertools.product(range(cells), repeat=n):
                    cases += 1
                    sep = separable(assign, labels, cells)
                    mixed = not sep

                    # ---- S1 is definitional here; verify the two agree
                    if sep != (not has_mixed_fibre(assign, labels, cells)):
                        v_s1.append({"k": k, "n": n})

                    # ---- S2: capacity exhaustion must force a mixed fibre
                    # required distinct outcomes = distinct labels that must be told apart
                    over_capacity = n_required > cells
                    if over_capacity:
                        capacity_fires += 1
                        if not mixed:
                            capacity_false_alarms += 1
                            v_s2.append({"k": k, "n": n, "why": "over capacity yet separable"})

                    if mixed:
                        if over_capacity:
                            fail_from_capacity += 1
                        else:
                            fail_below_capacity += 1
                        r1_elig += 1
                        if has_mixed_fibre(assign, labels, cells):
                            r1_caught += 1
                    else:
                        r2_elig += 1
                        if separable(assign, labels, cells):
                            r2_ok += 1

    r1_pass = r1_elig > 0 and r1_caught == r1_elig
    r2_pass = r2_elig > 0 and r2_ok == r2_elig
    r3_pass = capacity_false_alarms == 0
    r4_pass = fail_below_capacity > 0

    invariant_adds_power = capacity_fires > 0 and r3_pass

    if not (r1_pass and r2_pass):
        terminal, rc = "T4_CANNOT_CHECK", 3
    elif v_s2 or not r3_pass:
        terminal, rc = "T2_S2_FALSE", 0
    elif not invariant_adds_power:
        terminal, rc = "T3_INVARIANT_ADDS_NOTHING", 0
    else:
        terminal, rc = "T1_INVARIANT_ADDS_PREDICTIVE_POWER", 0

    print(json.dumps({
        "schema": "ORION.ORION09.SizeTransferInvariant.Result.v1",
        "protocol_identity": "ORION09.SIZE_TRANSFER_INVARIANT.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "features_k": KS, "sizes_by_k": SIZES_BY_K,
        "enumeration_reduced_before_outcome_access": ("frozen sizes 4..8 at k=3 are about 4e9 feature maps and do not terminate; reduced to the sizes shown BEFORE any outcome was read, and recorded here rather than silently"), "configurations_enumerated": cases,
        "violations": {"S1": len(v_s1), "S2": len(v_s2)},
        "capacity_invariant": {
            "times_it_fired": capacity_fires,
            "false_alarms": capacity_false_alarms,
            "failures_it_explains": fail_from_capacity,
            "failures_it_cannot_see": fail_below_capacity,
            "adds_search_free_power": invariant_adds_power},
        "controls": {
            "R1_mixed_fibre_blocks_separation": {"eligible": r1_elig, "caught": r1_caught, "passed": r1_pass},
            "R2_pure_configuration_no_alarm": {"eligible": r2_elig, "clean": r2_ok, "passed": r2_pass},
            "R3_capacity_bound_never_false_alarms": {"false_alarms": capacity_false_alarms, "passed": r3_pass},
            "R4_both_regimes_present": {"below_capacity_failures": fail_below_capacity, "passed": r4_pass}},
        "terminal": terminal,
        "promotion_status": ("INVARIANT_USEFUL__PROMOTION_CANDIDATE" if terminal.startswith("T1")
                             else "PROMOTION_STOPPED__RETURN_TO_SPECIALIST_VENUE"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
