# R24's control violation comparison is not checkable from committed data

**Date:** 2026-08-29 · **Disposition:** `CANNOT_CHECK` · **Terminal:** unchanged

R24's manuscript paragraph states that the matched no-geometry lexical control also
reached `44/44` coverage **"with fewer violations than the geometric arm (14 versus
20), so the registered geometry again supplied no measured advantage on that corpus."**

That is the same shape as R23's control claim, which was reported from bare counts and
has since been given a paired exact test (`../r23-density-backoff-revival/R23_CONTROL_PAIRED_TEST_V1.json`).
The same treatment was attempted here and **could not be completed from the committed
artifact.** This note records why, so the gap is visible rather than silently absent.

## What is tested in R24, and what is not

R24 does test its control — but on a different quantity:

- `negative_control_test` compares `R24_PRIMARY_LEARNED` against
  `R24_LEXICAL_MATCHED_PRIMARY` on **mean excess**, with 20,000 bootstrap replicates,
  `mean_diff = +0.000323174048`, interval `[0.0, 0.000969522145]`, and per-dataset
  differences retained.
- The **violation** comparison — `violations_strict` 20 versus 14 — has no test. It is
  the comparison the manuscript sentence actually relies on, and it is also the quantity
  that decides the terminal, since `20/44 = 0.4545` exceeds the registered maximum
  violation rate of `0.10`.

## Why it cannot be tested from what is committed

A paired test needs per-dataset violation flags for the two **policy** arms. The
artifact does not carry them. `coverage_records` holds per-dataset records for two
arms, but they are the **fibre-construction** arms — `R24_ARM_CONDITIONAL_BOUNDARY_FIBRES`
and `R24_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL` — whereas `violations_strict` is
reported in `arms_summary` for the policy arms `R24_PRIMARY_LEARNED` and
`R24_LEXICAL_MATCHED_PRIMARY`, which have aggregate summaries only.

A reconstruction was attempted and **rejected on validation before use**: deriving a
violation per dataset as `outcomes[ds]["best"] - outcomes[ds][best_arm] > best_bound`
over `coverage_records` yields **0 violations for both arms**, against published counts
of 20 and 14. The reconstruction therefore does not model the published quantity and
was discarded rather than reported. No paired test is offered here, and none should be
inferred.

## What this means

Both arms fail the registered gate regardless: `20/44 = 0.4545` and `14/44 = 0.3182`
are both far above the `0.10` maximum violation rate. So
`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` stands on the primary arm's own number and
does not depend on the comparison with the control. **Nothing here revives R24.**

What the gap does affect is the *strength* of the accompanying claim. As committed, an
independent reader cannot check whether 14 versus 20 is a real difference or sampling
noise on 44 paired datasets, because the per-dataset inputs are not published. The
sentence should therefore be read as a descriptive count, not an established
comparison — the same correction applied to R23, where the analogous gap *was* closable
and the difference turned out **not** to be significant (`p = 0.0923`).

## The emitter already computes it and then discards it

This is an emission gap, not a measurement gap, and the round's own committed emitter
shows it. In `fiberguard_pmlb_arm_conditional_r24.py` the per-dataset flag is built for
every row:

```python
"violation_strict": bool(
    decision["certified"] and excess > float(bound) + TOL
),
```

and is then consumed only in aggregate:

```python
"violations_strict": sum(bool(row["violation_strict"]) for row in certified),
```

The per-row `rows` mapping that carries `excess`, `bound` and `violation_strict` for
each dataset is never serialised; only `arm_summary`'s totals reach the artifact. So the
quantity a paired test needs existed at run time and was dropped at write time.

It is not recoverable from what was published. `negative_control_test` retains
per-dataset excess *differences* between the two policy arms, but a violation is a
threshold on each arm's *absolute* excess against its own bound, and neither absolute
excesses nor per-arm bounds are emitted per dataset.

## To close this

Serialise the existing per-row `violation_strict`, `excess` and `bound` for the policy
arms alongside `coverage_records`. No science changes: the values are already computed
on the path above, and the change is to write them out. That would make both the R24
control comparison and the round's violation rate independently checkable, and would let
the R23 paired test be repeated here.
