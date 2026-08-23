# P11I wide high-width replication — development packet

Base: `claude/papers-1-10-issues-uqrj2o@fd9892fdafd7734b07c8b24a4384c9e9561b1349`
Status: `PRE_OUTCOME_FREEZE`

## Question

P11H showed that the pooled universal attack wins at compiled-state width
`r=3` and loses at `r=7`, but its protected seed drew only two `r=3` cells and
therefore returned `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`. Does the positive
high-width regime replicate across fresh seeds and the complete three-geometry
bank-width cross while the same pooled attack still wins in matched `r=3`
controls?

## Design

- exact 2×3 factorial: state widths `{3, 7}` × bank geometries
  `{(14,2), (14,3), (19,3)}`;
- three fresh frozen data seeds: `2026082241`, `2026082242`, `2026082243`;
- five protected queries per cell, averaged only within cell;
- independent inferential unit: `(seed, bank geometry)`; query repetitions are
  technical measurements and never increase `n`;
- same five arms, training sizes, target, test size, seeding, and best-of-three
  universal attack as P11H;
- two full fresh-process executions must be byte-identical.

## Non-compensatory decision rule

Every one of the nine high-width cells must satisfy all three conditions:

1. compiled L2 accuracy at `n=64` is at least `0.95`;
2. the pooled universal attack remains strictly below `0.95` at every registered
   size below `n=256`;
3. compiled-minus-pooled accuracy at `n=64` is at least `0.20`.

Every matched low-width cell must show the pooled attack reaching `0.95` below
`n=256`. Any answer-laundering event, dead low-width attack, or replay mismatch
is an instrument failure, not a scientific negative.

No average across seeds, geometries, queries, or gates can rescue a failed
cell. No threshold, seed, geometry, arm, or denominator may change after this
freeze.

## Claim boundary

A pass supports only replication of a low-sample compiled-state advantage in
the registered `r=7` parity-majority regime against the strongest of the three
registered universal decoders. It does not relabel P11D or P11H, establish a
universal lower bound, or imply superiority in real agents.
