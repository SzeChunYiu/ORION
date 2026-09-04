# First-corridor `a=1` four-share support-three face is impossible — V1

Status: **proved elimination of the shared-multiplicity `c=4` slice for every prime `p>=7`**, with three exact small-prime depth bases and an independently generated hostile replay. No generalized Davenport value or novelty/priority claim is made here.

## 1. Setup

Let `p=2q+1>=7` be prime and put

`m=p+q=(3p-1)/2`.

In the saturated coordinates of the preceding `a=1` files,

`U=f1^(p-1) f2^(p-1) f3^(p-1) s`,

where `s=f1+f2+f3`.

Assume an exact-support-six first-corridor companion in the support-three equality branch has

`V=s^4 x^r y^t`, `r<=t`,

so

`r+t=m-4=3q-3`

and the atom relation is

`4s+r x+t y=0`.

The pair `UV` is `(m-1)`-short-zero-free. It contains five actual copies of `s`: four from `V` and one from `U`.

## 2. Relation-multiple certificate

For `1<=n<=p-1`, put

`d=[4n]_p`, `A=[rn]_p`, `B=[tn]_p`,

with residues in `{1,...,p-1}`. Multiplying the atom relation by `n` gives

`d s+A x+B y=0`.

If `A<=r` and `B<=t`, the `x,y` terms occur in `V`. The `d` copies of `s` can be realized in `UV` at cost

`lambda_4(d)=d`, for `d<=5`,

and

`lambda_4(d)=3d-10`, for `d>5`,

because every copy after the five actual `s` terms may be replaced by `f1+f2+f3`.

Hence any multiplier satisfying

`A<=r`, `B<=t`, `lambda_4(d)+A+B<=m-1`

produces a forbidden short zero-sum in `UV`.

We will repeatedly use the harmless bound

`lambda_4(d)<=3d`.

## 3. Multiplicity corridor

Since `t<=p-1=2q`, one has `r>=q-3`. Therefore the entire multiplicity range consists of

- four boundary rows `r=q-3,q-2,q-1,q`; and
- the interior `r>=q+1`.

Equivalently, write

`r=q-3+k`, `t=p-1-k`.

The boundary is exactly `k=0,1,2,3`.

## 4. Interior

This is the `c=4` specialization of `RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md`. For completeness, assume `r>=q+1`. Then also `t>=q+1`. For `p>=13`, take `n=2`. One gets

`d=8`, `lambda_4(d)=14`,

`A=2r-p`, `B=2t-p`,

and, because `r+t=m-4`,

`A+B=p-9`.

Thus the mixed zero-sum has length

`p+5<=m-1`

exactly when `p>=13`.

The only interior row below this range is

`(p,r,t)=(11,6,6)`.

The multiplier `n=4` gives `(d,A,B)=(5,2,2)` and length `9<=15=m-1`.

## 5. Lower endpoint `k=0`: `r=q-3`, `t=p-1`

The endpoint is controlled by the denominator `c+1=5`. According to the odd prime residue modulo ten, choose the following multiplier.

| `p` | `n` | `d` | `A` | `B` | range |
|---|---:|---:|---:|---:|---|
| `10h+1` | `8h` | `2h-3` | `2h+3` | `2h+1` | `h>=3` |
| `10h+3` | `8h+2` | `2h-1` | `2h+2` | `2h+1` | `h>=2` |
| `10h+7` | `8h+6` | `2h+3` | `2h` | `2h+1` | `h>=1` |
| `10h+9` | `8h+8` | `2h+5` | `2h-1` | `2h+1` | `h>=1` |

These multipliers are respectively

`(4p-4)/5`, `(4p-2)/5`, `(4p+2)/5`, `(4p+4)/5`.

In every displayed range the coefficients fit. Using `lambda_4(d)<=3d`, the corresponding total lengths are at most

`10h-5`, `10h`, `10h+10`, `10h+15`,

all at most `m-1` in their stated ranges.

Two small rows are outside the table:

- `(p,r,t)=(11,2,10)` is killed by `n=6`, giving `(d,A,B)=(2,1,5)` and length `8`;
- `(p,r,t)=(13,3,12)` remains after every relation-multiple certificate and is one of the exact bases in Section 9.

## 6. Lower inner boundary `k=1`: `r=q-2`, `t=p-2`

Here the denominator is `c-1=3`.

### `p=6h+1`

For `h>=2`, take `n=2h=(p-1)/3`. Then

`d=2h-1`, `A=h+1`, `B=2h+1`.

The coefficients fit and

`lambda_4(d)+A+B<=9h-1<=m-1=9h`.

The omitted row `p=7`, namely `(4,1,5)`, is an exact base.

### `p=6h+5`

Take `n=2h+2=(p+1)/3`. Then

`d=2h+3`, `A=h`, `B=2h+1`.

For `h=1` the length is `9<=15`. For `h>=2`,

`lambda_4(d)=6h-1`,

so the total is `9h<=m-1=9h+6`.

## 7. Upper inner boundary `k=2`: `r=q-1`, `t=p-3`

Again use denominator three.

### `p=6h+1`, `h>=3`

Take `n=2h-1=(p-4)/3`. Then

`d=2h-5`, `A=2`, `B=4`,

and

`lambda_4(d)+A+B<=6h-9<=m-1=9h`.

The two omitted primes have direct multipliers:

- `p=7`: `n=4` gives `(d,A,B)=(2,1,2)` and length `5`;
- `p=13`: `n=8` gives `(d,A,B)=(6,1,2)` and length `11`.

### `p=6h+5`

Take `n=2h+1=(p-2)/3`. Then

`d=2h-1`, `A=1`, `B=2`,

and the total is at most `6h<=m-1=9h+6`.

## 8. Upper endpoint `k=3`: `r=q`, `t=p-4`

The second endpoint is again controlled by denominator five.

| `p` | `n` | `d` | `A` | `B` | range |
|---|---:|---:|---:|---:|---|
| `10h+1` | `8h+1` | `2h+1` | `h` | `8h` | `h>=3` |
| `10h+3` | `8h+3` | `2h+3` | `h` | `8h` | `h>=1` |
| `10h+7` | `8h+5` | `2h-1` | `h+1` | `8h+8` | `h>=3` |
| `10h+9` | `8h+7` | `2h+1` | `h+1` | `8h+8` | `h>=2` |

These are respectively

`(4p+1)/5`, `(4p+3)/5`, `(4p-3)/5`, `(4p-1)/5`.

In the displayed ranges the exact costs give totals at most

`15h-7`, `15h-1`, `15h-4`, `15h+2`,

where the isolated cases with `d=5` are even shorter. Each bound is at most the corresponding value of `m-1`.

The omitted small rows are:

- `p=7`, killed by `n=3`, with `(d,A,B)=(5,2,2)` and length `9`;
- `p=11`, killed by `n=7`, with `(d,A,B)=(6,2,5)` and length `15`;
- `p=17`, row `(4,8,13)`, which is an exact base;
- `p=19`, killed by `n=11`, with `(d,A,B)=(6,4,13)` and length `25`.

## 9. Exact residual bases

After all symbolic and explicit multiplier certificates, exactly three arithmetic rows remain:

`(p,c,r,t)=(7,4,1,5),(13,4,3,12),(17,4,8,13)`.

For each row, solve the relation after choosing `y`:

`x=-r^(-1)(4s+t y)`.

The exact `a=1` depth is

`rho_U(z)=min(S(z),1+sum_i [z_i-1]_p)`,

or equivalently `S(z)-2` off the saturated coordinate hyperplanes and `S(z)` on them.

Pair short-freeness forces, for every available power of `x` and `y`,

`rho_U(jv)>=j`, `rho_U(-jv)>=m-j`.

Exhausting every `y in F_p^3` produces zero choices satisfying even these separate radial inequalities in all three rows. The primary checker freezes the result as

- `p=7`: 0 survivors;
- `p=13`: 0 survivors;
- `p=17`: 0 survivors.

Thus no residual row is realizable.

## 10. Theorem

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with a support-four maximal atom of type `a=1` cannot have a support-three rank-two companion with
>
> `v_e3(V)=4`.

Together with the previous one-, two-, and three-share theorems, every hypothetical companion in this face now satisfies

`boxed{v_e3(V)>=5.}`

## 11. Independent hostile replay

`verify_a1_light_support3_four_share_independent_v1.cpp` does not use any of the explicit mod-three or mod-five multiplier formulas.

For every prime through `5000`, it exhausts every admissible multiplicity row and every scalar multiplier. Across **388365** rows, exactly the same three multiplier residuals remain. All three are independently confirmed to be three-support atom-compatible.

For each residual, the verifier constructs the full maximal-atom depth table by occurrence-level dynamic programming over the actual terms of `U`; it does not call the closed depth formula. It then evaluates the complete graded inequality

`|W|+rho_U(-sigma(W))>=m`

for every proper count-vector subsequence of `V`, over a deliberately broader parameter universe that imposes no projective-plane or new-support filters.

The parameter counts and score ranges are:

| row | parameters | largest `mu` | theorem threshold |
|---|---:|---:|---:|
| `(7,4,1,5)` | 341 | 8 | 10 |
| `(13,4,3,12)` | 2195 | 12 | 19 |
| `(17,4,8,13)` | 4911 | 20 | 25 |

Here

`mu=min_{nonempty proper W|V} (|W|+rho_U(-sigma(W)))`.

No parameter reaches the theorem threshold. As positive mutation controls, lowering the artificial threshold to the largest observed `mu` admits respectively **6**, **72**, and **6** parameters. This prevents an implementation that always rejects from passing the audit.

The branch workflow runs:

- the primary Python formula/base checker;
- the optimized C++ independent replay through prime `5000`;
- an AddressSanitizer/UndefinedBehaviorSanitizer replay of the complete exact bases plus the multiplier sweep through prime `401`.

## 12. Structural consequence

The four-share proof reveals a reusable pattern absent from the isolated `c=1,2,3` statements:

- the two extreme multiplicity boundaries are controlled by multipliers with denominator `c+1=5`;
- the two inner boundaries are controlled by denominator `c-1=3`;
- the interior is still killed by doubling.

This is evidence for a general endpoint/inner-boundary multiplier lemma, but no statement for arbitrary `c` is claimed here.

## Boundary

- Shared multiplicity `c>=5` remains open in the `a=1` support-three face.
- The `a=2` light-share lane has separately eliminated `c=1,2,3`; its higher layers remain open.
- Rank-three four-support companions remain open.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
