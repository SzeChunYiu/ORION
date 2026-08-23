# X1-F exact bounded finding — Freeze--Schmid C_5^3 k=3 witness is insertion-saturated

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Replay checker: `research/orion-rg/x1f_freeze_schmid_c5cube_saturation.py`
Checker commit: `602d15b663472fb7b2b415e3afeab1e64651d501`

## Status

**CONFIRMATORY AFTER EXPLORATORY CALCULATION.**

The exact outcome was first observed in an exploratory private calculation. The committed checker independently reconstructs the statement from primitive C5^3 addition and exhaustive submultiset packing. This is not a blind prospective result.

## Freeze--Schmid lower witness

Specialize Freeze--Schmid Theorem 4.1 to `G=C_5^3`, `k=3`, `r=s=3`, `t=1`.

With basis e1,e2,e3 and injection of the three pairs to the three coordinates, set

- `g1=e1+e2`,
- `g2=e1+e3`,
- `g3=e2+e3`.

The proof's explicit sequence is represented by multiplicities

`e1^4 e2^4 e3^9 g1^2 g2^2 g3^3`,

of total length 24. It has no three pairwise-disjoint nonempty zero-sum submultisets, establishing the lower bound `D_3(C_5^3)>=25`.

## Exhaustive one-term extension result

For every `x in C_5^3` (all 125 group elements), form the 25-term sequence `S x`.

The checker:
1. enumerates every nonempty zero-sum submultiset of the resulting multiset exactly;
2. checks by exhaustive count-vector packing whether three such submultisets can be chosen pairwise disjointly;
3. repeats for all 125 possible x.

Result:

- base 24-term witness: no 3 disjoint zero sums;
- one-term extensions checked: 125/125;
- extensions still failing 3 disjoint zero sums: **0**.

Thus the explicit Freeze--Schmid lower witness is **insertion-saturated**: every possible single-term extension has three disjoint nonempty zero-sum subsequences.

## What this does and does not imply

It does **not** prove `D_3(C_5^3)=25`. A different 25-term sequence could still fail three disjoint zero sums.

It does show:
- the canonical general lower-bound construction cannot be extended to improve the lower bound;
- the lower-bound witness lies exactly on a local maximal obstruction boundary;
- `D_3(C_5^3)=25` becomes a particularly natural sharpness hypothesis to attack, but remains open/unchecked globally.

## Relevance to C45

If a theorem eventually proves `D_3(C_5^3)=25`, then the C45 split route becomes much stronger. After 21 short extractions from 133 terms, at least 28 remain; `D_3=25` would force three more quotient zero-sum blocks in the residual, yielding 24 total blocks while leaving at least three source terms. The 24 C9-kernel block sums would then have maximal zero-sum-free length, giving complete nonzero subsequence-sum coverage rather than only the near-maximal affine-coset guarantee.

This makes exact determination of `D_3(C_5^3)` a high-value mathematical subproblem of X1-E.

## Claim boundary

Finite exhaustive computation on one explicit witness receives no theorem/novelty authority. The Freeze--Schmid construction is donor-owned. The only new factual content here is the exact bounded insertion-saturation property of that witness, pending independent external replay if promoted beyond internal research state.
