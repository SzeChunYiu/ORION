# Second implementation of the `D_3(C_7^3)` elimination step — V5

Status: **the load-bearing computational step is now reproduced by a second, deliberately dissimilar implementation.** Both agree exactly.
Checker: `verify_d3_step5_independent_v5.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Why

The internal referee pass (`papers/orion-26-.../REFEREE_REPORT_V1.md`) identified step 5 of the `D_3(C_7^3) = 36` proof — enumerate the feasible atom-length spectra, cut by closure and the corridor, eliminate the survivors by complement systems — as the single place where one implementation carries a load-bearing claim. The end-to-end checker re-runs *that same* enumeration, so it guards against regression but not against a coding error in the enumeration itself.

## 2. What was built

A C program that recomputes step 5 from the mathematical statement, chosen to share as little as possible with `verify_D3_C7_end_to_end_v3.py`:

| | original | second implementation |
|---|---|---|
| language | Python | C |
| binomials | exact integer `math.comb`, reduced mod 7 afterwards | **Pascal's triangle built mod 7** from the start |
| consistency test | primal: row-reduce `[A \| b]`, look for a zero row with nonzero right-hand side | **dual (Fredholm)**: row-reduce `[A \| I]`, extract the left null space, check every null vector `λ` has `λ·b = 0` |
| length sets | `itertools.combinations` over a list | 12-bit **masks** enumerated in C |

The dual route is not an arbitrary variation: it is the formulation proved in `LUCAS_CRITERION_V5.md`, so the second implementation exercises the same mathematics through the theorem rather than through the original code path.

## 3. Result

```
recorded 6-triple corridor:   feasible spectra 548 ; after closure+corridor 8 ; eliminated 8 ; SURVIVING 0
tightened 4-triple corridor:  feasible spectra 548 ; after closure+corridor 5 ; eliminated 5 ; SURVIVING 0
```

The first line reproduces the recorded figures **exactly**: 548 feasible spectra, 8 after the cut, all 8 eliminated.

The second line is a bonus consistency check. Feeding it the tightened corridor of `SHORT_ATOM_BOUND_UNIFORM_V4.md` leaves 5 spectra instead of 8, and all 5 are eliminated — as it must be, since a smaller corridor is a strictly stronger constraint and the survivors of the tighter cut are a subset of the eight. Both routes reach no obstruction.

A Pascal control runs first: six independently computed values of `C(n,k) mod 7` (including `C(14,7) = 2`, the Lucas-degenerate case the arguments lean on) must match, or the program aborts before doing any work.

## 4. What this does and does not clear

**Does.** It removes ordinary implementation-error risk from the step: a transcription slip, an off-by-one in the degree range, a sign error in the complementation term, or a bug in the elimination would have to occur identically in two programs written in different languages, using different arithmetic and different decision procedures, to survive.

**Does not.** Both implementations were written by the same author from the same understanding. A *systematic* error — a wrong characterisation of the zero-sum sub-multisets, a wrong overlap range, a corridor triple that should not be there — would be reproduced faithfully by both. That risk is only retired by a third party, and the submission gate for independent mathematical review stands unchanged.

The honest formulation: **step 5 is now double-implemented, not independently verified.**

## Claim ceiling

This concerns step 5 only. Steps 1–4 of the proof are human-checkable arguments and step 3 is a corollary of `LUCAS_CRITERION_V5.md`; they are not the subject of this record.
