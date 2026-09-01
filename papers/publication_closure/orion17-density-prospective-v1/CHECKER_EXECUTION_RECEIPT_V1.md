# ORION-17 — independent checker execution receipt

**Executed:** 2026-08-29 on **LUNARC**, by the ORION-17xx orchestration lane, from a fresh
checkout of `wk/p0-evidence-20260829` at commit `787b6274`, LUNARC venv, Python 3.11.5.
**Not executed on the author's workstation.** Transcript retained by the orchestrator.

**Authority label:** `IMPLEMENTATION_INDEPENDENT`. This is **not** external verification
and **not** independent-investigator replication — same programme, same researcher,
different machine. `scientific_authority_delta = NONE`.

**Applicability to this tree:** `theory/density-prospective-v1/` is **byte-unchanged**
between `787b6274` and the current branch head
(`git diff --name-status 787b6274 HEAD -- <this dir>` returns nothing), so the run attests
exactly the artifacts committed here.

## Result — exit 0 (not 3), `"status": "PASS"`, `"correct": "5/5"`

`independent_checker/check_density_prediction.py` re-derived the verdict from the recorded
files. It imports no ORION-17 module and re-runs no campaign. Exit code 3 is its reserved
`CANNOT_CHECK` signal and was not returned.

`"threshold": 1.5` — the checker read the frozen threshold from the stamped document
rather than being given one.

| package | modules | edges/module | predicted | actual | donor false ret. | exact false ret. |
|---|---|---|---|---|---|---|
| requests | 19 | 0.8421 | SOUND | **SOUND** | 0 | 0 |
| networkx | 583 | 2.1355 | UNSOUND | **UNSOUND** | 91,507 | 0 |
| django | 906 | 3.6821 | UNSOUND | **UNSOUND** | 63,398 | 0 |
| tornado | 74 | 5.5676 | UNSOUND | **UNSOUND** | 12,773 | 0 |
| sympy | 1,566 | 8.6986 | UNSOUND | **UNSOUND** | 344,352 | 0 |

Every row matches `HELD_OUT_RESULT.json` and the manuscript tables exactly.

## All four checks and all four negative controls fired

Checks: `all_five_predictions_correct`, `tornado_the_disambiguator_is_correct`,
`tornado_is_small_but_dense`, `exact_containment_never_falsely_retains` — all `true`.

Negative controls — all `true`:

- `both_outcome_classes_occur_in_the_held_out_set` — the corpus is not degenerate.
- `an_inverted_rule_would_score_worse` — the rule beats its own inversion.
- `training_domains_are_separated_by_the_same_threshold` — 1.5 separates the calibration
  set too, so it was not fitted only to the held-out outcomes.
- **`size_rule_would_mispredict_at_least_one`** — this is the disambiguation, checked
  mechanically rather than argued: a size-based rule *does* misfire on this corpus, which
  is precisely the tornado case the stamped document registered in advance.

The controls firing is what makes the `PASS` meaningful: a checker that returned `PASS`
with its negative controls silent would not have discriminated anything.
