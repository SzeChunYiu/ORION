# X1-B k=4 — independent replay closes R2R-11 and R2R-12

Parent: #900.
Primary protocol: `X1B_K4_RANK2_RADICAL_FINAL_PREFIX_PROTOCOL.md`.
Independent verifier: `x1b_k4_rank2_radical_final_prefix_nomemo_replay.cpp`.

## Independence

This replay does not use the primary search representation or pruning:

- it carries the represented subset-sum set `Sigma_0(T)` directly;
- it does not use the illegal-next-term state `I(T)`;
- no memoization;
- no layerwise dynamic programming;
- no state merging;
- no minimum-last dominance.

The only quotient is the same mathematically necessary nondecreasing multiset ordering to avoid sequence-permutation duplicates.

## R2R-11

Fresh run:

```text
class 11 found 0 nodes 79487138 maxdepth 9
```

Therefore:
- no length-10 admissible prefix exists;
- exact maximum length is 9;
- canonical multiset nodes replayed: **79,487,138**.

## R2R-12

Fresh run:

```text
class 12 found 0 nodes 54683021 maxdepth 9
```

Therefore:
- no length-10 admissible prefix exists;
- exact maximum length is 9;
- canonical multiset nodes replayed: **54,683,021**.

## Agreement with primary enumeration

The independent results agree with the prospectively frozen primary layerwise enumerations:

- R2R-11: primary NO / max 9; independent NO / max 9;
- R2R-12: primary NO / max 9; independent NO / max 9.

The node counts differ substantially, as expected from the algorithmic independence.

## Consequence for the radical family

The complete radical census reduced every rank-2 radical realization to either:

1. a forbidden set containing one of the already independently closed patterns; or
2. one of the two final classes R2R-11 or R2R-12.

Both final classes are now independently NO.

Hence **the complete rank-2 radical realization branch of the k=4 residual is eliminated**.

Together with the independently closed rank-3 completion branch, there is no remaining rank<=3 bilinear realization compatible with the frozen k=4 residual requirements.

## Authority boundary

This closes the finite rank-2 radical branch. A separate proof-assembly packet must still verify the full chain from a hypothetical C15 counterexample to these finite interfaces before declaring k=4 closed, and k=3 remains separately gated before any `D(C_15^3)=43` theorem claim.