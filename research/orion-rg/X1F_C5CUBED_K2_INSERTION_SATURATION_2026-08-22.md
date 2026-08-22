# X1-F exact bounded finding — Freeze--Schmid C_5^3 k=2 witness is insertion-saturated

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #915
Replay checker: `research/orion-rg/x1f_freeze_schmid_c5cube_k2_saturation.py`
Checker commit: `f2048b9c745aca636b06ffef0153fb844550bc81`

## Status

**CONFIRMATORY AFTER EXPLORATORY CALCULATION.**

## Exact witness

Freeze--Schmid Theorem 4.1 specialized to `C_5^3`, `k=2`, `r=s=3`, `t=1` gives the explicit 19-term sequence

`e1^4 e2^4 e3^4 g1^2 g2^2 g3^3`,

where `g1=e1+e2`, `g2=e1+e3`, `g3=e2+e3`.

It has no two pairwise-disjoint nonempty zero-sum submultisets, establishing the donor lower bound `D_2(C_5^3)>=20`.

## Exhaustive one-term extensions

The checker examines every `x in C_5^3`, all 125 group elements, and exactly enumerates zero-sum submultisets of the 20-term extension `Sx`.

Result:
- extensions checked: 125/125;
- extensions still failing two disjoint zero sums: 0.

Thus the explicit 19-term Freeze--Schmid obstruction is **insertion-saturated**.

## Structural consequence for X1-F

This does not prove `D_2(C_5^3)=20`; a different 20-term obstruction could exist.

However, if the exact equality `D_2=20` can be established, then every atom A dividing a hypothetical 26-term zero-sum sequence `B in M_3(C_5^3)` must satisfy

`|A| >= 26-D_2 = 6`,

because the zero-sum remainder `B A^(-1)` must lie in `M_2`.

Any 3-atom factorization of B would then have atom-length triple summing to 26 with each entry in `[6,13]`, a substantial inverse-structure restriction.

Together with the independently committed k=3 insertion-saturation result, the data motivate—but do not establish—the sharpness hypothesis

`D_2(C_5^3)=20`, `D_3(C_5^3)=25`.

## Claim boundary

The donor witness and lower bound are Freeze--Schmid's. The only internal new fact here is exact bounded insertion saturation of that witness. No exact D2/D3 or novelty authority is claimed.
