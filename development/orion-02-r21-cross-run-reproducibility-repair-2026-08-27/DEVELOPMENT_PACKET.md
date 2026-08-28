# ORION-02 R21 cross-run reproducibility repair development packet

Date: 2026-08-27
Base: `PR #1550@800ba6f611d580b37ec583caba802157410f5abb`
Parent: #1512, ORION-02 Round 2 direct-relative/joint-route mechanism

## Atomic development questions

1. Why did dedicated run `33084807980` reproduce byte-identically within one
   runner but differ from the committed result admitted by run `33082103451`?
2. Can the implementation be made to obey the already-frozen rule that exact
   distance ties follow lexical instance order without adding a fitted
   tolerance or changing any scientific choice?
3. Can two separate hosted runners reproduce both one another and the preserved
   committed receipt before repaired custody is admitted?
4. Can the successful and divergent raw receipts remain immutable and
   independently hash-verifiable throughout the repair?

## Recovered incumbent and adverse history

- The prospectively frozen executor and protocol produced the adverse science
  terminal `C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE`.
- Run `33082103451` at exact head `d1ea1ce04ca915fad9b35288b40eef77eec7dd15`
  produced two identical results with SHA-256 `9606f30d...`; those bytes are
  committed.
- Run `33084807980` at relocation-only head
  `800ba6f611d580b37ec583caba802157410f5abb` produced two identical results
  with SHA-256 `00d67a62...`, then failed the committed-byte comparison.
- The executor bytes are identical across those heads.  The only scalar
  differences are 17 fold-1 predictions and their interval endpoints, plus
  two derived row digests.  Every decision, loss, timeout, aggregate,
  terminal, and authority boundary is unchanged.
- R18 null/retraction, R19 repair, BNSL null, the TSP prerequisite
  `CANNOT_CHECK`, immutable convergence V1, and protected Task-3/P9 are not
  repair targets.

## Bounded saturation assessment

### Knowledge

The two raw action artifacts, their exact environments, the frozen executor,
and the pinned CSP-MZN subject are sufficient to localize the divergence.  The
17 affected queries and 30 candidate route-fit rows have bitwise-identical
transformed static vectors.  Their mathematical squared distances are zero.

### Search universe

The admissible repair space contains only exact duplicate-vector recognition,
the frozen stable lexical tie rule, hard byte comparisons, and additive
custody.  It excludes distance tolerances, rounding, changed k, changed data,
changed folds, changed models, changed thresholds, and changed terminals.

### Formulation

The defect is an implementation/custody defect: cancellation-form floating
distance evaluation can give bitwise-identical vectors host-dependent tiny
positive distances before stable sorting.  A repaired result is authoritative
only if separate hosted runners reproduce each other and the preserved
committed object exactly.

## Challenge to the saturation basis

This diagnosis is false if any non-identical vector, scientific decision, or
aggregate differs between the two receipts, or if exact-duplicate handling is
insufficient to reproduce the committed object across separate runners.  The
repair must fail closed in either case rather than widen an epsilon or tune a
tie band after seeing outcomes.

## Why an earlier check missed this route

The workflow executed twice on the same runner.  Both processes used the same
host and BLAS kernel, so within-runner byte identity could not discriminate
host-dependent matrix-product accumulation.  Stable sorting guaranteed lexical
order only for bitwise-equal computed distances, not for mathematically equal
distances perturbed before sorting.

## Frozen implementation hypothesis

Before sorting, set a distance to exact zero only when the transformed query
row and transformed training row are bitwise identical.  Leave every other
distance byte and the stable sort unchanged.  Two separate runner jobs must
then match each other and the preserved `9606f30d...` object byte-for-byte.

## Reopen triggers and honest terminals

- Any scientific field or adverse terminal changes: stop; the defect-only
  hypothesis is falsified.
- Any non-identical distance needs a tolerance or rounding rule: stop with
  `ORION02_R21_ADVERSE_PRESERVED__CROSS_RUN_REPRODUCIBILITY_CANNOT_CHECK`.
- Any separate-runner mismatch remains: preserve it additively and keep the
  same custody `CANNOT_CHECK` terminal.
- Exact separate-runner and committed-byte equality permits only successor
  reproducibility custody.  It is not a new science round, positive evidence,
  external independence, production value, journal authority, or submission
  authorization.
