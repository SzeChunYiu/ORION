# ORION-12 route-aware stopping V3 — query-conditional marginal estimator

**Protocol id:** `ORION12.BEIR_ROUTE_AWARE_STOPPING_CONDITIONAL.v3`
**Status:** `DESIGN_FROZEN` — committed before any V3 outcome was computed.
**Parents:** V1 `ROUTE_AWARE_STOPPING_NOT_SUPPORTED`;
V2 `DENSITY_NORMALIZED_STOPPING_NOT_SUPPORTED`.

## Why a third identity, and how its selection was informed

V2 was selected from V1's own diagnosis (absolute threshold vs varying relevance
density). It repaired the NFCorpus never-stop pole and left ArguAna **bit-identical
to V1 at every depth** — lowering the threshold 1.0 → 0.1 changed no stop decision.

**That is diagnostic, not a tuning signal.** For a tenfold threshold change to move
nothing, the quantity being compared must be insensitive to the decision. Reading
V1's code shows why:

```python
rem = {rr: marg[i].get(rr, 0.0) for rr in ROUTE_ORDER[i:]}
if rem and max(rem.values()) < TAU: break
```

`marg[i][rr]` is a development-set mean indexed by **prefix position and route
only**. `qid` never enters it. The stopping decision is therefore **identical for
every query** at a given prefix — the rule cannot adapt to the query in front of it,
which is precisely what a *route-aware* rule was supposed to do.

I disclose plainly that V3's mechanism was chosen after seeing V2's outcome. That
is diagnosis-driven mechanism selection, which the revival doctrine requires. What
it must not become is outcome tuning, so: **the three conditions, corpora,
`split_seed`, `route_order`, `rrf_k`, `patience` and the depth grid are carried over
unchanged, and no parameter is swept.**

## The V3 mechanism

Make the estimator query-conditional. For query `q` at prefix `i`, scale the global
marginal by how much of route `rr`'s list is still unseen **for this query**,
relative to what is typical on dev:

```python
unseen_q  = len(set(lists[q][rr][:d]) - set(seen))
ratio     = unseen_q / max(dev_mean_unseen[i][rr][d], eps)
rem[rr]   = marg[i][rr] * ratio
```

`dev_mean_unseen[i][rr][d]` is computed on the development half only, so no
held-out information enters the decision — the same information boundary V1 set.

The threshold stays **`TAU = 1.0`, V1's original absolute value**. V3 changes the
*estimator*, not the threshold; keeping V1's threshold is what makes the comparison
attributable to the estimator alone. `TAU_REL` and density normalization are **not**
used — V3 is a sibling of V2, not a stack on top of it.

## Endpoints and conditions — carried over verbatim

> - its recall is within `0.02` of `fusion` at equal or lower cost, **and**
> - its false-complete rate is no worse than `generic_active`'s by more than `0.02`, **and**
> - it reads strictly fewer documents than `fusion` at matched recall.

All three, held-out half, pooled over the three corpora. Condition 3 is
operationalized as in V2 (`cost < fusion.cost` and `recall >= fusion.recall` at the
same depth), disclosed there and unchanged here.

## Mandatory control

Same gate as V2: the harness must reproduce V1's frozen numbers first
(150 of 150 cost/recall values; ArguAna@10 cost 10.0 recall 0.6771). If it does
not, report `CANNOT_CHECK_HARNESS_DOES_NOT_REPRODUCE_V1` and make no V3 claim.

## Pre-declared falsifier

If ArguAna remains **identical to V1** under V3, the query-conditional hypothesis is
wrong and must be recorded as such — not rescued by a fourth estimator in the same
round. That outcome would say the per-query unseen-fraction carries no usable signal
at that prefix, which is a stronger and more useful negative than a tuning failure.

## Terminals

- `CONDITIONAL_STOPPING_SUPPORTED` — all three conditions hold, pooled.
- `CONDITIONAL_STOPPING_NOT_SUPPORTED` — any condition fails, with corpus and margin.
- `PROMOTE_CONDITIONALLY__REGIME_LOCAL` — holds on some corpora, fails on others.
  Intermediate under the global-recovery doctrine; owes a further iteration and is
  **not** reportable as success.
- `CONDITIONAL_ESTIMATOR_INERT` — the pre-declared falsifier above fires.
- `CANNOT_CHECK_HARNESS_DOES_NOT_REPRODUCE_V1`.

## Authority

`scientific_authority_delta: NONE`. Successor evidence under a new identity. Cannot
convert V1's or V2's negative into a pending success.
