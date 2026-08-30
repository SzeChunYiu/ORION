# ORION-02 CC18 certifiability — findings V1

**Terminal: `CERTIFIABILITY_DISCRIMINATOR_NOT_SUPPORTED`**, and it fails on exactly
one of the three predeclared clauses. The other two hold, and which one fails is
the result.

## The three clauses

| clause | required | observed |
|---|---|---|
| coverage `>= 0.90` on every stratum | yes | **holds** — minimum 0.993 |
| prediction matches observation | yes | **holds** — 4 of 4 strata |
| `theorem_minimal` width no worse than `distance_proxy` | yes | **fails** |

## The theorem's predictive content is confirmed, including a real tie

| stratum | predicted | observed | min coverage | width, theorem | width, proxy |
|---|---|---|---|---|---|
| `binary_small` | **no value** | **no value** | 1.000 | 2.00 | 2.00 |
| `binary_wide` | value | value | 1.000 | **1.92** | 1.99 |
| `multiclass_small` | value | value | 1.000 | 2.90 | **2.64** |
| `multiclass_wide` | value | value | 0.993 | 8.00 | **7.80** |

`binary_small` is a genuine no-value stratum: the criterion, computed from
calibration data alone, says refinement cannot narrow the certificate, and it does
not — width stays at 2.00, identical to `coarse`. That is the "not" side of the
biconditional actually landing, which is what the contrast requirement exists for.
The prediction was right on all four.

## What fails, and it is the prescriptive half

The theorem says *when* refining helps. It also prescribes *how* — refine where a
fibre's labels are not constant, here as an equal-frequency binning of the
highest-mutual-information feature. At equal fibre budget (`K = 4` for every arm),
that prescription is **beaten by k-means on standardised features, which never
looks at a label at all**: 2.90 against 2.64 on `multiclass_small`, 8.00 against
7.80 on `multiclass_wide`.

It wins on `binary_wide` (1.92 against 1.99) and ties on `binary_small`. So the
prescription is not useless — it is beaten wherever there are more than two
classes.

The reading is that the theorem's **predictive** content survives contact with
fresh heterogeneous data and its **prescriptive** content does not. A practitioner
should use the criterion to decide whether to refine, and should not use the
refinement it suggests.

## Not rescued

The protocol froze `K = 4`, the split seed, the strata and the 0.90 gate, and said
failure is terminal and not to be repaired by re-binning, re-splitting or changing
`K`. Raising `K` for `theorem_minimal` alone would win the width comparison and
would be exactly the manoeuvre the freeze forbids. Nothing was changed.

## Standing record, untouched

This is a new prospective identity. It consumed **no** revival-ledger slot. R23
(`C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`) and R24
(`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`) stand as recorded, their corpora were
not touched, and nothing here rescues, reopens or reinterprets them. This negative
is independent of theirs and is about a different question on different data.

12 CC18 datasets, task ids frozen by metadata before any fetch, 50/50 calibration
split at seed 20260830.
