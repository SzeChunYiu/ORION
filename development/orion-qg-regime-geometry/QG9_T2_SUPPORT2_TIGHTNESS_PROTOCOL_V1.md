# QG-9 T2 — exact support-two tightness at n=2

Date: 2026-08-21
Issue: #803
Parent theorem: PR #792 / receipt commit `a80dbd57d9124f058de7465a13de8c69416c368b`
Parent terminal: `QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED`
Branch: `shadow/orion-qg-qg9-t2-support2-tightness`
Status: **FROZEN BEFORE ANY CAP1 OR UNRESTRICTED RESULT ON T2 CANDIDATES.**
Authority ceiling: bounded tightness evidence for frozen R6I only; no novelty / R6 / physical-advantage authority.

## Question

Does some frozen-R6I instance satisfy

`C_DP < C_cap1`,

where `C_cap1` is the exact optimum restricted to all four independent generators having global support <=1?

A single strict witness proves support 2 is necessary. Failure to find one in this frozen inverse-design domain is only a bounded negative and cannot authorize support<=1.

## Minimal witness size and cap1 structure

Use `n=2`. A nonzero support<=1 Pauli lives on one qubit. Since a block requires `symp(R0,R1)=1`, two support<=1 independent generators cannot occupy different qubits. Therefore every cap1 block is localized to exactly one qubit and is one of 12 ordered anticommuting generator pairs (6 local ordered pairs × 2 qubits).

## Cap1-blind candidate generator

Reconstruct the parent V3/V4 local-state machinery and enumerate concrete two-column block states:

1. each column state is `(r0,r1,s0,s1) in {I,X,Y,Z}^4`, excluding `(r0,r1)=(I,I)`;
2. group each state by the parent V3 action-profile type;
3. for each unordered two-column type case, require full R6I single-block acceptance:
   - total `<R0,R1>=1`;
   - `c0=2<S0,R0>+<S1,R0>` nonzero;
   - `c1=2<S0,R1>+<S1,R1>` nonzero;
   - `c0!=c1`;
4. require the parent V3 relabel/delete grammar has **no** safe move for that concrete two-column type case;
5. require `max(w(R0),w(R1))=2`.

For every concrete surviving block state, canonicalize only by **qubit swap**. (No Pauli-letter quotient is used in T2; this keeps the transformation discipline transparent.) Canonical candidate identity is the lexicographically smaller of the original two-column tuple and its qubit-swapped tuple.

For each canonical block state:
- build block A and B from the same state, so shared Tag labels match exactly;
- set target triples `P=(R0,R1,R0*R1)` for both blocks, giving the desired frame zero Restore;
- compute the desired support-2 witness cost `U2 = 2*min_c uanti(R,c) + 2*(w(S0)+w(S1))`;
- central tie-break: lexicographically first minimum for the sealed desired witness;
- record candidate before any cap1 or unrestricted optimum is computed.

Candidate scan: **all canonical candidates**, in canonical tuple order. No post-outcome extension.

## Exact production cap1 referee

Enumerate all 12 support<=1 ordered symplectic frame pairs for A and B. For each pair:
- minimize block-A `uanti + Restore` over 3 central choices;
- minimize block-B `uanti + Restore` over 3 central choices and all 6 target permutations;
- minimize shared Tag cost by direct enumeration over all 16 choices of `S0` and 16 of `S1`, retaining only equal nonzero distinct branch labels across A/B.

The exact minimum over 12×12 frame-pair combinations is `C_cap1`.

No unrestricted production DP call is allowed until `U2` and `C_cap1` are sealed for the candidate.

## Positive gate

For the first candidate with `U2 < C_cap1`:

1. call production `shared_tag_exact`;
2. require `C_DP <= U2 < C_cap1`;
3. independently recompute the returned production witness checks and cost;
4. independently recompute `C_cap1` with a second brute implementation that does not call the production cap1 helper;
5. serialize the first strict witness and stop.

Positive terminal:

`QG9_SUPPORT2_TIGHT_WITNESS_FOUND__CAP1_STRICT_GAP`

This is a theorem of **necessity** for the frozen family: because `C_DP < C_cap1`, no support<=1 optimum exists for that instance.

## Honest negative

If every candidate has `U2 >= C_cap1`, terminal:

`QG9_T2_NO_TIGHT_WITNESS_IN_FROZEN_INVERSE_DESIGN_DOMAIN`.

No support1 authority follows.

## Independent generic ORION verifier

Reimplement the phase-free one-qubit Pauli multiplication, symplectic form, weight, the 12 cap1 frame pairs, direct tag enumeration, and exact cap1 cost. Reconstruct the canonical candidate set independently from primitive concrete local states plus the serialized parent unsafe-case criterion. For a positive, rerun the strict-gap witness; for a negative, verify every candidate row.

## Native ORION-Q responsibilities

- `RESP:TIGHT` → accept strict cap1 gap only;
- `RESP:NEGATIVE` → record bounded negative only;
- `RESP:DISAGREE` → CANNOT_CHECK / reject;
- never map no-witness to support1 theorem authority.

## Frozen gates

- parent protected support2 terminal and both-accept bound;
- production `_MUL/_SYMP/_LW` bind to primitive Pauli algebra;
- exactly 12 cap1 frame pairs;
- candidate generation occurs before cap1/unrestricted opening;
- cap1 production/generic equality;
- first strict witness only, deterministic order;
- no chemistry/protected subject/network;
- `support1_authority=false`, `novelty_authority=false`, `physical_quantum_advantage_claim=false`.
