# Rank-three `a>=4` doubling reduction to a thin new-value boundary — V1

Status: **proved prime-uniform structural theorem**. In the first-corridor exact-support-six rank-three face, every canonical support-four maximal type `a>=4` is forced onto a thin boundary strip in the two genuinely new multiplicities. Any box with both new multiplicities above `(p-1)/2` contains a forbidden zero-sum of length exactly `p-1`.

This uses `SUPPORT4_SIMULTANEOUS_OVERLAP_SUM_BOUND_V1.md` and is independent of the bounded rank-three discovery scan.

No support-seven theorem, generalized Davenport value, or novelty/priority claim is made here.

## 1. Setup

Let

`p=2H+1`, `m=3H+1`,

and let the support-four maximal atom have canonical type

`4<=a<=H`.

Assume the exact-support-six equality face is rank three:

`V=s^c g^d x^r y^t`,

where all multiplicities are positive, `r<=t`, and

`c+d+r+t=m`.

The simultaneous-overlap theorem gives

`boxed{c+d<=a-2.}`

Put

`S=c+d`.

Then

`S<=a-2<=H-2`.

## 2. Literal overlap resources in the pair

The maximal atom contains

- `a` copies of `s`;
- `p-a` copies of `g`.

The companion contributes another `c` copies of `s` and `d` copies of `g`.

Thus the pair `UV` contains

`s^(a+c) g^(p-a+d)`

on the two overlap values.

Because `c+d<=a-2` and `d>=1`,

`c<=a-3`,

so

`2c<=a+c`.

Also

`d<=a-3<p-a`,

since `a<=H` gives `p-a>=H+1>=a+1`. Hence

`2d<=p-a+d`.

Therefore the pair contains at least `2c` literal copies of `s` and `2d` literal copies of `g`.

## 3. Doubling when `r>H`

Assume

`r>H`.

Since `t>=r`, also `t>H`.

Double the companion relation

`c s+d g+r x+t y=0`.

Because `H<r,t<p`, the least positive residues of the two new-value coefficients are

`R=2r-p`, `T=2t-p`.

They satisfy

`1<=R<=r`, `1<=T<=t`.

Thus

`x^R y^T`

is an actual subsequence of `V`, and its group sum is

`-2c s-2d g`.

Section 2 provides the literal cancelling subsequence

`s^(2c) g^(2d)`

inside `UV`.

Hence

`x^R y^T s^(2c) g^(2d)`

is a nonempty zero-sum subsequence of the pair.

Its length is

`R+T+2c+2d`

`=(2r-p)+(2t-p)+2S`

`=2(r+t+S)-2p`

`=2m-2p`

`=2(3H+1)-2(2H+1)`

`=boxed{2H=p-1.}`

Since `p-1<m`, this contradicts the inherited pair short-freeness.

Therefore:

> `boxed{r<=H.}`

for every surviving rank-three box of type `a>=4`.

## 4. Thin-boundary parameterization

Since

`r+t=m-S=3H+1-S`

and `t<=p-1=2H`, one also has

`r>=H+1-S`.

Thus every survivor satisfies

`H+1-S<=r<=H`.

Write

`boxed{r=H-k}`

with

`0<=k<=S-1`.

Then automatically

`boxed{t=p-S+k.}`

Hence the entire rank-three `a>=4` multiplicity problem is reduced to the strip

`0<=k<=c+d-1`,

whose width is at most

`c+d<=a-2`.

This is the rank-three analogue of the boundary-strip reductions that drove the support-three proof.

## 5. Strategic consequence

The bounded scalar-plane discovery previously scanned a two-dimensional `(r,t)` region. The present theorem shows that an all-prime proof never needs such a search for `a>=4`:

1. choose the overlap pair `(c,d)` with `c+d<=a-2`;
2. choose only the boundary index `k=0,...,c+d-1`;
3. set `r=H-k`, `t=p-c-d+k`;
4. apply the exact overlap-plane scalar certificate or quotient atomicity.

The next rank-three theorem should therefore be a boundary scalar/stability statement in `(c,d,k)`, not a four-multiplicity classification.

## Verification receipt

`check_support4_rank3_a_ge4_doubling_boundary_reduction_v1.py` verifies the resource inequalities, doubled coefficient residues, exact `p-1` length identity, and boundary parameterization for every prime through `2003`, every canonical type `a>=4`, and every positive `(c,d)` satisfying the proved simultaneous-overlap sum bound.

The checker is regression only; theorem authority is the literal doubling argument above.

## Boundary

- The thin boundary `r<=H` remains to be eliminated.
- Types `a=2,3` are not covered by the simultaneous-overlap sum theorem.
- No `D_3(C_p^3)` value or all-k formula is claimed.
