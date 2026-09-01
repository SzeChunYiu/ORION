# V5 — the fibre-constancy question, over the unselected population

**Status at time of writing:** `PROTOCOL_FROZEN__NOT_YET_COMPUTED`
**Scientific authority delta:** `NONE`.

## The open question, in V1's own words

`vocabulary-minimality-v1/BPRIME_FIBRE_CRITERION_V1.json` terminates
`CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` and says why:

> The 64 serialised witnesses are selected on `C_D++ < min(C_D+, f_B')`. Cost constancy
> within an `f_B'` fibre on a gap-selected subset [cannot settle the criterion.]

and states what would settle it:

> Serialise `f_B'` and `C_D++` for all 740 evaluated instances, not only the 64 candidates,
> and re-run this fibre grouping over the unselected population.

On those 64 the relationship looked exact and uniform: `C_Dxx = f_B' − 1` in all 64,
`C_D+ − C_Dxx = 1` in all 64, `C_DP = C_Dxx` in all 64.

## Why this can be answered now without a new run

The V4 per-panel-dedupe run (SLURM 3561900, receipt committed at
`../vocabulary-minimality-v4-per-panel-dedupe/RUN_3561900_RAW.json.gz`, decompressed sha256
`28a760c7…7857f`) serialises `full_census_rows_v2`: **13,458 rows**, each carrying `C_DP`,
`C_Dplus`, `C_Dxx`, `f_Bprime`, `gap4`, `panel` and `regime`, across all ten panels.

That is the unselected population V1 asked for, and eighteen times the 740 it hoped for. No
new computation is required; the data is already committed.

## The criterion

From `certificate-explanation-gap-v1/THEORY.md` Theorem 2, as V1 quotes it: an exact
Ψ-only explanation exists **iff cost is constant on every Ψ-fibre**. Here the fibre key is
`f_Bprime` and the cost is `C_Dxx`.

So: group all 13,458 rows by `f_Bprime`, and ask whether `C_Dxx` is constant within every
group.

## Terminals

- `FIBRE_CONSTANCY_HOLDS_ON_UNSELECTED_POPULATION` — `C_Dxx` is constant within every
  `f_Bprime` fibre. V1's `CANNOT_CHECK` resolves to supported.
- `FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION` — at least one fibre carries two
  distinct `C_Dxx` values. V1's `CANNOT_CHECK` resolves to refuted, and the uniformity seen
  on the 64 was a selection artefact.
- `CANNOT_CHECK_INSUFFICIENT_SERIALISATION` — the receipt does not carry both fields for
  every row.

## Prediction, recorded before computing

**`FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION`.**

The 64 witnesses were selected on `C_Dxx < min(C_D+, f_B')`, a condition that constrains the
relationship between exactly those quantities. A subset chosen by a predicate over `C_Dxx`
and `f_B'` will tend to show a tight relationship between `C_Dxx` and `f_B'` whether or not
the population does, which is the reason V1 refused to conclude from it. If the full census
also shows constancy, the selection was harmless and the criterion is met.

Secondary prediction: the `borrow`, `split` and `tie` regimes — 12,875 of the 13,458 rows,
none of which satisfy the selection predicate — are where the violations will be found, and
the 583 `fourth` rows will continue to look uniform.

## What the answer will not establish

Either way this is a statement about the frozen unit-cost R6M grammar and the ten registered
panels, not about all `n`. It carries no novelty credit and moves no other terminal. V1's
own `promotes_no_claim: true` continues to apply.
