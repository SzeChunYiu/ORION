# ORION-21 tie-robust phase — engineering readiness

**Protocol:** `ORION21.TIE_ROBUST_PHASE.v1`  
**Status:** `RUNNER_AND_INDEPENDENT_CHECKER_READY__SCIENTIFIC_EXECUTION_NOT_RUN`  
**scientific_authority_delta:** `NONE`

> **Superseded 2026-08-29 — the run has since happened.** This document records the
> readiness state as it stood *before* execution, and is left unedited for that reason: the
> status line above describes that prior state, not the current one. The frozen command was
> executed once on LUNARC (job `3552796`, `ORION_SOURCE_COMMIT b8fd5d2c`) and returned
> terminal `T3_TIE_AMBIGUOUS_VERDICT_CHANGING`, with the independent checker in agreement
> (`status: PASS`). See `CLAIM_DISPOSITION.md` § "Executed outcome (2026-08-29)" and the raw
> outputs under `result/run-3552796/`.

## What this packet adds

The scientific protocol, theory, ladder, thresholds, seeds, and admissible terminals were already frozen before this engineering work. This packet adds only the missing execution machinery:

- `run_tie_robust_phase.py` — deterministic set-valued reconstruction;
- `independent_checker/check_tie_robust_phase.py` — transcript-only independent recomputation; and
- `run_tie_robust_phase.sbatch` — the registered LUNARC batch entry point.

No `RESULT.json` is committed and no registered ladder outcome is read in this packet.

## Runner semantics

For every frozen cell, seed, train size and query the runner:

1. reconstructs the P11H keyed generator stream exactly (`default_rng([seed,0,d,s,r])`), preserving query/test draws and sequential train-size draws;
2. computes **integer** feature-label correlations;
3. finds the exact top-`r` equality class, with no tolerance;
4. enumerates every support consistent with the boundary equality;
5. uses ascending feature index only to name the prospectively registered canonical member, never to replace the admissible set;
6. emits bit-packed labels and every candidate prediction stream;
7. sums per-query minima/maxima to obtain the exact per-seed extrema (choices are independent across queries);
8. sums seed extrema to obtain exact seven-seed mean bounds;
9. computes `n_cross_lo` and `n_cross_hi` by exact integer comparison with `0.95 = 19/20`; and
10. evaluates the original C1/C2/C3/C4 criterion at the registered low/high endpoint vectors.

There is no candidate truncation, approximate equality, floating scorer, post-outcome tolerance, or adaptive ladder extension. Resource exhaustion therefore fails closed into the existing T4/CANNOT_CHECK path rather than changing the scientific object.

Zero integer correlation is not special-cased: `sign(0)=0`, so such a selected coordinate contributes exactly zero to the registered linear screening score. This is the literal integer-sign continuation used by the exact-anchor reconstruction and adds no tolerance.

## Independent checker

The checker imports **no runner or generator code**. It reads only:

- the frozen protocol/terminal documents;
- `RESULT.json`; and
- the emitted bit-packed label/prediction transcripts.

It independently:

- verifies transcript SHA-256 digests;
- reconstructs candidate correct counts from raw bits;
- reconstructs the complete support equality class from the emitted fixed/tied/need metadata;
- rejects missing or extra candidate supports;
- recomputes query, seed and seven-seed min/max bounds;
- recomputes crossing intervals and point-identification status;
- recomputes the registered endpoint verdicts; and
- requires exact agreement with the runner terminal.

Exit codes remain distinct: `0` checked-green, `2` checker disagreement/RED, `3` scientific CANNOT_CHECK.

## Engineering-only smoke test

Before this packet was written, the runner and checker were exercised on a deliberately tiny **non-scientific synthetic ladder** (`d=5,s=2,r=2`, two seeds, two train sizes, 64 test rows). This does not use any registered ORION-21 ladder outcome and grants no scientific authority.

The smoke test covered both support regimes:

- 7 singleton/separable query points;
- 1 tied/set-valued query point;
- 9 candidate prediction streams;
- all raw transcript hashes and min/max bounds independently reproduced; and
- runner/checker terminal agreement.

`python -m py_compile` also passes independently for both scripts.

The smoke test is an engineering control only. Its terminal is not an ORION-21 result and must never be cited as evidence about the registered study.

## Scientific execution still required

The frozen protocol requires a **LUNARC compute node**. The scientific run therefore remains unexecuted here. The batch entry point writes a run-specific scratch directory containing:

- `RESULT.json`;
- `CHECKER_REPORT.json`;
- raw `transcript/` files;
- `transcript.tar.gz`; and
- SHA-256 digests.

A valid result requires both the runner and independent checker to complete under the frozen protocol. T4/CANNOT_CHECK remains a first-class outcome; no retry with relaxed equality is permitted.

## Exact next command

From the registered LUNARC checkout after this packet lands:

```bash
sbatch papers/orion-21-state-as-computation/experiments/tie-robust-phase-v1/run_tie_robust_phase.sbatch
```

The resulting run directory must be copied back **without editing any output**, then independently reviewed before any manuscript or claim-ledger change.

## Stop rule

No further theory or protocol changes are justified before this run. The next scientific action is the single frozen LUNARC execution. If it returns T4, the lane terminates CANNOT_CHECK exactly as preregistered.
