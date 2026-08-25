"""EXEC-XP-01 -- T23 coupled scientific advance, structural verification only."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent

def advance(available: bool, admit: bool) -> bool:
    return available and admit

def run(levels=5):
    cells = viol = 0
    ru = wu = 0                     # the two independence countermodels
    compute_rescues = gov_rescues = 0
    for available in (False, True):
        for admit in (False, True):
            for compute in range(levels):
                for governance in range(levels):
                    cells += 1
                    adv = advance(available, admit)
                    # independent formulation: advance fails if either conjunct fails
                    indep = not ((not available) or (not admit))
                    if adv != indep:
                        viol += 1
                    # countermodels
                    if available and not admit:
                        ru += 1                       # reachable but unauthorized
                        if compute == levels - 1 and adv:
                            compute_rescues += 1      # max compute produced an advance
                    if admit and not available:
                        wu += 1                       # well-specified but unreachable
                        if governance == levels - 1 and adv:
                            gov_rescues += 1
    return {"cells": cells, "biconditional_violations": viol,
            "countermodels": {"reachable_unauthorized": ru, "wellspecified_unreachable": wu,
                              "both_present": ru > 0 and wu > 0},
            "impossibility": {"compute_rescues_missing_authority": compute_rescues,
                              "governance_rescues_unreachability": gov_rescues}}

def main():
    t0 = time.time(); grid = {"levels": 5, "seed": 20260825}
    r = run(grid["levels"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-XP-01",
         "grid": grid, **r, "totals": {"wallclock_seconds": round(time.time()-t0, 3)}}
    (HERE/"RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2)+"\n")
    print("cells", r["cells"], "viol", r["biconditional_violations"])
    print("countermodels", r["countermodels"])
    print("impossibility", r["impossibility"])
main()
