# X1-D finding — 23-block C5 quotient packing with at least two unused indices

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Current frozen issue: #909 (to be superseded rather than mutated)

## Donor inputs

For `Q=C_5^3`:

- `eta(Q)=33`, so every sequence of length at least 33 contains a nonempty zero-sum subsequence of length at most 5.
- `D(Q)=13`.

## Packing theorem

Every 133-term sequence over `C_5^3` admits 23 pairwise-disjoint nonempty zero-sum subsequences while leaving at least **two unused terms**.

### Step 1 — 21 short blocks

Starting from 133 terms, repeatedly remove a zero-sum subsequence of length at most 5.

After 20 removals, at most 100 terms were removed, so at least 33 remain. Therefore eta=33 guarantees a 21st short zero-sum block.

After 21 removals, at most 105 terms were removed, so at least

`133-105 = 28`

terms remain.

Thus there exist 21 pairwise-disjoint quotient-zero-sum blocks, each of length at most 5, and a residual of size at least 28.

### Step 2 — two additional blocks from 26 residual terms

Any 26-term sequence over Q contains two disjoint nonempty zero-sum subsequences:

1. take any 13 selected terms; since `D(Q)=13`, they contain a nonempty zero-sum subsequence `Z_22` of length at most 13;
2. removing `Z_22` from the full 26-term selected set leaves at least 13 terms, which contain a second nonempty zero-sum subsequence `Z_23` by `D(Q)=13`.

Apply this to 26 of the at-least-28 residual terms. The two resulting zero-sum blocks use at most those 26 indices, leaving at least two original source indices unused.

Hence the full packing has:

- 21 short blocks of size <=5;
- 2 further zero-sum blocks of size <=13;
- at least 2 unused terms.

## Why this matters for the C45 split route

The live P5 proof requires 23 quotient blocks whose C9-kernel lift sums sit at the sharp `nu_3(C_9^3)=23` threshold, plus one legal correction escaping an exceptional affine index-3 coset.

The earlier #909 packing policy (20 short blocks + a 3-block base packing inside >=33 residual terms) did not guarantee any unused source indices. The new construction guarantees a residual of at least two indices **without reducing the 23-block count**.

Therefore every one-block exchange involving one of the 21 short blocks has a search universe of at most

`5 + |R|`

indices; in the worst minimal-residual case this is at most 7 indices. This sharply reduces the local exchange state for the next prospectively frozen search.

## Protocol consequence

#909 froze a different packing policy before this donor-derived improvement was found. Do not edit that frozen policy after the fact. The correct action is to preserve #909 and open a fresh successor freeze using the stronger residual-two packing.

## Claim boundary

This is an elementary consequence of donor constants eta(C5^3)=33 and D(C5^3)=13. It is a programme/packing improvement, not a mathematical novelty claim. Novelty can only arise from an all-sequence correction-escape/obstruction theorem or new Davenport result.
