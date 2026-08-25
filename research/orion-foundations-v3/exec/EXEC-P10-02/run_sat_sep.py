"""EXEC-P10-02 -- T22 separation on a family that actually contains UNSAT."""
from __future__ import annotations
import itertools, json, random, time
from pathlib import Path
HERE = Path(__file__).resolve().parent

def sat_check(a, cs):
    """Single independent pass: verify a supplied assignment."""
    return all(any(a[abs(l)-1] == (l > 0) for l in c) for c in cs)

def decide(cs, nvars):
    """Exhaustive decision. Returns (found_assignment_or_None, steps)."""
    steps = 0
    for bits in itertools.product((False, True), repeat=nvars):
        steps += 1
        if sat_check(list(bits), cs):
            return list(bits), steps
    return None, steps

def run(nvars=5, ratios=((21, 4.2), (26, 5.2)), samples=1500, seed=20260825):
    rng = random.Random(seed)
    lits = [l for v in range(1, nvars+1) for l in (v, -v)]
    fams = []
    for nclauses, ratio in ratios:
        for _ in range(samples):
            cs = [tuple(rng.sample([v for v in range(1, nvars+1)], 3)) for _ in range(nclauses)]
            cs = [tuple(c * (1 if rng.random() < .5 else -1) for c in cl) for cl in cs]
            fams.append((cs, nclauses, ratio))

    # PRECONDITION: the family must contain UNSAT before anything is reported
    pre_unsat = 0
    for cs, _, _ in fams:
        if decide(cs, nvars)[0] is None:
            pre_unsat += 1
            if pre_unsat >= 1:
                break
    if pre_unsat == 0:
        return {"precondition": {"unsat_present": False, "checked_before_reporting": True},
                "separation": None,
                "abort_reason": "No unsatisfiable formula in the generated family; run aborted before reporting a separation that was never tested."}

    formulas = satn = unsatn = check_pass = check_fail = 0
    ssat = sunsat = 0
    for cs, nclauses, ratio in fams:
        formulas += 1
        found, steps = decide(cs, nvars)
        if found is None:
            unsatn += 1; sunsat += steps
        else:
            satn += 1; ssat += steps
            if sat_check(found, cs): check_pass += 1
            else: check_fail += 1
    return {"precondition": {"unsat_present": True, "checked_before_reporting": True},
            "separation": {"formulas": formulas, "sat": satn, "unsat": unsatn,
                           "mean_search_steps_sat": round(ssat/max(1,satn), 2),
                           "mean_search_steps_unsat": round(sunsat/max(1,unsatn), 2),
                           "max_possible_assignments": 2**nvars,
                           "check_passes": check_pass, "check_failures": check_fail,
                           "search_asymmetry": round(sunsat/max(1,unsatn) / max(0.01, ssat/max(1,satn)), 2)}}

def main():
    t0 = time.time()
    grid = {"nvars": 5, "ratios": [[21, 4.2], [26, 5.2]], "samples_per_ratio": 1500, "seed": 20260825}
    r = run(grid["nvars"], tuple(tuple(x) for x in grid["ratios"]), grid["samples_per_ratio"], grid["seed"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P10-02", "grid": grid, **r,
         "totals": {"wallclock_seconds": round(time.time()-t0, 3)}}
    (HERE/"RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2)+"\n")
    print("precondition unsat_present:", r["precondition"]["unsat_present"])
    if r["separation"]:
        s = r["separation"]
        print(f"formulas {s['formulas']} SAT {s['sat']} UNSAT {s['unsat']}")
        print(f"mean search: SAT {s['mean_search_steps_sat']} UNSAT {s['mean_search_steps_unsat']} "
              f"of {s['max_possible_assignments']}  asymmetry {s['search_asymmetry']}x")
        print(f"check passes {s['check_passes']} failures {s['check_failures']}")
main()
