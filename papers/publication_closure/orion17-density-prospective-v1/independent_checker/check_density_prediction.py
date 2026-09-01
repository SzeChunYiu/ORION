#!/usr/bin/env python3
"""Independent evaluation of ORION-17's stamped density predictions.

Re-derives each held-out verdict from the recorded campaign output and compares
it with the rule frozen in STAMPED_PREDICTIONS.md. Imports no ORION-17 module and
re-runs no campaign. Negative controls must fire.

Exit 0 PASS, 1 FAIL, 3 CANNOT_CHECK.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
THRESHOLD = 1.5                       # frozen in STAMPED_PREDICTIONS.md
PREDICTED = {"requests": "SOUND", "networkx": "UNSOUND", "django": "UNSOUND",
             "tornado": "UNSOUND", "sympy": "UNSOUND"}
OBSERVED_TRAINING = {"flask": (0.79, "SOUND"), "numpy": (2.53, "UNSOUND"),
                     "scipy": (2.65, "UNSOUND")}

for f in ("HELD_OUT_DENSITY.json", "HELD_OUT_RESULT.json"):
    if not (BASE / f).exists():
        print(f"CANNOT_CHECK: {f} absent"); sys.exit(3)

dens = {d["domain"]: d for d in json.loads((BASE / "HELD_OUT_DENSITY.json").read_text())["held_out"] if d.get("usable")}
res = json.loads((BASE / "HELD_OUT_RESULT.json").read_text())
rows, hits = {}, 0
for dom in res["domains"]:
    name = dom["domain"].replace("repos/", "")
    if not dom.get("usable"):
        continue
    dc = dom["policies"]["donor-coarse"]["false_closure_retention"]
    ec = dom["policies"]["exact-containment"]["false_closure_retention"]
    d = dens.get(name)
    if d is None:
        print(f"CANNOT_CHECK: no pre-outcome density for {name}"); sys.exit(3)
    rule = "UNSOUND" if d["edges_per_module"] >= THRESHOLD else "SOUND"
    actual = "UNSOUND" if dc > 0 else "SOUND"
    if rule != PREDICTED.get(name):
        print(f"CANNOT_CHECK: rule/{name} disagrees with the stamped table"); sys.exit(3)
    rows[name] = {"edges_per_module": d["edges_per_module"], "modules": d["modules"],
                  "predicted": rule, "actual": actual,
                  "donor_false_retention": dc, "exact_false_retention": ec}
    hits += rule == actual

checks = {
    "all_five_predictions_correct": hits == len(rows) == 5,
    "tornado_the_disambiguator_is_correct": rows.get("tornado", {}).get("predicted") == rows.get("tornado", {}).get("actual"),
    "tornado_is_small_but_dense": rows.get("tornado", {}).get("modules", 0) < 100 and rows.get("tornado", {}).get("edges_per_module", 0) > 5,
    "exact_containment_never_falsely_retains": all(r["exact_false_retention"] == 0 for r in rows.values()),
}
controls = {
    "both_outcome_classes_occur_in_the_held_out_set":
        len({r["actual"] for r in rows.values()}) == 2,
    "an_inverted_rule_would_score_worse":
        sum(("SOUND" if r["edges_per_module"] >= THRESHOLD else "UNSOUND") == r["actual"]
            for r in rows.values()) < hits,
    "training_domains_are_separated_by_the_same_threshold":
        all((d >= THRESHOLD) == (o == "UNSOUND") for d, o in OBSERVED_TRAINING.values()),
    "size_rule_would_mispredict_at_least_one":
        any((r["modules"] < 100) and r["actual"] == "UNSOUND" for r in rows.values()),
}
ok = all(checks.values()) and all(controls.values())
print(json.dumps({"threshold": THRESHOLD, "correct": f"{hits}/{len(rows)}", "rows": rows,
                  "checks": checks, "negative_controls": controls,
                  "status": "PASS" if ok else "FAIL"}, indent=1, sort_keys=True))
for k, v in {**checks, **controls}.items():
    print(f"  {'ok  ' if v else 'FAIL'} {k}")
sys.exit(0 if ok else 1)
