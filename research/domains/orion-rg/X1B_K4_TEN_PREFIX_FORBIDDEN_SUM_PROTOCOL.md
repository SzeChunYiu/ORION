# X1-B k=4 — prospective exact ten-prefix forbidden-subset-sum discriminator

Parent: #900.
Input: common rank-2 residual lift and its three residual block-sum pair types.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No exhaustive length-10 existence/nonexistence outcome is known at freeze time.

## Exact equivalence

The three unordered residual pair types in `C_5^3` are

```text
P1={(0,2,0),(3,2,0)}
P2={(0,2,0),(0,2,0)}
P3={(1,0,0),(2,4,0)}.
```

Let T be a ten-term sequence in `C_5^3`. Each pair itself is zero-sum-free.

For one pair P={x,y}, the twelve-term sequence `Txy` is zero-sum-free iff:

1. T is zero-sum-free; and
2. no nonempty subset sum of T equals `-x`, `-y`, or `-(x+y)` (with duplicate-pair subset sums interpreted positionally).

Therefore all three extensions are simultaneously maximal zero-sum-free iff the nonempty subset sums of T avoid exactly

```text
S_bad = {
  (0,0,0),
  (0,1,0), (2,1,0), (0,3,0),
  (3,1,0), (4,0,0), (2,3,0)
}.
```

Thus the final common-prefix question is an exact finite extremal problem:

> Does there exist a length-10 sequence T over `F_5^3` whose every nonempty subset sum avoids `S_bad`?

A YES gives an explicit ten-block-sum obstruction surviving all current block-sum/group-algebra gates. A NO eliminates both final k=4 quotient orbits.

## Symmetry normalization

`S_bad` spans and lies in the plane `z=0`. Any length-10 admissible T must contain an element outside this plane; otherwise T would be a length-10 zero-sum-free sequence in `C_5^2`, impossible since `D(C_5^2)=9`.

The linear stabilizer of `S_bad` in `GL(3,5)` fixes the plane pointwise and acts transitively on off-plane vectors by shears/scaling. Hence one off-plane term may be normalized to

`e3=(0,0,1)`.

After fixing e3, no further nontrivial stabilizer is assumed in the authoritative search.

## Frozen exhaustive search

Maintain the exact represented subset-sum set `Sigma_0(T)` including the empty sum 0.

Adding x is legal iff `(Sigma_0(T)+x)` avoids `S_bad`; then update

`Sigma_0(Tx)=Sigma_0(T) union (Sigma_0(T)+x)`.

Search all multisets extending the normalized `e3` term to total length 10. Permutation duplicates may be removed by canonical multiset ordering or an equivalent memoized subset-sum-state traversal, provided completeness is independently checked.

Required outputs:
- whether length 10 exists;
- maximum length reached if NO;
- explicit witness if YES;
- node/state counts and symmetry assumptions;
- independent primitive subset-sum replay;
- `CANNOT_CHECK_RESOURCE_BOUND` if exhaustive closure is not achieved.

A length-9 witness alone is not a negative proof. A length-10 witness is still only a block-sum obstruction, not a 43-term C15 counterexample.