# ORION-Q MAX-R5G H4 independent replay protocol

Date: 2026-08-20
Parent: #679 / #698
Branch: `shadow/orion-q-max-r0`
Status: frozen after R5F outcome and before the second implementation is run.
Authority: independent hostile verification only; cannot self-authorize novelty/R6.

## Object under replay

R5F fresh H4 confirmation reported:

- locked source blob `b98792b1055dbac0ebf2a7576f72412e3e4ac6c5`;
- 8 qubits, 268 nonidentity Pauli terms, no singleton;
- B* `(Lambda,CNOT,T,direct) = (5.15888533051182, 5332, 43148, 0)`;
- E `(Lambda,CNOT,T,direct) = (4.862865511405695, 4198, 40224, 86)`;
- 228,693 perfect matchings exhaustively evaluated;
- frozen pair/witness/sorted-term hashes:
  - sorted terms `39d5897efd90f9ab3e639cd5586d06b46e9fccb3e04bb675a23e0798280c1a6b`;
  - B* pair list `917b0dbf4a380225e609e78918252a4bf2ddb3ed8180c52247d676d0e34f4611`;
  - E pair list `c516fcac4914190beefc099823b7933e8af449aa8723c882c78accd5c30c5608`;
  - B* proof `29cf9f601d4a783cbb2398fabdecb55193a6bd3816a877fb722d4a66f77ff889`;
  - E proof `9dd11ff0cbac36373a7da4ccd4625153aa0cb9527e6bf6400d29377e1f5381a1`.

## Independence requirements

The replay implementation may reuse only the previously verified DUCC -> Jordan-Wigner semantic layer. It must **not import** the R5C/R5E/R5F compiler, controlled-cost DP, matching frontier, or proof functions.

It must independently implement:

1. Pauli symplectic arithmetic;
2. direct-block classification and orientation;
3. the controlled TARE m=2 representation search by enumerating all 64 `(r0,r1,s)` local triples per qubit inside a dictionary dynamic program;
4. both global Restore-base branches and both target orientations;
5. full witness reconstruction and semantic assertions;
6. quartet B* reconstruction;
7. exhaustive perfect matchings in every 12-term window;
8. an independently coded exact global Pareto composition under `direct_delta >= 0` and `DeltaLambda <= 1% * Lambda(B*)`;
9. canonical sorted-term, pair-list and witness hashes.

## Frozen replay gates

All must hold:

- source blob and 8-qubit JW semantics reproduce;
- sorted-term hash matches R5F;
- B* pair-list hash matches R5F;
- E pair-list hash matches R5F;
- B* proof hash matches R5F, or, if an exactly tied alternative witness is found, every witness verifies and aggregate resource values match while the tie is explicitly reported;
- E proof hash matches R5F under the same caveat;
- all B*/E aggregate values match within floating tolerance / exactly for integral resources;
- 228,693 perfect matchings are independently enumerated;
- independently reconstructed E is the exact minimum controlled-CNOT state in the frozen disjoint-window search under the normalization/direct gates;
- R5F's sign remains positive for CNOT, T and normalization-weighted CNOT/T.

## Failure response

Any mismatch reopens R5F. A replay mismatch is not resolved by changing the expected hashes or relaxing the resource gates; responsibility must be diagnosed first.

## Positive terminal

At most:

`MAX_R5G_H4_INDEPENDENT_REPLAY_GREEN`

The next step remains donor-composed audit + hostile novelty, not R6 by fiat.
