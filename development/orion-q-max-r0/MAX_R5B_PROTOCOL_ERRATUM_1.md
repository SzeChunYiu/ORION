# MAX-R5B protocol erratum 1 — canonical local Pauli code order

Date: 2026-08-20
Status: **FROZEN BEFORE ANY R5B replay/accounting result**
Applies to: `MAX_R5B_PROOF_CARRYING_REPLAY_AND_OUTER_ACCOUNTING_PROTOCOL.md`

The protocol text accidentally wrote the canonical local base-4 order as `I,X,Z,Y`.

The already-verified ORION symplectic code used throughout R4D/R5 is:

`I=0, X=1, Y=2, Z=3`, i.e. canonical order **`I,X,Y,Z`**.

For the R5B proof-carrying replay, all lexicographic witness tie-breaking uses `I,X,Y,Z`. No scientific outcome has been computed under R5B before this correction, and no other gate, objective, source, or tie-break rule changes.
