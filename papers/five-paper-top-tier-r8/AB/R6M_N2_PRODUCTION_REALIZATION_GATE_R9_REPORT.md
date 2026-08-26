# R6M n=2 production-realization gate execution (R9)

## Frozen question

Can the AB weak-certificate terminal budget be transferred to the current Pauli/TARE R6M production implementation merely because the finite `n=2` optimizer can be exhaustively replayed?

## Bound sources

The execution binds source commit `1e18787841d99d76a3c7661505838d2eca8780db`, the exact R6M protocol/runner/result blobs, the support-two donor protocol/runner/result blobs, and the Q1 manuscript and claim ledger. The executable receipt verifies both Git blob SHA-1 and file SHA-256 for every bound object before enumeration.

## Smallest complete finite replay

The registered `n2_a` hostile panel is replayed over all 32 outer choices (four relative permutations times eight central-branch choices). For every outer choice, the R6M dynamic program is checked against the independent global-Pauli brute evaluator. Each brute evaluation covers 983,040 feasible shared-Tag/orientation/frame triples, for 31,457,280 candidate evaluations in total.

All 32 DP/brute comparisons agree. The exact cost histogram is:

| Structural cost | Outer configurations |
|---:|---:|
| 6 | 8 |
| 7 | 20 |
| 8 | 4 |

This establishes finite current-runner agreement only.

## Why the gate rejects

R6M defines feasibility, objective evaluation, exhaustive candidate enumeration and a deterministic argmin. It does **not** define an extensional semantics-preserving shortening-move registry. Moving from one optimizer choice to a lower-cost choice is not automatically a declared production rewrite. Therefore the execution does not invent weak or production moves, and it deliberately sets `production_registry.declared_complete=false`.

The authoritative V2 checker returns exactly:

`FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED`

with the sole issue:

`PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE`

The checker-reported zero certificate waste for the empty declared move lists is **not interpretable** as a production result; the registry is incomplete and the terminal is rejected.

## Authority boundary

The receipt supports all of the following narrow statements:

- the bound source bytes match the frozen identities;
- the smallest registered `n=2` panel was exhaustively replayed;
- every DP result agrees with the independent brute evaluator; and
- the application correctly fails closed at the missing extensional move registry.

It does not establish an R6M production lower bound, a complete compiler grammar, quantum advantage, novelty, external validation or journal authority. Promotion requires an explicit semantics-preserving production move registry, an omission-hostile completeness argument, objective nonincrease for every move, and a realizing witness irreducible under all admitted moves.

## LUNARC execution binding

The same frozen payload at Git SHA `a70a1abc9b645bf66dc14864cdff11cd6a06fd1f` was replayed by LUNARC job `3543875`, which completed with exit code `0:0` after 31,457,280 candidate evaluations. The result and certificate bytes match the committed SHA-256 digests exactly. `R6M_N2_LUNARC_EXECUTION_RECEIPT_R9.json` binds the SLURM state, source SHA, output hashes, preserved adverse terminal and authority ceiling; its SHA-256 is `adfff444457a370be673ad0fa7f17ffeaf7c013228aa1e829dcdf741ec3b2f91`. Jobs `3543870` and `3543874` are retained as wrapper-only failures before the scientific entrypoint and produced no scientific outcome.
