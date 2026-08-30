# Checking the eleven "needs fixing" diagnoses against emitted data

Three of the eleven carried enough per-example data to check the diagnosis rather than act
on it. **Two of the three did not survive.** In both cases a real defect exists — it is a
different defect from the one assigned, and in one case it is the defect assigned to a
different paper.

This matters before anyone re-runs a campaign: the corrective action follows from the
diagnosis, and two of three diagnoses pointed at the wrong stage.

## Triage — can the diagnosis be checked without re-running?

| paper | per-example rows | status |
|---|---:|---|
| ORION-14 | 4,200 | checked — **diagnosis held**, fixed by re-analysis |
| ORION-11 | 19,022 | checked — **diagnosis did not hold** |
| ORION-24 | 67 packets × 2 systems | checked — **diagnosis did not hold** |
| ORION-17 | 432 | checked — **diagnosis held**, genuinely blocked on external data |
| ORION-05 | 120 | needs the V2 campaign (LUNARC) |
| ORION-13 | 48 | too few — must re-run |
| ORION-02 | 13 | must re-run; confirms "lacks serialized paired data" |
| ORION-19 | 0 jsonl | must re-run |

## ORION-14 — held. Fixed by re-analysis, no re-run.

Uncertainty was understated exactly as described. The published interval is case-level;
at the clustering unit the half-width is 5.48× wider. The effect survives (12 clusters,
6 discordant all favouring ORION, exact p = 0.031). Detail in the paper's
`analysis/cluster-respecting-reanalysis-v1/`.

## ORION-11 — did not hold

Diagnosed as *"10/11 comparisons cannot distinguish full ORION from the comparator;
several ablations behave identically."* Measured from the experiment's own traces:

- **No arm is behaviourally inert.** Highest identical-action-trace rate against ORION is
  18.1%; the oracle and faithful Active-VOI share 0%.
- **6 of 6 comparisons discriminate** on the criterion `PROTOCOL.json` freezes, all
  favouring ORION (exact McNemar log₁₀p from −4.8 to −206.4).
- The "10/11" is not an ablation result at all. It is a **shortcut probe** in
  `MECHANICAL_SOLVABILITY_AUDIT_V1.md`: a regex on resource path stems recovers 10 of 11
  DECOMPOSITION cases at precision 1.00, 0/55 false positives.

**Real defect: corpus leakage.** The benchmark encodes its answer in resource filenames.
Redesigning the ablations would not touch it.

## ORION-24 — did not hold

Diagnosed as *"apparent advantage concentrated in one designed RETAIN_NEGATIVE stratum."*
Measured over the 67 gold-labelled packets:

| family | n | SYSTEMA | SYSTEMB | gap |
|---|---:|---:|---:|---:|
| APPARENT_POSITIVE_SUBSUMED | 12 | 0 | 12 | +12 |
| NEGATIVE_RETAINED | 9 | 0 | 9 | +9 |
| LEAKY_OR_CORRUPT_BENCHMARK | 7 | 0 | 7 | +7 |
| NULL_LIVE_PARENT | 9 | 0 | 7 | +7 |
| NON_IDENTIFIABLE | 6 | 2 | 6 | +4 |
| REGIME_CHANGE_REOPEN | 6 | 0 | 3 | +3 |
| INTERACTION_ONLY | 7 | 0 | 1 | +1 |
| STRONG_PROMOTABLE | 11 | 11 | 11 | 0 |
| **total** | **67** | **13** | **56** | **+43** |

The advantage spans **7 of 8 families**. `NEGATIVE_RETAINED` contributes 9 of 43 — **21%**,
not a concentration.

**Real defect: the comparator is degenerate.** SYSTEMA emits `PROMOTE` on **65 of 67**
packets (the other 2 are `CANNOT_CHECK`), against a gold distribution spanning 8
dispositions. Beating an always-promote baseline establishes very little, and the 11/11 tie
on `STRONG_PROMOTABLE` is exactly what an always-promote system scores by construction.

Note this is the defect assigned to **ORION-13** ("the baseline is effectively always-merge
on the tested corpus"). It is present here too, and here it is measurable.

## ORION-17 — held

Diagnosed as needing the larger disagreement study because simpler rivals (module/edge
count) can explain the same projects. Checked whether it could be settled in-tree: **no
ORION-17 file mentions `density` at all** (control: the same search finds 8 `domain`
matches in `benchmark/instances_v1.jsonl`, so the search works). The benchmark holds 8
instances with no density, module or edge fields. Repo-wide, density-and-modules co-occur
only in archived math-evaluation papers.

`CANNOT_CHECK_NO_IN_TREE_PREDICTORS` — the external cohort is genuinely required, as
diagnosed.

## What follows

1. **Check before re-running.** Two of three checkable diagnoses were wrong, and both
   pointed at a stage that would not have been repaired by the prescribed fix.
2. **Degenerate comparators are the recurring defect**, confirmed in ORION-24 and alleged
   in ORION-13 and ORION-19. That is one design fault, not three.
3. **ORION-13 and ORION-19 should be measured the same way before re-running** — but
   neither emits enough per-example data (48 rows; 0 jsonl), which is itself the finding:
   the emission gap is what forces a re-run.
