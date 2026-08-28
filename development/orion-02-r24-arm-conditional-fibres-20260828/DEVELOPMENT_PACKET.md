# ORION-02 R24 arm-conditional boundary-fibre development packet

Date: 2026-08-28

## Atomic development question

Does conditioning each local finite fibre on the candidate arm remove R23's
cross-arm intersection failure while boundary-witness selection keeps the
selected-fibre maximum empirically meaningful on held-out queries?

## Preserved negative history

- R22 exact full-state coverage was zero, and its scalar-grand-mean fallback
  performance values remain invalid.
- R23 corrected the fallback and raised Hamming k=2 full-state coverage to
  `32/44`, below the `0.95` gate.
- R23's lexical control reached `39/44`; Hamming geometry was therefore not
  supported by coverage.
- R23 primary learned decisions had `24/42` strict selected-pool-bound
  violations. Coverage did not establish certificate extension or value.

## Mechanistic delta

R23 used one common two-member pool for all arms. R24 constructs a separate
two-member local fibre for each arm from tau-good development witnesses. A
density-derived Hamming radius is a hard eligibility condition. Within it, the
two largest arm excesses are retained as boundary witnesses. Exact cells are
preserved only when all members are tau-good for that arm.

This is one pool-construction lever. It does not change corpus, folds, tau,
features, costs, portfolio, learned predictors, primary selection, or fallback.

## Alternatives rejected before execution

- increasing k or tau: post-outcome parameter tuning, not a new mechanism;
- choosing the easiest good witnesses: optimistic bound engineering;
- lexical good witnesses as the proposal: retained only as a no-geometry
  negative control;
- redefining strict validity to use tau rather than the exact selected-pool
  maximum: would weaken the failed gate;
- claiming same-corpus R24 as untouched-domain evidence: false because the R23
  outcome table was inspected.

## Required tests and stop conditions

Tests are frozen for radius minimality, local tau filtering, boundary ordering,
order invariance, exact-cell preservation, arm-specific admissibility, hostile
scorer exclusion, terminal precedence, nine-fold custody, deterministic policy
replay, two-process byte comparison, and independent-verifier mechanics.

Stop without counting the attempt on any source, digest, scheduler, parser,
wrapper, byte-identity, or verifier failure. Count only a verified scientific
terminal. Preserve every failed wrapper directory and all adverse outputs.

## Authority

The development packet authorizes only the bounded experiment. It grants no
external independence, generalization, submission, top-tier, merge, or
paper-freeze authority.
