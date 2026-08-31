# ORION-21 query-family capability successor V2 — findings

**Terminal:** `QUERY_FAMILY_CAPABILITY_ESTIMATED`
**Parent terminal unchanged:** `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET`

## Stage A — the frozen result reproduces

The `|S|=1` stratum re-derives V1 exactly, on a different machine
(`billy-laptop-old`) and a different stack (Python 3.14.4 / scikit-learn 1.9.0 /
numpy 2.4.6, against V1's recorded 1.7.1 / 2.3.2):

| access class | recomputed | V1 recorded | matches |
|---|---|---|---|
| LINEAR | 3/10 | 3/10 | yes |
| RBF | 5/10 | 5/10 | yes |
| KNN | 5/10 | 5/10 | yes |

The resulting intervals also agree with `GATE_DESIGN_POWER_V1` to three decimals
(LINEAR `[0.067, 0.652]`, RBF and KNN `[0.187, 0.813]`), so the two studies
independently validate each other.

## Stage B — the unresolved band is now resolved

`GATE_DESIGN_POWER_V1` could exclude the registered capability level but not the
0.6–0.8 band, where the `>=8/10` gate had 17–68% power. With 55 responsibilities
instead of 10, **all three pooled intervals lie entirely below 0.6**:

| access class | pooled | point | 95% Clopper–Pearson |
|---|---|---|---|
| LINEAR | 7/55 | 0.127 | **[0.053, 0.245]** |
| RBF | 21/55 | 0.382 | **[0.254, 0.523]** |
| KNN | 23/55 | 0.418 | **[0.287, 0.559]** |

The V1 negative moves from "below the registered bar, location unknown" to a
bounded quantity. Capability is not near-miss: for LINEAR the upper bound is
0.245, well under half the registered bar.

## The new structural finding: capability falls as responsibility complexity rises

The two strata separate in the same direction for every access class, and the
mean quality delta worsens with them:

| access class | `\|S\|=1` capability | `\|S\|=2` capability | mean Δ `\|S\|=1` | mean Δ `\|S\|=2` | worst Δ `\|S\|=2` |
|---|---|---|---|---|---|
| LINEAR | 0.300 | 0.089 | −0.0338 | −0.0571 | −0.1563 |
| RBF | 0.500 | 0.356 | −0.0254 | −0.0306 | −0.1216 |
| KNN | 0.500 | 0.400 | −0.0267 | −0.0300 | −0.1092 |

A 16-of-64 compiled state loses more of the universal state's accessible content
as the responsibility becomes structurally richer, and it loses it fastest under
the linear decoder. The V1 access-class ordering survives the enlargement:
LINEAR is worst, the nonlinear and local decoders recover more from compiled
state — consistent with ORION-21's placement reading that stronger downstream
access buys back part of the work moved into state construction.

## What this does not do

- It does **not** rescue the V1 gate. V1's `>=8/10` terminal is untouched and no
  claim is promoted; `P11_ACTIVE_CLAIM_AUTHORITY_V2.json` remains the authority.
- It does **not** close the readiness checklist item "learned non-oracle
  compiler." That item asks for a learned compiler that *works* at family scale.
  This result is evidence in the opposite direction, now with a sharp bound.
- Responsibilities within a stratum share one dataset and one fold split, so
  these are nominal binomial intervals; the dependence is stated, not modelled
  away. A design with independent source datasets would be the next tightening.
