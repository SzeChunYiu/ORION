# ORION-12 route-aware stopping V2 — relevance-density-normalized threshold

**Protocol id:** `ORION12.BEIR_ROUTE_AWARE_STOPPING_DENSITY.v2`
**Status:** `DESIGN_FROZEN` — written and committed **before** any V2 outcome was
computed and before the corpora were fetched into this working tree.
**Parent:** `beir-route-aware-stopping-v1`, terminal
`ROUTE_AWARE_STOPPING_NOT_SUPPORTED`.

## Why a new identity rather than a re-run

V1 forbids rescue in its own words: the negative is *"not rescued by re-tuning
`P`, `k`, the depth grid or the overlap statistic, all of which are frozen"*.
This protocol therefore re-tunes **none** of them. Corpora, `split_seed`,
`route_order`, `rrf_k`, `patience` and the depth grid are carried over unchanged.

Exactly **one** thing changes, and it is a change of mechanism, not of a knob.

## The defect being repaired

V1's stopping rule is

```python
TAU = 1.0          # "expected < one new relevant document"
if rem and max(rem.values()) < TAU:   # stop
```

`TAU` is an **absolute count of documents**. V1's own findings attribute the
failure to exactly this: the rule *"stops when no unread route is expected to
contribute one new relevant document — an absolute count"*, while the number of
relevant documents per query differs by an order of magnitude across corpora.
The result is bimodal and never adaptive:

- **ArguAna** (≈1 relevant/query) — stops after the first route every time, at
  every depth, and gives up 0.101 recall against fusion.
- **NFCorpus** — never stops; cost equals the exhaustive oracle's.
- **SciFact** — sits behind fusion at four of five depths.

A single absolute threshold cannot be simultaneously correct at both poles. That
is a specification error, not a tuning shortfall.

## The V2 mechanism

Normalize the threshold by the corpus's own relevance density:

```python
D_dev  = mean number of relevant documents per query, development half only
TAU_REL = 0.1                      # declared once, below
threshold = TAU_REL * D_dev
if rem and max(rem.values()) < threshold:   # stop
```

**Estimator:** `D_dev` is the development-split mean relevant-documents-per-query.
The development half is already the only data V1's overlap statistic may see, so
this introduces no new information channel and no held-out leakage.

**`TAU_REL = 0.1`, declared here, single value, no sweep.** The mechanism
argument fixes it: the rule should stop when no unread route is expected to add
even a tenth of a typical query's relevant set. This is directionally correct at
both failing poles by construction — at `D_dev ≈ 1` the threshold falls below
V1's 1.0 so the rule stops *less* eagerly, and at `D_dev > 10` it rises above 1.0
so the rule stops *more* eagerly. No value of `TAU_REL` was chosen by looking at
a V2 outcome, because none had been computed when this file was committed.

If a sweep is ever run it must be declared as a sweep with a pre-committed
selection rule and every cell reported; this protocol declares none.

## Endpoints and conditions — carried over verbatim from V1

Unchanged, quoted from `../beir-route-aware-stopping-v1/PROTOCOL_V1.md`:

> - its recall is within `0.02` of `fusion` at equal or lower cost, **and**
> - its false-complete rate is no worse than `generic_active`'s by more than
>   `0.02`, **and**
> - it reads strictly fewer documents than `fusion` at matched recall.

All three, on the held-out half, pooled over the three corpora.

## Mandatory control, run before the V2 arm is believed

The harness must first reproduce V1's frozen numbers. Required agreement:

- corpus zip SHA-256 equal to V1's recorded `zip_sha256`;
- `route_aware_stop` on ArguAna at depth 10 → cost `10.0`, recall `0.6771`;
- V1's three conditions still evaluate to failing.

**If the control does not reproduce, the study reports
`CANNOT_CHECK_HARNESS_DOES_NOT_REPRODUCE_V1` and no V2 claim is made.** An
improvement measured by a harness that cannot reproduce the frozen negative is a
property of the harness, not of the mechanism.

## Terminals

- `DENSITY_NORMALIZED_STOPPING_SUPPORTED` — all three conditions hold, pooled.
- `DENSITY_NORMALIZED_STOPPING_NOT_SUPPORTED` — any condition fails, recorded
  with the failing corpus and margin.
- `PROMOTE_CONDITIONALLY__REGIME_LOCAL` — conditions hold on some corpora and
  fail on others, e.g. the normalization repairs one pole and breaks the other.
  Under the global-recovery doctrine this is **intermediate, not terminal**: it
  owes a further revival iteration and must not be reported as a success.
- `CANNOT_CHECK_HARNESS_DOES_NOT_REPRODUCE_V1` — as above.

## Authority

`scientific_authority_delta: NONE` until executed. This protocol grants no claim,
does not alter ORION-12's frozen terminal, and does not touch its
`journal_package/`. A V2 result, whatever it is, is successor evidence under a new
identity — it does not retroactively convert V1's `ROUTE_AWARE_STOPPING_NOT_SUPPORTED`
into a pending success.
