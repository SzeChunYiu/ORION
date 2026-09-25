# First-corridor `a=2` light-share multiplicity four is impossible — V1

Status: **proved prime-uniform branch elimination for every prime `p>=7`, with one bounded exact base at `p=13`**. Together with the one-, two-, and three-share theorems, every hypothetical `a=2` light-share support-three equality companion now has shared multiplicity at least five.

No generalized Davenport value or novelty/priority claim is made here.

## 1. Setup and the uniform interior reduction

Write

`p=2H+1`, `m=(3p-1)/2=3H+1`,

and use

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

`g=s-2^(-1)(e1+e2)`.

Assume an exact-support-six first-corridor support-three companion shares the light value exactly four times:

`V=s^4 x^r y^t`, `r<=t<=p-1`.

Then

`4s+r x+t y=0`, `r+t=3H-3`.

By `RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md`, every survivor has

`r=H-3+d`, `t=2H-d`, `d in {0,1,2,3}`.

Thus only four boundary rows remain for each prime.

We use the certified radial costs

`lambda(5)<=5`, `lambda(6)<=6`, `lambda(7)<=9`, `lambda(10)<=14`,

coming from the six actual copies of `s` in `UV` and the identity

`2s=2g+e1+e2`.

Whenever a scalar multiple gives residues `(D,A,B)` with `A<=r`, `B<=t` and `lambda(D)+A+B<m`, it produces a forbidden short zero-sum. If instead `D<=4`, `A<=r`, `B<=t`, it is a nonempty proper coefficient relation inside `V`, contradicting atomicity.

## 2. Boundary `d=0`

### `p=8k+1`

Take `n=6k+2`. Then

`(D,A,B)=(5,3k-4,2k-1)`.

The radial realization has length

`5+(3k-4)+(2k-1)=5k<m=12k+1`.

### `p=8k+3`

Take `n=4k+2`. Then

`(D,A,B)=(2,2k-1,4k+1)`

is componentwise bounded by `(4,r,t)`, hence is a proper zero-sum subsequence of `V`.

### `p=8k+5`

For every prime in this class beyond `p=13`, one has `k>=3`. Take `n=2k+2`. Then

`(D,A,B)=(3,k-2,6k+3)`

is a proper coefficient relation inside `V`.

The prime `p=13` is the sole arithmetic resonance and is handled exactly in Section 6.

### `p=8k+7`

Take `n=2k+2`. Then

`(D,A,B)=(1,k,6k+5)`

is a proper coefficient relation inside `V`.

Hence `d=0` is empty except for the bounded `p=13` resonance.

## 3. Boundary `d=1`

For the four residue classes of `p` modulo eight:

- `p=8k+1`: `n=2k+2` gives `(7,3k-4,4k-3)` and total radial length `7k+2<m`;
- `p=8k+3`: `n=2k+2` gives `(5,3k-2,4k-1)` and total length `7k+2<m`;
- `p=8k+5`: `n=2k+2` gives the proper coefficient relation `(3,3k,4k+1)`;
- `p=8k+7`: `n=2k+2` gives the proper coefficient relation `(1,3k+2,4k+3)`.

Thus `d=1` is empty for every admissible prime.

## 4. Boundary `d=2`

Again split modulo eight.

- `p=8k+1`: `n=2k+1` gives the proper coefficient relation `(3,k-1,2k-2)`.
- `p=8k+3`: `n=2k+1` gives the proper coefficient relation `(1,k,2k)`.
- `p=8k+5`, `p>13`: `n=2k+3` gives `(7,k-2,2k-4)`, of radial length `3k+3<m`.
- `p=8k+7`: `n=4k+4` gives the proper coefficient relation `(2,2k+1,4k+2)`.

At `p=13`, take `n=8`; the residues are `(6,1,2)`, whose radial length is `6+1+2=9<19`.

Hence `d=2` is empty.

## 5. Boundary `d=3`

- `p=8k+1`: take `n=4k+3`. The residues are `(10,2k-1,p-10)` and the radial length is `10k+4<m=12k+1`.
- `p=8k+3`: take `n=4k+3`. The residues are `(6,2k,p-6)` and the radial length is `10k+3<m=12k+4`.
- `p=8k+5`, `p>13`: take `n=2k+3`. The residues are `(7,3k+1,p-7)` and the radial length is `11k+8<m=12k+7` for `k>=3`.
- `p=8k+7`: take `n=2k+3`. The residues are `(5,3k+2,p-5)` and the radial length is `11k+9<m=12k+10`.

At `p=13`, take `n=11`; the residues are `(5,1,8)` and the radial length is `14<19`.

Thus `d=3` is empty.

## 6. The sole scalar resonance: `p=13`, `d=0`

Here

`(p,c,r,t)=(13,4,3,12)`

and the atom relation is

`4s+3x-y=0`, so `y=4s+3x`.

Use standard coordinates

`s=(0,0,1)`, `e1=(1,0,0)`, `e2=(0,1,0)`,

`g=s-7(e1+e2)`.

The first-corridor plane condition says `K=span(s,x)` meets `supp(U)` only in `s`. Writing `x=(a,b,c0)`, this is equivalent to

`a!=0`, `b!=0`, `a!=b`.

Therefore the complete structural universe has

`13*12*11=1716`

parameters.

For every such `x`, set `y=4s+3x` and test every nonempty proper subsequence

`W=s^i x^j y^k`,

`0<=i<=4`, `0<=j<=3`, `0<=k<=12`,

against the exact graded condition

`|W|+rho_U(-sigma(W))>=19`.

Two independent implementations give:

- structural parameters: **1716**;
- parameters passing both new-value singleton inequalities: **78**;
- parameters passing the full graded condition: **0**.

The complete minimum-score histogram is

| score | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| count | 4 | 18 | 58 | 132 | 246 | 352 | 420 | 272 | 124 | 40 | 44 | 6 |

No structural parameter reaches the required score `19`. As a positive mutation control, lowering the artificial threshold to `14` leaves exactly six states.

`check_a2_light_support3_four_share_elimination_v1.py` uses the closed support-four depth formula; `verify_a2_light_support3_four_share_independent_v1.cpp` rebuilds `rho_U` occurrence-by-occurrence from the actual maximal atom before replaying the complete structural universe.

## 7. Theorem

Combining Sections 2--6:

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=2` cannot have a support-three rank-two light-share companion with
>
> `v_e3(V)=4`.

Together with the previous light-share theorems,

`boxed{v_e3(V)>=5}`

for every hypothetical `a=2` light-share support-three equality companion.

The exact multi-copy ceiling remains

`v_e3(V)<=2 floor((p-1)/4)`.

Consequently the entire `a=2` support-three branch is now analytically empty not only at `p=7` but also at `p=11`, where the ceiling is four.

## Boundary

- The light-share family with `c>=5` remains open for larger primes.
- The rank-three support-four equality face remains open.
- The `p=13` finite base is exact computational authority backed by two structurally different implementations; it is not promoted to an all-prime argument.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
