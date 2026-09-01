#!/usr/bin/env python3
"""ANON.REFINEMENT_TO_CERTIFIABILITY.v1 -- exhaustive counterexample search.

Every check looks for a VIOLATION of R1-R5. Finding none over an exhaustive family is
the evidence, and the planted-violation controls are what make that evidence mean
something rather than reflect a search that cannot see.

R3 is compared against the TRUE minimum over all set partitions, never against another
heuristic -- a greedy-versus-greedy comparison would be circular, and R3 is the claim
most likely to be wrong.

  0 = searched, terminal emitted     3 = could not check
"""
import json, itertools

TOL = 1e-9
GRID = list(range(7))
SIZES_MAIN = [2, 3, 4, 5]      # R1, R2, R3, R5
SIZES_R4 = [2, 3, 4]           # R4 nests partition enumeration; scope stated in output
EPS_GRID = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]


def set_partitions(items):
    """Every set partition of `items` -- the exhaustive ground truth for R3 and R4."""
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for smaller in set_partitions(rest):
        for i in range(len(smaller)):
            yield smaller[:i] + [[first] + smaller[i]] + smaller[i + 1:]
        yield [[first]] + smaller


def diameter(vals):
    return max(vals) - min(vals) if vals else 0.0


def greedy_parts(vals, width):
    """Left-to-right sweep: open a new part when the value exceeds this part's min by
    more than `width`. R3 claims this count is optimal."""
    if not vals:
        return 0
    s = sorted(vals)
    count, anchor = 1, s[0]
    for v in s[1:]:
        if v - anchor > width + TOL:
            count += 1
            anchor = v
    return count


def true_min_parts(vals, width):
    """Exhaustive minimum over ALL set partitions. Independent of greedy_parts."""
    best = None
    for part in set_partitions(range(len(vals))):
        if all(diameter([vals[i] for i in blk]) <= width + TOL for blk in part):
            if best is None or len(part) < best:
                best = len(part)
    return best


def best_constant_error(vals):
    """Worst-case error of the best single certificate value -- the midpoint optimum.
    This is the ACCEPTED case: one number for the whole fibre."""
    return diameter(vals) / 2.0


def best_indexed_error(vals):
    """Worst-case error when the certificate may see the member index -- the capability
    the fibre denies. Used only by control X1."""
    return max(abs(v - v) for v in vals) if vals else 0.0


def certifiable(err, eps):
    """The ONE predicate every finding and every control is decided by."""
    return err <= eps + TOL


def broken_greedy(vals, width):
    """A deliberately wrong part-counter, used only by control X2 to prove the R3
    comparison can fire at all."""
    return 1


def main() -> int:
    v_r1, v_r2, v_r3, v_r4, v_r5 = [], [], [], [], []
    x1_elig = x1_caught = 0
    x2_pairs = 0
    x2_elig = x2_caught = 0
    x3_alarms = 0
    x4_elig = x4_caught = 0
    x5_checked = x5_ok = 0
    configs = 0

    multisets_main = [m for k in SIZES_MAIN
                      for m in itertools.combinations_with_replacement(GRID, k)]
    multisets_r4 = [m for k in SIZES_R4
                    for m in itertools.combinations_with_replacement(GRID, k)]

    for vals in multisets_main:
        vals = list(vals)
        D = diameter(vals)
        for eps in EPS_GRID:
            configs += 1
            width = 2.0 * eps

            # ---- R1: diameter within 2 eps  =>  midpoint certificate is eps-valid
            if D <= width + TOL:
                mid = (min(vals) + max(vals)) / 2.0
                if max(abs(mid - v) for v in vals) > eps + TOL:
                    v_r1.append({"fibre": vals, "eps": eps, "D": D})

            # ---- R2: eps-validity  <=>  D <= 2 eps, both directions
            achievable = certifiable(best_constant_error(vals), eps)
            if achievable != (D <= width + TOL):
                v_r2.append({"fibre": vals, "eps": eps, "D": D, "achievable": achievable})

            # ---- R3: greedy count == exhaustive true minimum
            g, t = greedy_parts(vals, width), true_min_parts(vals, width)
            x2_pairs += 1
            if t is None or g != t:
                v_r3.append({"fibre": vals, "eps": eps, "greedy": g, "true_min": t})
            # X2 planted violation: a deliberately wrong counter must be caught by the
            # SAME `!=` comparison, otherwise the R3 check proves nothing.
            if t is not None and t != 1:
                x2_elig += 1
                if broken_greedy(vals, width) != t:
                    x2_caught += 1

            # ---- X3: degenerate no-alarm -- zero diameter, or eps wide enough for one part
            if D == 0 or D <= width + TOL:
                if g != 1:
                    x3_alarms.__class__  # keep type stable
                    x3_alarms += 1

            # ---- X5: eps = 0 must need one part per DISTINCT value (barrier recovered)
            if eps == 0.0:
                x5_checked += 1
                if g == len(set(vals)):
                    x5_ok += 1

            # ---- X1: on configs where the ACCEPTED certificate is not eps-valid, a
            # certificate seeing the member index must be, and the SAME `certifiable`
            # predicate must return True for it and False for the accepted one.
            if not certifiable(best_constant_error(vals), eps):
                x1_elig += 1
                if certifiable(best_indexed_error(vals), eps):
                    x1_caught += 1

    # ---- R4: separator realisability, exhaustive over separator atom-structures
    for vals in multisets_r4:
        vals = list(vals)
        for eps in EPS_GRID:
            width = 2.0 * eps
            kstar = true_min_parts(vals, width)
            for atoms in set_partitions(range(len(vals))):
                atom_vals = [[vals[i] for i in a] for a in atoms]
                unrealisable = any(diameter(av) > width + TOL for av in atom_vals)

                # minimum S-measurable parts: group ATOMS, exhaustively
                kS = None
                for grouping in set_partitions(range(len(atoms))):
                    if all(diameter([v for gi in blk for v in atom_vals[gi]]) <= width + TOL
                           for blk in grouping):
                        if kS is None or len(grouping) < kS:
                            kS = len(grouping)

                if unrealisable:
                    x4_elig += 1
                    if kS is None:
                        x4_caught += 1
                    else:
                        v_r4.append({"fibre": vals, "eps": eps, "atoms": atoms,
                                     "why": "S-indistinguishable pair exceeds 2 eps but a finite S-measurable cost was found"})
                else:
                    if kS is None:
                        v_r4.append({"fibre": vals, "eps": eps, "atoms": atoms,
                                     "why": "realisable by the characterisation but no S-measurable partition found"})
                    elif kstar is not None and kS < kstar:
                        v_r4.append({"fibre": vals, "eps": eps, "atoms": atoms,
                                     "kS": kS, "kstar": kstar, "why": "kS < k* violates R4"})

    # ---- R5: coverage identity over a family of fibres
    for eps in EPS_GRID:
        width = 2.0 * eps
        fam = multisets_r4
        covered = sum(1 for m in fam if diameter(list(m)) <= width + TOL)
        n_certifiable = sum(1 for m in fam if certifiable(best_constant_error(list(m)), eps))
        if covered != n_certifiable:
            v_r5.append({"eps": eps, "covered": covered, "certifiable": n_certifiable})

    x1_ok = x1_elig > 0 and x1_caught == x1_elig
    x2_ok = x2_pairs > 0 and x2_elig > 0 and x2_caught == x2_elig
    x4_ok = x4_elig > 0 and x4_caught == x4_elig
    x5_ok_all = x5_checked > 0 and x5_ok == x5_checked

    if not (x1_ok and x2_ok and x4_ok and x5_ok_all) or x3_alarms:
        terminal, rc = "T5_CANNOT_CHECK_CONTROL_FAILED", 3
    elif v_r3:
        terminal, rc = "T2_GREEDY_IS_NOT_OPTIMAL", 0
    elif v_r1:
        terminal, rc = "T3_SUFFICIENCY_FAILS", 0
    elif v_r4:
        terminal, rc = "T4_REALISABILITY_CHARACTERISATION_FAILS", 0
    elif v_r2 or v_r5:
        terminal, rc = "T4_REALISABILITY_CHARACTERISATION_FAILS", 0
    else:
        terminal, rc = "T1_REFINEMENT_CROSSES_THE_BOUNDARY_CONSTRUCTIVELY", 0

    print(json.dumps({
        "schema": "ANON.RefinementToCertifiability.Result.v1",
        "protocol_identity": "ANON.REFINEMENT_TO_CERTIFIABILITY.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "enumeration": {
            "value_grid": GRID, "eps_grid": EPS_GRID,
            "sizes_R1_R2_R3_R5": SIZES_MAIN, "sizes_R4": SIZES_R4,
            "configs_main": configs,
            "R4_scope_note": "R4 nests partition enumeration over separator atoms inside partition enumeration over fibres, so it is exhaustive on sizes 2-4 rather than 2-5. The scope is stated, not silently truncated.",
            "exhaustive_within_stated_scope": True},
        "violations": {"R1": len(v_r1), "R2": len(v_r2), "R3": len(v_r3),
                       "R4": len(v_r4), "R5": len(v_r5)},
        "violation_examples": {"R1": v_r1[:3], "R2": v_r2[:3], "R3": v_r3[:3],
                               "R4": v_r4[:3], "R5": v_r5[:3]},
        "controls": {
            "X1_planted_subfloor_certificate_is_caught": {"eligible": x1_elig, "caught": x1_caught, "passed": x1_ok},
            "X2_greedy_vs_exhaustive_true_minimum": {"comparisons": x2_pairs,
                "planted_eligible": x2_elig, "planted_caught": x2_caught, "passed": x2_ok,
                "note": "true_min_parts enumerates all set partitions and shares no code with greedy_parts; a deliberately wrong counter is run through the same comparison to prove it can fire"},
            "X3_degenerate_no_alarm": {"alarms": x3_alarms, "passed": not x3_alarms},
            "X4_unrealisable_case_detected": {"eligible": x4_elig, "caught": x4_caught, "passed": x4_ok},
            "X5_eps_zero_recovers_the_barrier": {"checked": x5_checked, "ok": x5_ok, "passed": x5_ok_all}},
        "terminal": terminal,
        "promotion_status": ("THEORY_STEP_COMPLETE__PROMOTION_NOT_YET_EARNED"
                             if terminal.startswith("T1") else "PROMOTION_FAILED_AT_THEORY_STEP"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
