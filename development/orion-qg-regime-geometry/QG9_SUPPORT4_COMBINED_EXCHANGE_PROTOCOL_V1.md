# QG-9 support-4 combined-exchange theorem — protocol V1

Date frozen: 2026-08-21. Parent: ORION-QG #740. Frontier issue: #762.
Frozen base: `f90c7dfa484791d5c0fa325bf0d1b13c68b5f72d`.
Authority ceiling: bounded R6I theorem candidate only; no novelty, R6, or physical-advantage authority.

## Motivation

Canonical QG-1 proves every optimum of the frozen R6I rank-2 shared-Tag grammar has each independent generator supported on at most five qubits. Its proof uses separate SOLO moves on non-coincidence columns and PAIR moves on coincidence columns, leaving a finite zero-sum-free support-5 boundary.

Exploratory preflight (not authority) suggests that this boundary can be closed by allowing **combined per-column deletions** across a block. V1 freezes the complete production-bound test before any official result.

## Local state and actions

At one qubit a block carries independent generator letters `(a,b)` and shared Tag letters `(s0,s1)`. The dependent third letter is always recomputed as `a*b`.

Local action grammar:
- `d0`: `(a,b) -> (I,b)` when `a != I`;
- `d1`: `(a,b) -> (a,I)` when `b != I`;
- `db`: `(a,b) -> (I,I)` when either generator is active;
- `none`.

For each action compute its exact five-bit semantic change signature

`(<R0,R1>, <S0,R0>, <S1,R0>, <S0,R1>, <S1,R1>)_before XOR _after`.

A multi-column edit is semantics-preserving iff the XOR of all selected local signatures is zero.

## Production local cost bound

Use the exact R6I local objective with multipliers `(4,4,4)` and one central branch reduced to `2`, plus all three Restore supports. Tag is unchanged.

For every `(a,b,s0,s1)` representative, every action, every central in `{0,1,2}`, and every target triple `(p0,p1,p2) in {I,X,Y,Z}^3`, compute exact `Delta C`.

Local representatives are grouped only by the descriptor

`(a_active,b_active,coincidence, alpha, beta00,beta10,beta01,beta11)`

where `alpha=<a,b>`, `beta_i0=<Si,a>`, `beta_i1=<Si,b>`. For every descriptor/action, the action signature must be unique across representatives; the cost certificate uses the **worst** `Delta C` across all representatives/targets separately for each central choice.

Thus a combined action pattern with summed worst cost <=0 for every central is safe for every concrete local realization in that descriptor pattern.

## QG-1 irreducible boundary domain

Choose a generator called R0. For support `w`, enumerate every multiset of local descriptors with R0 active on all `w` columns. Retain a deliberately broad superset of valid QG-1 irreducible patterns:

- global anticommutation parity XOR is 1;
- R0's two-bit Tag label is nonzero;
- coincidence-column Tag classes contain no nonempty zero-sum subset;
- R0 non-coincidence classes `(alpha,beta00,beta10)` contain no nonempty zero-sum subset;
- R1 non-coincidence classes `(alpha,beta01,beta11)` contain no nonempty zero-sum subset.

The valid R6I boundary is a subset of this domain, so closing the broader domain is sufficient.

No expected number of retained patterns is supplied to the official checker.

## Support-5 closure gate

For every retained `w=5` descriptor multiset, search the finite Cartesian product of local actions. A successful combined move must:

1. choose at least one non-`none` action;
2. have total five-bit signature XOR zero;
3. delete at least one active R0 letter;
4. never add support to either generator;
5. have summed worst-case `Delta C <= 0` for **each** of the three central choices.

Primary theorem gate: **every retained support-5 pattern has such a move**.

Combined with canonical QG-1 support≤5, this yields a lexicographic descent contradiction for any support-5 generator and therefore the candidate theorem:

> Every optimum in the frozen R6I grammar admits all four independent generators with global support ≤4, for every n and every admitted instance.

## Support-4 boundary control

Run the same search at `w=4` and report all patterns with no safe combined move. A nonempty obstruction set prevents V1 from claiming support≤3 by this edit grammar. Absence of a support-4 move is **not** a tightness theorem.

No expected obstruction count is supplied.

## Independent verification

Generic ORION verifier reimplements the phase-free one-qubit Pauli algebra, descriptors, signatures, local costs, irreducibility predicate, and combined-move search without importing the candidate script or R6I production tables.

Native ORION-Q verifier binds the candidate algebra to production `r6i._MUL/_SYMP/_LW`, binds canonical QG-1 receipt authority/gates, and verifies the proof-composition ledger. It cannot promote support≤3, tightness, novelty, or physical advantage.

## Honest terminals

- `QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED`
- `QG9_SUPPORT5_COMBINED_EXCHANGE_COUNTEREXAMPLE_FOUND`
- `QG9_PRODUCTION_BINDING_OR_PARENT_GAP`
- `QG9_GENERIC_NATIVE_DISAGREEMENT`
- `QG9_CANNOT_CHECK`

## Claim boundary

The theorem, if earned, is only for the frozen R6I objective/grammar. It does not cover R6K factor variants, other objective weights, larger Tag ranks, support-4 tightness, or physical quantum advantage.
