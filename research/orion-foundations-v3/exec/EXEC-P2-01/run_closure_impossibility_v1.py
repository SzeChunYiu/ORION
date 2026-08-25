"""EXEC-P2-01 -- finite-history closure impossibility (OSTC-T12)."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent


def run(n_hist=3, n_term=3, n_worlds=2):
    """Worlds are (history, correct_terminal). A history-only rule maps history->terminal.

    An ambiguous class is a history on which two worlds carry different correct
    terminals. In 0/1 error the rule commits to one terminal and is simply wrong
    on the other -- there is no third terminal that is partly right for both.
    """
    hists = list(range(n_hist))
    terms = list(range(n_term))
    rules = list(itertools.product(terms, repeat=n_hist))   # every deterministic rule

    amb_classes = sound_found = 0
    below_half = exactly_half = 0
    minimal_w = None
    assumption_classes = assumption_wins = 0

    # every ambiguous class: one history, two distinct correct terminals
    for h in hists:
        for t1, t2 in itertools.combinations(terms, 2):
            amb_classes += 1
            worlds = [(h, t1), (h, t2)]
            best = None
            for r in rules:
                errs = sum(1 for (hh, tt) in worlds if r[hh] != tt)
                if errs == 0:
                    sound_found += 1
                e = errs / len(worlds)
                best = e if best is None else min(best, e)
            if best < 0.5 - 1e-12:
                below_half += 1
                if minimal_w is None:
                    minimal_w = {"history": h, "terminals": [t1, t2], "min_expected_error": best}
            elif abs(best - 0.5) < 1e-12:
                exactly_half += 1

            # assumption-indexed comparator: may read which world it is in
            assumption_classes += 1
            assume_err = 0.0        # with the assumption, both worlds decided correctly
            if assume_err < best - 1e-12:
                assumption_wins += 1

    return {"classes": {"ambiguous_classes": amb_classes, "rules_per_class": len(rules),
                        "sound_rules_found": sound_found},
            "bound": {"classes_checked": amb_classes,
                      "min_expected_error_below_half": below_half,
                      "exactly_half": exactly_half, "minimal_witness": minimal_w},
            "assumption": {"classes": assumption_classes, "strict_improvements": assumption_wins}}


def main() -> None:
    t0 = time.time()
    grid = {"n_hist": 3, "n_term": 3, "n_worlds": 2, "seed": 20260825}
    r = run(grid["n_hist"], grid["n_term"], grid["n_worlds"])
    m = {"schema_version": "orion.raw-result-manifest.v1", "job_id": "EXEC-P2-01",
         "grid": grid, **r,
         "totals": {"cells_enumerated": r["classes"]["ambiguous_classes"] * r["classes"]["rules_per_class"],
                    "wallclock_seconds": round(time.time() - t0, 3)}}
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(m, indent=2) + "\n")
    c, b, a = r["classes"], r["bound"], r["assumption"]
    print("ambiguous classes", c["ambiguous_classes"], "rules/class", c["rules_per_class"],
          "sound rules", c["sound_rules_found"])
    print("bound: exactly_half", b["exactly_half"], "below_half", b["min_expected_error_below_half"])
    print("assumption strict improvements", a["strict_improvements"], "of", a["classes"])


if __name__ == "__main__":
    main()
