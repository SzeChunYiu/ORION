# QG-7d amendment — direct n=2 pinned-residual discriminator

Date: 2026-08-21
Issue: #836
Parent protocol commit: `b8ef07923b64e09906f558398a474eb4ca0cd836`
Status: **FROZEN BEFORE ANY N2_DIRECT EXACT COST OUTCOME.**

This amendment adds one counterexample-first arm only. It does not alter J5, its gates, the T4b census, or any theorem terminal.

## Admissibility binding

The frozen R6M synthetic research grammar function `_synthetic_terms(target_pairs)` accepts arbitrary Pauli keys and checks only that exactly six terms are supplied. The exact `_solve_config` / `_brute_config_n2` machinery admits local target letter `I=0`; there is no nonzero-target predicate in this research grammar.

The QG-7d analyzer must bind this by source identity and by at least one hostile control containing an identity target branch for which production DP and independent n=2 brute agree. If this cannot be checked, `N2_DIRECT` is `CANNOT_CHECK` and grants no authority.

## N2_DIRECT construction

Use only the two touched T4b coordinates `(b,a)` as the two physical qubits; do **not** add a spectator coordinate.

Source rows are selected from the committed QG-7c `t4b_pinned.failing_verbatim_capped` list in exact stored order. The first run is frozen to all available committed capped rows (currently 40) and may not add/remove rows after seeing costs.

For each row:

1. decode the same `(coreB, envB, coreA, envA, case, ja, R_b, R_a, p)` state as QG-7c `_realize_row`;
2. construct the six target branch keys on exactly two qubits `(b,a)` using the identical QG-7c formulas **but omit the common spectator `Z` entirely**;
3. preserve identity target keys when produced; do not repair/replace them;
4. reconstruct the reference pinned comm-s2 configuration and require it to satisfy frozen R6S labels/acceptance before using the row as a scientific discriminator;
5. evaluate exact `C_D++`, `C_D+`, `f_B′`, `f_B″` in that order;
6. if and only if `C_D++ < min(C_D+, f_B′, f_B″)`, open unrestricted frozen DP and proof-carrying R6M replay;
7. require `C_DP == C_D++`, every R6M/D++ witness check green, and independent generic-ORION reconstruction before B‴ authority.

The first replay-confirmed strict row in stored order is the selected witness. Continue the frozen 40-row scan for morphology after selection; selection does not stop counting.

## Exact positive condition

`C_DP == C_D++ < min(C_D+, f_B′, f_B″)`

Positive terminal contribution:

`N2_DIRECT_BTRIPLEPRIME_WITNESS`

which may authorize the issue-level terminal

`QG7D_BTRIPLEPRIME_REGIME_FOUND__PINNED_COMM_S2_EXACT_WITNESS`.

## Honest negative

If all admitted committed rows satisfy

`C_D++ >= min(C_D+, f_B′, f_B″)`,

record

`N2_DIRECT_NO_GAP_IN_COMMITTED_T4B_ROWS`.

This is bounded negative evidence only. It does not close PA/PP or the all-n theorem.

## Anti-overclaim

Identity-target admissibility here is an internal synthetic research-grammar fact, not a statement about physical chemistry inputs. No chemistry data or protected stretched-N2 subject may be read. No novelty, R6 or physical quantum-advantage authority follows.