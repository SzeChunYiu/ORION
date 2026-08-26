# P12 certificate-necessity theorem — result receipt V1

**Terminal:** `P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_GREEN`

**Freeze-before-execution:** theorem and checker committed (`e1a730c1`) before the first checker execution on this branch. Checker runtime: 1.1 s single process (miniforge CPython, no subprocesses, no worker pools).

## What was executed

The independent falsifier implemented the exact frozen five-gate contract of `P12_CERTIFICATE_NECESSITY_THEOREM_V1.md` over the registered reduced state (`n in {1,2}`, costs `{1,2,3}`, deltas `{-1..5}`, five price pairs, budgets `{0..6}`):

- ledgers enumerated per family: **462** (21 of size 1 + 441 of size 2);
- cells enumerated per family: **16,170** (462 ledgers × 5 price pairs × 7 budgets);
- indistinguishable pairs compared per family: 19,215 (`C2a`) up to 372,645 (`C4`); `C0` control compares 0 pairs by construction (identity separates every pair);
- parent-DP sufficiency re-verification cells: **16,170/16,170** oracle-equal, 0 failures.

## Gate results

| Gate | Result |
|---|---|
| G1 exact-field control (`C0`) zero witnesses | GREEN (0 witnesses) |
| G2 every coarsening family has a witness | GREEN — all six families, minimal witness size n=1 in every family |
| G3 optimistic + pessimistic reconstruction err | GREEN — 12/12 mutant catches, all objective shortfalls |
| G4 parent DP matches exhaustive oracle everywhere | GREEN (16,170/16,170) |
| G5 enumeration complete (declared counts) | GREEN |

## Witness counts (N2)

| Family | Witness pairs | Delta pairs separated |
|---|---|---|
| `C0_identity` (control) | 0 | — |
| `C1_sign_only` | 14,410 | the 10 pairs within `{1..5}` |
| `C2a_interval_k2` | 1,362 | {0,1}, {2,3}, {4,5} |
| `C2b_interval_k3` | 6,516 | the 6 pairs within {0,1,2} and within {3,4,5} |
| `C3a_threshold_theta1` | 15,586 | 11 pairs (−1,0) plus the 10 within `{1..5}` |
| `C3b_threshold_theta2` | 9,936 | 9 pairs: (−1,0), (−1,1), (0,1), plus the 6 within `{2..5}` |
| `C4_declared_cost_only` | 112,268 | all 21 unordered delta pairs |

Every family's minimal witness is a single-structure ledger. Example `C1` witness at prices `(2,1)`, budget 1: delta `1` has unique optimum `{}` (value `-1` if taken) while delta `3` has unique optimum `{S0}` (value `+1`); both deltas are `+` under sign-only, so no sign-measurable selector can be optimal on both.

Example `C4` reconstruction catch (optimistic): a true ledger `[(1,1)]` at prices `(2,1)`, budget 1 is reconstructed as `[(1,5)]` because 5 is the reachable maximum of the single certificate-free cell; the reconstructed DP materializes `S0` and realizes objective `-1` against oracle `0`.

## Scientific result

The parent selection-sufficiency law proved that exact per-structure additive charge certificates are **sufficient** for guaranteed-everywhere optimality (T1–T3), with an empirical price-obliviousness witness family (T4). This successor proves the **converse direction**:

- **N1 (general):** any two ledgers indistinguishable under a coarsening of the certificate channel, with distinct unique optima, defeat every deterministic coarsening-measurable selector on at least one ledger, and every randomized one with worst-case error probability at least 1/2.
- **N2 (mechanized):** every registered coarsening family — sign-only, interval-k for k=2,3, threshold bits at theta=1,2, and certificate-free — admits thousands of impossibility witnesses in the registered state, each verified against an exhaustive oracle; the exact-field control admits none.
- **N4 (iff):** within the registered environment, guaranteed-everywhere charged-objective optimality by a black-box selector is attainable **iff** the selector reads the exact realized certificates. The parent receipt's open question — "how much prospective/partial charge information is enough?" — is answered: none of the registered partial-information reductions preserves exact optimality.

## Authority boundary

Necessity is bounded-formal on the registered reduced state for the witness families (N1 itself is fully general); no prospective-cost, external, or deployment authority is granted; the parent theorem, its checker, its CI workflow, and all frozen P12A/P12B artifacts are untouched. This receipt grants no promotion wording beyond the iff stated above.
