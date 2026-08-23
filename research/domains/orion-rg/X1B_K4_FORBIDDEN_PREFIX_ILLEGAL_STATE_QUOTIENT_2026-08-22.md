# X1-B k=4 — exact illegal-next-state quotient for forbidden-prefix search

Parent: #900.
Frozen search protocol: `X1B_K4_RANK3_FORBIDDEN_PREFIX_PROTOCOL.md`.
Committed before use in the authoritative search implementation.

## Setup

Let `G=F_5^3`, let `F subset G` be one frozen forbidden set containing zero, and let

`Sigma_0(T)={sum(U): U <= T}`

include the empty subset sum 0.

The frozen condition is

`(Sigma_0(T) \ {0 from the empty subset only}) cap F = empty`,

implemented incrementally by requiring, before appending a term x,

`(Sigma_0(T)+x) cap F = empty`.

## Illegal-next-term state

Define

`I(T)=F-Sigma_0(T)={f-s : f in F, s in Sigma_0(T)}`.

Then x is an illegal next term exactly when

`x in I(T)`.

Indeed,

`x in F-Sigma_0(T)`

iff there exist `f in F`, `s in Sigma_0(T)` with `x=f-s`,

iff `s+x=f in F`,

iff `(Sigma_0(T)+x) cap F` is nonempty.

Thus the full future legality interface depends on `I(T)` alone.

## Exact update

After appending a legal x,

`Sigma_0(Tx)=Sigma_0(T) union (Sigma_0(T)+x)`.

Therefore

`I(Tx)`
`=F-Sigma_0(Tx)`
`=(F-Sigma_0(T)) union (F-(Sigma_0(T)+x))`
`=I(T) union (I(T)-x)`.

Hence the exact transition is

> `I' = I union (I-x)`.

The initial state is `I(empty)=F`.

## Consequence for exhaustive search

The prospectively frozen multiset enumeration can be implemented with:

- one 125-bit set I;
- current depth;
- last canonical element index (to quotient only by sequence permutation);
- transition `I -> I union (I-x)` for legal `x notin I`.

Memoization on `(I, depth, last_index)` is exact because two prefixes with the same triple have identical admissible future continuations under the frozen ordering.

No group symmetry, heuristic pruning, or weakened success criterion is introduced.

## Claim boundary

This is an elementary exact search-state quotient. It is an implementation theorem for the frozen finite discriminator, not a C15 theorem or novelty claim.