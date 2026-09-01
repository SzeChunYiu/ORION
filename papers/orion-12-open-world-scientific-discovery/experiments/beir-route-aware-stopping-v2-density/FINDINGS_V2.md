# ORION-12 density-normalized stopping V2 — findings

**Terminal: `DENSITY_NORMALIZED_STOPPING_NOT_SUPPORTED`.**
15 of 15 held-out cells fail at least one of the three frozen conditions.

## The control passed twice, independently

The protocol gated every V2 claim on first reproducing V1's frozen numbers.

- Local reproduction: **150 of 150 (cost, recall) values identical**, 0 mismatches.
- LUNARC reproduction (job 3560191): **150 of 150 identical**, 0 mismatches.
- Corpus zips match V1's recorded SHA-256 on both machines.
- Protocol checkpoint met exactly: ArguAna@10 `route_aware_stop` cost 10.0, recall 0.6771.

The V2 numbers below are therefore a property of the mechanism, not of the harness.

## One pole repaired, the other untouched

`threshold = TAU_REL * D_dev`, with `TAU_REL = 0.1` frozen before execution.

**NFCorpus (`D_dev = 38.63` → threshold 3.86).** V1's defect was that the rule
never stopped and cost *more* than fusion at every depth. V2 repairs it:

| depth | fusion | V1 | V2 |
|---|---|---|---|
| 10 | r .1381 / c 9.96 | r .1707 / c 19.52 | r .1375 / c **7.83** |
| 50 | r .2072 / c 49.39 | r .2399 / c 82.69 | r .1885 / c **34.08** |
| 200 | r .2888 / c 195.67 | r .3280 / c **279.36** | r .2454 / c **112.06** |

At depths 10, 20 and 50 V2 satisfies condition 1 — recall within 0.02 of fusion at
strictly lower cost — which no arm achieved on NFCorpus under V1. At depth 200 the
recall deficit is 0.043, past the frozen 0.02 margin.

**ArguAna (`D_dev = 1.0` exactly → threshold 0.1). V2 is identical to V1 at every
depth.** The normalization changed nothing on the pole it was equally meant to fix.

**SciFact (`D_dev = 1.13` → threshold 0.11).** Also identical to V1 at every depth.

## The deeper defect this exposes, which V1 did not name

V1 attributed its failure to the threshold being an absolute count. V2 confirms
that in one direction: raising the threshold where density is high genuinely
repairs the never-stop pole.

But lowering the threshold from 1.0 to 0.1 on ArguAna changed **no stop decision at
all**. For that to be true, the rule's estimated maximum marginal contribution must
already sit below 0.1 — essentially zero. So on ArguAna the defect is **not the
scale of the threshold but the informativeness of the estimator feeding it**: the
frozen rank-overlap statistic predicts near-zero new relevant documents for every
unread route, so no threshold in any sensible range keeps the rule reading.

That is a different lever from the one V2 tested. It is recorded here and **not
acted on** — acting on it now would be choosing a second mechanism after seeing
V2's outcome.

## Why this is not a conditional promotion

The NFCorpus repair is real and large, and it would be easy to present as
`PROMOTE_CONDITIONALLY__REGIME_LOCAL`. It does not qualify: **all 15 cells fail at
least one condition**, including every NFCorpus cell on conditions 2 and 3. A
corpus-local improvement inside a globally failing gate is not a conditional pass.

## Operationalization disclosed

Conditions 1 and 2 are direct. Condition 3 — *"reads strictly fewer documents than
fusion at matched recall"* — was operationalized as `cost < fusion.cost` **and**
`recall >= fusion.recall` at the same depth. That is a strict reading; a weaker
interpolated reading of "matched recall" could flip condition 3 on individual
cells. It cannot change the terminal, because condition 1 already fails on all five
ArguAna cells and at NFCorpus depth 200.

## Authority

`scientific_authority_delta: NONE`. Successor evidence under a new identity. It
does not alter ORION-12's frozen terminal and does not convert V1's
`ROUTE_AWARE_STOPPING_NOT_SUPPORTED` into a pending success.
