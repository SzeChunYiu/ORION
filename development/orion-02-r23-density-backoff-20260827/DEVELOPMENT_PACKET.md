# ORION-02 R23 density-backoff development packet

Date: 2026-08-27

## Atomic development questions

1. Is R22's zero full-state coverage caused by exact-cell sparsity rather than
   by the learned scorer?
2. Can the smallest nontrivial, outcome-independent backoff pool restore
   coverage while retaining exact worst-case computation over selected shield
   members?
3. After applying the same valid fallback evaluator to parent and revival, is
   learned ordering valuable against the matched static arm?

## Incumbent mechanics and negative history

R22 is preserved at `d49f6905`. Its exact-cell coverage is zero. Its terminal
is therefore adverse on coverage. A separate evaluator defect used a scalar
grand mean as F* and made fallback excess negative; those performance values
cannot be promoted. The corrected exact-cell parent and R23 both use the same
executable F* arm correction.

## Bounded saturation assessment

- **Knowledge:** the incumbent exact cell, coarsening, shield-table split,
  threshold selection, and finite worst-case grammar are fully specified by
  R22. The new atom is only sparse-cell pool construction.
- **Search universe:** considered fixed nearest-neighbour backoff, adaptive k,
  reduced axes, larger shield partitions, tuned tau, outcome-trained metric,
  and learned clustering. Only fixed `k=2` Hamming backoff changes one atom
  without changing folds, tau, corpus, or adding outcome tuning.
- **Formulation:** coverage restoration and learned value are separated. The
  selected-pool maximum is not called conditional validity.

## Challenge to the saturation basis

Hamming distance treats heterogeneous median-split bits equally and lexical
ties are arbitrary. The fixed lexical no-geometry pool is therefore retained
as a negative control. A chance lexical-control win or high realized violation
rate narrows or defeats the geometry interpretation.

## Why prior search could look falsely flat

R22 required exact equality on every acquired bit. With far more possible
binary vectors than shield members, refinement mechanically destroyed cells
before proposal quality could matter. Fallback then collapsed arms, and the
scalar-F* defect obscured the performance scale.

## Reopen triggers

Reopen rather than patch after outcomes if any binding drifts, a custody set
overlaps, an excess is negative, two processes differ, the independent pool
replay differs, the exact-cell parent is not preserved when cell size is at
least two, the lexical negative control is omitted, or a gating hostile control
fails. Coverage below 0.95 and value null/adverse are retained outcomes, not
reasons to tune k, tau, bits, folds, or arms.

## Frozen implementation hypothesis

When an exact cell contains fewer than two shield members, the two members
minimizing `(direct Hamming distance, lexical dataset name)` form the only R23
backoff pool. Exact cells of size at least two remain unchanged. Worst-case
excess and admissibility are computed exactly over the selected pool; learning
cannot change admissibility. F* is the lexical-tied best shield-mean executable
portfolio arm in both parent and revival.

## Tests frozen before execution

Known-answer F*, sparse/dense cell, Hamming, lexical-control, input-order,
custody, hostile-scorer, terminal-precedence, two-run wrapper, and independent
verifier tests are frozen with the executor. Full execution is prohibited
until they pass.
