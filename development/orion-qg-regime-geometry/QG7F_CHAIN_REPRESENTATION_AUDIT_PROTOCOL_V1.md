# QG-7f — pinned-chain representation audit V1

Date: 2026-08-22
Issue: #874
Parent result: `QG7E_V2_PP_SINGLE_PINNER_RESULTS.json`
Status: **FROZEN BEFORE QG-7f F0 OUTCOME.**
Authority ceiling: representation-premise theorem/refutation only. No chain normalization, global B'', novelty, R6, or physical-advantage authority.

## 1. Why F0 precedes any chain theorem

QG-7e V2 closes the single non-comm-s2 PP pinner sector all-n under its exact three-stage certificate, while preserving `CHAIN_ALL_N=false`. The registered QG-7f sketch proposed reducing the remaining chain to a directed pin graph on one common two-coordinate Tag support.

Before any normalization candidate is frozen, this protocol audits the load-bearing premise:

> **P2:** every simultaneously irreducible comm-s2 block in the remaining structural grammar must occupy the same two Tag coordinates.

QG-7c's exact M1 inventory proves that an irreducible comm-s2 block anticommutes with the shared Tag on both support coordinates. But the QG-7c T2 receipt states only `wt(S) <= 3 + #comm-s2` in the general irreducible sector; its weight-3 consolidation theorem is comm-s2-free/conditional on the open comm-s2 sector. Therefore P2 may not be imported from QG-7c without a separate proof.

F0 is an explicit hostile counterexample-first audit of P2. A positive refutation does **not** prove that the constructed configuration is an optimizer or that it survives every later normalization. It proves only that the proposed two-coordinate representation is not a theorem consequence of the currently earned local irreducibility/shared-label premises.

## 2. Frozen three-qubit hostile configuration

Use local Pauli codes `0=I, 1=X, 2=Y, 3=Z`. Local symplectic product is 1 iff both letters are nonidentity and distinct; n-qubit symplectic product is the XOR/sum mod 2 of local products.

Freeze the shared Tag and three ordered frame pairs exactly:

```
S  = (X, X, X)

A0 = (X, I, I)
A1 = (Y, I, I)

B0 = (Y, Y, I)
B1 = (Z, I, I)

C0 = (I, Y, Y)
C1 = (I, Z, I)
```

Intended shapes:
- A = anchored at coordinate 0;
- B = comm-s2 with support-two frame B0 on `{0,1}` and weight-one partner B1 at `a=0`;
- C = comm-s2 with support-two frame C0 on `{1,2}` and weight-one partner C1 at `a=1`.

The supports `{0,1}` and `{1,2}` are deliberately different.

## 3. Frozen gates

### F0.1 Parent custody

Require:
- QG-7e V2 committed result terminal is `QG7E_V2_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN`;
- `both_accept=true`;
- `PP_SINGLE_PINNER_ALL_N=true`;
- `CHAIN_ALL_N=false`;
- QG-7c result reports `G5_m1_inventory_complete=true` and `m1_inventory.holds=true`;
- QG-7c T2 reports `comm_s2` occupies exactly 2 anticommuting Tag qubits.

### F0.2 Shared-label feasibility

For each block j in {A,B,C} require:
- both frames nonzero;
- `symp(R_j0,R_j1)=1`;
- common labels `(symp(S,R_j0), symp(S,R_j1)) = (0,1)`.

### F0.3 M1-shape binding

A must satisfy the anchored local shape directly.

For B and C independently, bind exactly the QG-7c M1 `comm_s2` conditions:
- support weights `(w(R0), w(R1))=(2,1)`;
- support of R1 is coordinate `a`, contained in support(R0);
- if b is the other support coordinate of R0, then S is nonzero at both a,b;
- `local_symp(S[a],R0[a])=1` and `local_symp(S[b],R0[b])=1`;
- `R1[a] not in {I,S[a],R0[a]}`.

### F0.4 Lemma-E irreducibility control

For each comm-s2 block, there must be no support coordinate q of its support-two frame satisfying both:
- `local_symp(R0[q],R1[q])=0`; and
- `local_symp(S[q],R0[q])=0`.

This is the exact class-(0,0) single-zeroing reducibility control used by M1.

### F0.5 Representation refutation

Require simultaneously:
- `wt(S)=3`;
- both B and C pass F0.3/F0.4;
- `support(B0) != support(C0)`;
- each support is a subset of support(S).

If all gates pass, P2 is refuted under the current earned local structural premises.

## 4. Independent generic ORION

Generic ORION must rebuild all Pauli algebra from the frozen six tuples above, without importing production algebra or the production analyzer. It must independently derive weights, support sets, pair symplectic products, Tag labels, comm-s2 shape predicates and class-(0,0) reducibility.

## 5. Native ORION-Q responsibility

Native ORION-Q may authorize only:

`REPRESENTATION_PREMISE_REFUTATION`

It must keep all of the following false:
- `CHAIN_REPRESENTATION_COMPLETE`
- `CHAIN_ALL_N`
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS`
- `FIFTH_REGIME_FOUND`
- novelty/R6/physical-advantage authority.

## 6. Honest terminals

Strong refutation:

`QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION`

If the candidate fails an earned M1/shared-label gate:

`QG7F_F0_CANDIDATE_REJECTED__TWO_COORD_REDUCTION_UNRESOLVED`

If parent custody or independent verification fails:

`QG7F_CANNOT_CHECK_REPRESENTATION_PREMISE`

## 7. Successor rule

If P2 is refuted, no QG-7f successor may freeze a two-coordinate pin graph as complete. The next representation must either:
1. admit overlapping comm-s2 support pairs inside a higher-weight shared Tag and enumerate/canonicalize those finite support hypergraph types; or
2. first prove a new global theorem reducing the Tag support in the actual remaining chain sector.

Only after that representation obligation is closed may a chain normalization move library be prospectively frozen.
