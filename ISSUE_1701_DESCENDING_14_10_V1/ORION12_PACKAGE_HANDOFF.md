# ORION-12 package handoff

Live `main` already records the honest bounded IP&M track:

- recall@100 difference `-0.0177`, bootstrap interval
  `[-0.0273, -0.0091]`: the noninferiority gate fails;
- read cost `2.8x` the comparator: the cost gate fails;
- nDCG@10 `+0.1488`, interval `[+0.1010, +0.1995]`, ahead on 42/50 topics:
  favourable but non-gating and therefore not a rescue;
- two of five routes remain unavailable.

The closeout head `ae670d943228ea07b53de28a1a1c174a4f1494c5`
binds review PDF `e23e853d...`; live main binds `90e424cf...`.
The closeout's `current_revision/` package is not present on live main. Use the
editorial/audit material as a donor, then rebuild and re-bind exact live bytes.
Do not upload the old archive as though it represented current source.
