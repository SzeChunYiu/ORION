"""EXEC-P2-01 independent checker. Does not import the runner.

Every deterministic history-only rule is materialised as an explicit function
table and scored directly, so "no sound rule exists" is verified by exhaustion
rather than argued. The minimum is taken over that explicit list.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent


def main() -> int:
    m = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    g = m["grid"]
    hists, terms = list(range(g["n_hist"])), list(range(g["n_term"]))
    rules = [dict(zip(hists, combo)) for combo in itertools.product(terms, repeat=g["n_hist"])]

    amb = sound = below = exact = 0
    for h in hists:
        for t1, t2 in itertools.combinations(terms, 2):
            amb += 1
            worlds = [(h, t1), (h, t2)]
            errs = []
            for r in rules:
                e = sum(1 for (hh, tt) in worlds if r[hh] != tt) / len(worlds)
                if e == 0.0:
                    sound += 1
                errs.append(e)
            best = min(errs)
            if best < 0.5 - 1e-12:
                below += 1
            elif abs(best - 0.5) < 1e-12:
                exact += 1

    c, b, a = m["classes"], m["bound"], m["assumption"]
    dis = []
    for name, mine, theirs in (("ambiguous_classes", amb, c["ambiguous_classes"]),
                               ("rules_per_class", len(rules), c["rules_per_class"]),
                               ("sound_rules", sound, c["sound_rules_found"]),
                               ("exactly_half", exact, b["exactly_half"]),
                               ("below_half", below, b["min_expected_error_below_half"])):
        if mine != theirs:
            dis.append(f"{name}: mine={mine} theirs={theirs}")

    tight = exact == amb and below == 0
    r = {"schema_version": "orion.independent-checker-receipt.v1", "job_id": "EXEC-P2-01",
         "imports_runner": False,
         "method_difference": "Every rule materialised as an explicit dict function table and scored directly; the universal claim is exhausted rather than argued.",
         "independent_findings": {
             "ambiguous_classes": amb, "rules_per_class": len(rules),
             "sound_history_only_rules": sound,
             "min_expected_error_exactly_half": exact,
             "min_expected_error_below_half": below,
             "bound_is_tight_and_unhedgeable": tight,
             "assumption_strict_improvements": a["strict_improvements"],
             "ambiguity_exists": amb > 0},
         "disagreements": dis,
         "cross_job_note": ("Confirms the disanalogy EXEC-P12-01 identified. In 0/1 error the "
                            "1/2 bound is ATTAINED, with no rule doing better; T17's half-gap "
                            "bound in real-valued loss was beatable by a hedge action. Same "
                            "argument shape, different loss structure, different outcome."),
         "terminal": ("EXEC_P2_01_SECOND_INDEPENDENT_CHECKER_GREEN"
                      if not dis and tight and a["strict_improvements"] > 0
                      else "EXEC_P2_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"),
         "independence_boundary": "Two implementations inside one programme; not external adjudication."}
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r["independent_findings"], indent=2)); print("disagreements:", dis or "none")
    return 0 if not dis and tight else 2


if __name__ == "__main__":
    sys.exit(main())
