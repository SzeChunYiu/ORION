#!/usr/bin/env python3
"""ANON.FIBRE_DIAMETER_FLOOR.v1 -- exhaustive counterexample search.

Searches for a certificate that BEATS the D(z)/2 floor. Finding none over an
exhaustive family is evidence only if the search can see a violation when one is
present, so every control below drives the SAME code path with a deliberately
planted violation and requires it to be caught.

  0 = searched, terminal emitted     3 = could not check
"""
import json, itertools

TOL = 1e-9
VALUE_GRID = list(range(7))          # frozen
FIBRE_SIZES = [2, 3, 4, 5]           # frozen
CSTEP = 0.05                         # frozen certificate-grid resolution


def candidates(vals):
    """Certificate values to try: a dense grid wider than the fibre, every observed
    target value, and the exact midpoint -- which must be listed explicitly because
    it is the analytic optimum and need not land on the grid."""
    lo, hi = min(vals), max(vals)
    span = hi - lo
    out, x = set(), lo - span - 1.0
    while x <= hi + span + 1.0:
        out.add(round(x, 10)); x += CSTEP
    out.update(float(v) for v in vals)
    out.add((lo + hi) / 2.0)
    return sorted(out)


def worst_error(c, vals):
    return max(abs(c - v) for v in vals)


def best_accepted_error(vals, *, may_see_member_index=False):
    """Best worst-case error over admissible certificates.

    may_see_member_index=False is the real case: the certificate is accepted on the
    whole fibre, so it is ONE number -- a function of z alone.
    may_see_member_index=True is the control: the certificate may answer per member,
    which is exactly the capability the fibre denies. It must beat the floor.
    """
    if may_see_member_index:
        return max(abs(v - v_) for v, v_ in [(v, v) for v in vals])  # 0 by construction
    return min(worst_error(c, vals) for c in candidates(vals))


def beats_floor(err, floor):
    """The single comparison every finding and every control routes through."""
    return err < floor - TOL


def interval_covers_both_ends(c, r, lo, hi):
    return abs(c - lo) <= r + TOL and abs(c - hi) <= r + TOL


def main() -> int:
    configs = []
    for k in FIBRE_SIZES:
        configs.extend(itertools.combinations_with_replacement(VALUE_GRID, k))

    violations, degenerate_alarms, c3_failures = [], [], []
    c1_eligible = c1_caught = 0
    c4_eligible = c4_caught = 0
    checked = 0

    for vals in configs:
        vals = list(vals)
        lo, hi = min(vals), max(vals)
        D, floor = hi - lo, (hi - lo) / 2.0
        checked += 1

        # ---- the search proper: can a z-only certificate beat the floor?
        best_err = best_accepted_error(vals)
        if beats_floor(best_err, floor):
            rec = {"fibre": vals, "D": D, "floor": floor, "achieved": best_err}
            (degenerate_alarms if D == 0 else violations).append(rec)

        # ---- C3: the optimum must EQUAL D/2, attained at the midpoint
        mid_err = worst_error((lo + hi) / 2.0, vals)
        if abs(mid_err - floor) > TOL or best_err > floor + TOL:
            c3_failures.append({"fibre": vals, "D": D, "floor": floor,
                                "midpoint_error": mid_err, "search_best": best_err})

        if D > 0:
            # ---- C1 (planted violation): a certificate allowed to see the member
            # index must be CAUGHT by the same beats_floor comparison.
            c1_eligible += 1
            if beats_floor(best_accepted_error(vals, may_see_member_index=True), floor):
                c1_caught += 1

            # ---- Theorem 2: no interval of radius < D/2 may cover both ends
            r_narrow = floor - 10 * TOL
            for c in candidates(vals):
                if interval_covers_both_ends(c, r_narrow, lo, hi):
                    violations.append({"fibre": vals, "D": D, "interval_center": c,
                                       "radius": r_narrow,
                                       "why": "interval narrower than D/2 covered both diameter ends"})

            # ---- C4 (planted violation): at radius >= D/2 the midpoint MUST cover
            # both ends, proving interval_covers_both_ends can return True at all.
            c4_eligible += 1
            if interval_covers_both_ends((lo + hi) / 2.0, floor + 10 * TOL, lo, hi):
                c4_caught += 1

    c1_ok = c1_eligible > 0 and c1_caught == c1_eligible
    c4_ok = c4_eligible > 0 and c4_caught == c4_eligible

    if not c1_ok or not c4_ok or c3_failures or degenerate_alarms:
        terminal, rc = "T4_CANNOT_CHECK_CONTROL_FAILED", 3
    elif violations:
        terminal, rc = "T2_FLOOR_VIOLATED__THEOREM_FALSE", 0
    else:
        terminal, rc = "T1_FLOOR_HOLDS_EXHAUSTIVELY", 0

    print(json.dumps({
        "schema": "ANON.FibreDiameterFloor.Result.v1",
        "protocol_identity": "ANON.FIBRE_DIAMETER_FLOOR.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "enumeration": {"value_grid": VALUE_GRID, "fibre_sizes": FIBRE_SIZES,
                        "certificate_grid_step": CSTEP,
                        "configurations_enumerated": checked, "exhaustive": True},
        "controls": {
            "C1_planted_distinguishing_certificate_is_caught": {
                "eligible": c1_eligible, "caught": c1_caught, "passed": c1_ok,
                "note": "routes through the same beats_floor comparison as a real finding"},
            "C2_degenerate_fibre_no_alarm": {
                "alarms": len(degenerate_alarms), "passed": not degenerate_alarms},
            "C3_optimum_equals_half_diameter": {
                "failures": len(c3_failures), "passed": not c3_failures},
            "C4_planted_wide_interval_is_detected": {
                "eligible": c4_eligible, "caught": c4_caught, "passed": c4_ok,
                "note": "proves interval_covers_both_ends can return True at all"}},
        "violations_found": len(violations),
        "violation_examples": violations[:5],
        "terminal": terminal,
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
