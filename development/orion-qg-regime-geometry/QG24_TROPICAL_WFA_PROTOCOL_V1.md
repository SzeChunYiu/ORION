# ORION-QG QG-24 — exact three-block TARE as a finite tropical weighted automaton V1

Date: 2026-08-22
Parent programme: #740
Issue: #880
Execution branch: `codex/orion-qg-qg24-tropical-wfa-20260822`
Structural parents:
- R6S all-n frame-support theorem (`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`)
- QG-7c M1/T1/T2 structural reductions (`research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json` and frozen protocol)
Hostile/compactness control: QG-23 protected result (`research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json`)
Status: **FROZEN BEFORE QG-24 MACHINE OUTCOME.**
Authority: exact compiler-representation theorem only; weighted-automata/tropical mathematics is donor-owned. No novelty, R6, physical-advantage, chain-closure, B''-completeness, automaton-minimality, or asymptotic-phase authority.

## Scientific question

For one fixed perfect matching of six nonzero target Pauli strings into the three R6M/TARE blocks A/B/C, is the exact unrestricted frozen unit-objective TARE optimum over arbitrary physical qubit count `n` recognized by one finite weighted automaton over the tropical `(min,+)` semiring?

The input word is the sequence of qubit columns

`x_q = (P_A0(q),P_A1(q),P_B0(q),P_B1(q),P_C0(q),P_C1(q)) in {I,X,Y,Z}^6`.

Thus the input alphabet has exactly `4^6 = 4096` symbols. The six full target Paulis must be nonzero at final instance scope, but individual input columns may be any of the 4096 symbols.

## P0 — exact finite-support existence parent

Full unrestricted authority requires an existence theorem for an optimum inside fixed support caps.

1. R6S earns, for every `n` and every admitted frozen R6M instance, an unrestricted optimum with all six frame Paulis of global support `<=2`.
2. Starting from such an optimum, apply only already-earned non-increasing all-n reductions used before the open QG-7c T4b chain step: L1/(2,2)-block elimination, L2 orientation, class-(0,0) Lemma-E zeroing, L4a out-of-frame Tag pruning, the exhaustive M1 A/P/C classification, and T1 commuting-Tag prune. None requires T4b chain closure.
3. After T1, every surviving Tag coordinate is anticommuted by at least one irreducible block. M1/T2 gives exactly one anticommuting Tag coordinate for A/P and two for C, so `wt(S) <= a+p+2c = 3+c <= 6` for three blocks.

Therefore at least one unrestricted optimum exists with:
- each frame support in `{1,2}`;
- shared Tag support in `{1,...,6}`.

QG-23 is a hostile-corrected compactness control, not logically required for the automaton equality. Its stronger auxiliary-union statement must not be confused with the automaton state contract.

If the parent binding cannot justify the Tag `<=6` optimum-existence step independently of T4b, return `QG24_BOUNDED_TAG_AUTOMATON_EXACT__UNRESTRICTED_TAG_CAP_OPEN` rather than promoting unrestricted equality.

## P1 — fixed global-control sectors

For a fixed matching, global controls that affect local transition cost are finite and may be handled as external sectors:
- target permutation bit for each block: `2^3 = 8` tuples;
- central-frame bit for each block: `2^3 = 8` tuples.

There are therefore exactly **64 sectors**.

The common shared-Tag label orientation is **not** a separate sector. Final acceptance directly requires all branch-0 Tag/frame syndromes to equal one bit `l0`, all branch-1 syndromes to equal one bit `l1`, and `l0 != l1`, thereby accepting both `(0,1)` and `(1,0)` orientations.

A full optimization over the 15 possible perfect matchings, when desired, is a further finite outer minimum and does not change finite-state recognizability. QG-24 V1 proves the theorem for each fixed matching.

## P2 — frozen automaton state contract

Within one fixed global-control sector, the state after reading a prefix contains exactly:

1. six frame-support counters `w_i in {0,1,2}`;
2. one shared-Tag support counter `w_S in {0,1,...,6}`;
3. three accumulated frame-pair symplectic parities `a_j = <R_j0,R_j1> in F_2`;
4. six accumulated Tag/frame syndrome parities `b_i = <S,R_i> in F_2`.

No local Pauli letter from a previous qubit is retained.

Raw state count per sector is frozen exactly as

`3^6 * 7 * 2^9 = 2,612,736`.

This is an unreduced upper bound, not a minimality claim. Reachability/minimization is a successor question only after exactness is sealed.

## P3 — local transition relation

At one input column `x=(p_0,...,p_5)`, a nondeterministic transition chooses local auxiliary letters

`(f_0,...,f_5,s) in {I,X,Y,Z}^7`.

Reject a transition if any frame-support counter would exceed 2 or the Tag-support counter would exceed 6.

Update:
- `w_i += 1[f_i != I]`;
- `w_S += 1[s != I]`;
- for each block `j`, `a_j ^= local_symp(f_2j,f_2j+1)`;
- for each `i`, `b_i ^= local_symp(s,f_i)`.

For the fixed target-permutation tuple, first map the six input target letters to branch order. Local Restore letter is `t_i = local_mul(p_i,f_i)`.

Local transition weight is exactly

`sum_i m_i * 1[f_i != I] + 2*1[s != I] + F3(t_0,t_2,t_4) + F3(t_1,t_3,t_5)`,

where within each block the fixed central bit gives multiplier 2 to the central frame and 4 to the noncentral frame.

The final accepting path weight subtracts the frozen constant 18 once.

Path concatenation adds weights; alternative paths combine by minimum. Hence the machine is a weighted automaton over the tropical `(min,+)` semiring.

## P4 — final acceptance is exactly the frozen R6M semantics

After the last input column, accept iff:

1. every frame counter is 1 or 2 (all six frames nonzero and within the cap);
2. all three frame-pair parity bits equal 1;
3. branch-0 Tag syndromes are common: `b_0=b_2=b_4=l0`;
4. branch-1 Tag syndromes are common: `b_1=b_3=b_5=l1`;
5. `l0 != l1`;
6. Tag support is within the cap already enforced.

No other history-dependent acceptance condition is permitted in V1.

## P5 — Markov-completeness / path-configuration bijection

The analyzer must bind production `config_cost` and `config_labels` and independently audit that:
- frozen cost is exactly the sum over qubit-local frame support, Tag support and two F3 Restore terms, plus constant `-18`;
- Pauli multiplication and symplectic form are coordinatewise over phase-free `F_2^2`;
- global pair anticommutation and Tag syndromes are XORs of the local symplectic bits;
- nonzero/support conditions are completely determined by the counters.

Therefore, within a fixed sector:
- every accepting path uniquely specifies one support-capped admissible TARE configuration and has exactly its frozen cost;
- every support-capped admissible TARE configuration uniquely specifies one accepting path and has exactly the same cost.

Let `C_WFA` be the minimum accepting-path weight over all 64 sectors. Then `C_WFA` equals the exact optimum over frame-support<=2, Tag-support<=6 configurations.

## P6 — unrestricted all-n equality

By P0, at least one unrestricted optimum lies inside those support caps. By P5, every capped configuration is an original admissible configuration. Hence

`C_DP <= C_WFA <= C_DP`,

so for every physical qubit count `n` and every admitted fixed-matching six-target instance,

`C_WFA = C_DP`.

This is an exact representation/algorithmic theorem. It does **not** prove that D+/B'/B'' is complete or that the open chain sector has a closed-form normalization.

## P7 — complete local-table binding

Production analyzer and generic ORION must separately reconstruct the phase-free local algebra on `{I,X,Y,Z}` and verify complete tables:
- 16 local multiplication entries;
- 16 local symplectic entries;
- 4 local weight entries;
- 64 F3 entries.

Production analyzer binds its independently reconstructed tables to the frozen R6M/R6S production tables.

## P8 — complete n=1 calibration

Before all-n authority, execute a complete n=1 calibration over all **729** valid one-qubit target six-tuples (`{X,Y,Z}^6`).

At n=1, the complete feasible shared-Tag/frame auxiliary inventory has exactly **48** rows:
- 3 nonzero Tag letters;
- 2 label orientations;
- for each of three blocks, 2 choices for the opposite frame letter.

For every one of 729 target tuples:
- minimize the frozen production `config_cost` over all 48 feasible auxiliary rows, 8 target-permutation tuples and 8 central tuples;
- independently minimize the one-column automaton transition/final-acceptance formula over the same semantic domain;
- require equality and serialize the ordered 729-value minimum-cost vector digest and histogram.

The generic verifier rebuilds this full calibration from primitive local algebra without importing production transition tables or the production QG-24 analyzer and must reproduce the same minimum-cost vector digest/histogram.

Any mismatch serializes the first target tuple and both costs.

## P9 — complexity statement

QG-24 may state only:

> Because the state space and local auxiliary alphabet are finite constants for this fixed six-target grammar, exact evaluation by sparse dynamic programming over reachable weighted-automaton states is linear in word length `n` up to a grammar-dependent constant factor.

No practical runtime claim is earned from the raw 2,612,736-state bound. No dense transition matrix need be materialized.

## Independent generic ORION

Generic ORION must:
- implement phase-free local Pauli algebra independently;
- derive the same 4096-symbol alphabet, 64 sectors, state variables and exact raw state count;
- independently prove/update the local parity/counter transition contract;
- independently enumerate the 48 feasible n=1 auxiliary rows and the complete 729-target calibration;
- verify the P0 parent facts only after its finite-state contract is sealed.

It may share the frozen protocol specification but not production local tables or transition code.

## Native ORION-Q responsibility gate

May authorize `FINITE_STATE_EXACT_COMPILER` and `UNRESTRICTED_DP_EQUALITY_ALL_N` only if:
- production and generic finite-state contracts agree;
- complete n=1 calibrations agree;
- R6S support<=2 all-n parent is protected;
- QG-7c Tag<=6 existence argument is bound without using the open T4b theorem;
- every accepting path remains an original admissible configuration;
- all stronger authority coordinates below remain false.

Mandatory false coordinates:
- `AUTOMATON_MINIMALITY`
- `CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS`
- `CHAIN_ALL_N`
- `ASYMPTOTIC_PHASE_BOUNDARY`
- `GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY`
- novelty/R6/physical-advantage authority.

## Intended strong terminal

`QG24_TARE_UNRESTRICTED_EXACT_OPTIMUM_RECOGNIZED_BY_FINITE_TROPICAL_AUTOMATON_ALL_N`

Honest alternatives:
- `QG24_BOUNDED_TAG_AUTOMATON_EXACT__UNRESTRICTED_TAG_CAP_OPEN`
- `QG24_STATE_SPECIFICATION_MISSING_GLOBAL_CONSTRAINT`
- `QG24_N1_CALIBRATION_COUNTEREXAMPLE`
- `QG24_PARENT_BINDING_GAP`
- `QG24_GENERIC_NATIVE_DISAGREEMENT`
- `QG24_CANNOT_CHECK`

## Donor subtraction

Weighted automata, tropical semirings, rational series, transfer matrices, finite-state dynamic programming and automaton minimization are established mathematics/computer science and receive zero novelty credit. Candidate contribution is only the exact TARE-specific representation theorem, its proof-carrying state contract, and downstream compiler-specific consequences.