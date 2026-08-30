# ORION-21 split-clustered capability — findings V3

**Terminal: `CAPABILITY_SURVIVES_SPLIT_CLUSTERING`.** Estimation study. It
declares no gate and promotes no ORION-21 claim; V1's `>=8/10` family-scale
negative and `P11_ACTIVE_CLAIM_AUTHORITY_V2` stand exactly as they are.

## What V2 could not do, and what V3 does

V2 reported a capability band from a **single fold seed** over a 55-responsibility
family. Its interval was a binomial one on `n = 55`: **[0.053, 0.245]**, width
**0.192**. Two things were wrong with it. The interval is nine times wider than the
question needs, and — more importantly — the binomial treats 55 responsibilities
scored under one fold split as 55 independent draws, which they are not.

V3 runs **20 fixed seeds** (`20261121 … 20261140`), takes the **seed** as the
clustering unit, and resamples seeds rather than responsibilities in the bootstrap.

| decoder | capability | seed-clustered 95% CI | width |
|---|---|---|---|
| LINEAR | 0.152 | [0.141, 0.162] | 0.021 |
| RBF | 0.400 | [0.389, 0.411] | 0.022 |
| KNN | 0.389 | [0.378, 0.400] | 0.022 |

All three read `BELOW_0.6__SURVIVES_CLUSTERING`. Pooled `n = 1100` over 20 seeds.

**The narrowing is not a statistical trick and should not be read as one.** The
clustered interval is not narrower than a binomial on the same data; it is
narrower than V2's binomial on **one twentieth of the data**. The width came down
because there are twenty times more responsibilities, and the clustered bootstrap
is what makes that width honest given they are not independent.

That the seed is a real unit is visible in the data: per-seed capability ranges
**0.109 to 0.200** for LINEAR, a spread far too large to treat a single seed's
figure as the population value. V2 did, and that is the limitation V3 was written
to remove.

## What this changes and what it does not

It tightens a **negative**. The compiled state's capability over a 55-member query
family is 0.152 under LINEAR and about 0.39–0.40 under the two stronger decoders,
all decisively below 0.6, and that conclusion no longer rests on one draw. The
family-scale claim that failed in V1 fails more clearly, not less.

`parent_unchanged: True` — the V2 record is not edited, replaced or rescued.

## What is not addressed

**One shared dataset.** Among the datasets reachable without network access, only
`digits` has the `d >= 16` feature count and the class count the mechanism needs.
Seed-level independence is established here; **dataset-level independence is out
of reach and is not claimed.** A successor that varies the dataset would be
testing something this study cannot.

Protocol SHA-256 `b7b5a2e9951fcb188e7d8f319030624fe547b6b6cbc7dc5494e8de8ea4fee001`;
run on `billy-laptop-old`, Python 3.14.4, numpy 2.5.2, scikit-learn 1.9.0.
