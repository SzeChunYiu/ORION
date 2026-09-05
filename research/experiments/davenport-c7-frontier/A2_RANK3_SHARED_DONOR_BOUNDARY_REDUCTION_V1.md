# Type `a=2` rank-three shared-donor reduction and a balanced boundary band — V1

Status: **proved prime-uniform interior elimination and balanced-band elimination**. Every surviving exceptional rank-three type-two companion is forced into a one-parameter boundary strip. A negative-even certificate then removes the balanced half of every strip with `7<=c` and `c+1<=p/3`.

This note does not close the full exceptional `a=2` boundary, the first-corridor support-seven theorem, or any generalized Davenport value.

## 1. Setup

Let `p=2H+1>=7` be prime and `m=p+H=3H+1`. Use the canonical type-two maximal atom

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where `e1+e2=2(s-g)`.

Consider a hypothetical zero-sum companion

`V=s^c g^d x^r y^t`,

with positive multiplicities and `|V|=m`, and suppose `UV` has no nonempty zero-sum of length less than `m`. The exact light-overlap ceiling proved in `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md` gives

`1<=c<=2 floor(H/2)<=H`.

Since `U` already contains `p-2` copies of `g`, the short-freeness of `UV` forces `d<=1`, hence `d=1`. Similarly `r,t<=p-1`. Thus the companion relation is

`c s+g+r x+t y=0`, `c+1+r+t=m`.                       (1)

The actual old-support donor, including the shared occurrences, is

`B=U s^c g=e1^(p-1)e2^(p-1)s^(c+2)g^(p-1)`.

The following arguments use only (1) and the actual multiplicities. They require no additional rank or geometric assumption about `x,y`.

## 2. Shared-donor doubling removes every interior row

Suppose `r,t>H`. Put

`E=floor((c-1)/2)`, `z=2c-2E`, `w=2+2E`.

Then

`E(e1+e2)+z s+w g=2c s+2g`.

The counts are available in `B`:

- if `c` is odd, then `z=c+1` and `w=c+1`;
- if `c` is even, then `z=c+2` and `w=c`;
- `E>=0` and `E<=p-1`;
- `z<=c+2` and `w<=H+1<=p-1`.

Doubling (1) supplies new-value counts

`R=2r-p`, `T=2t-p`,

which are positive and satisfy `R<=r`, `T<=t`. Therefore

`e1^E e2^E s^z g^w x^R y^T`

is an actual zero-sum subsequence of `UV`. Its length is

`R+T+2E+z+w=p-1+2E`.

Because `2E<=c-1<=H-1`, this is at most

`p+H-2=m-2`.

This contradicts short-freeness.

> **Interior-elimination theorem.** Every surviving type-two row has at least one new multiplicity at most `H`.

Order `r<=t` and write

`r=H-k`, `t=p-c-1+k`.

Then `r<=H` gives `k>=0`, while `t<=p-1` gives `k<=c`. The complete surviving strip is therefore

`boxed{r=H-k, t=p-c-1+k, 0<=k<=min(c,H-1).}`            (2)

The extra `H-1` endpoint records the already assumed positivity of `r`. Every ordered positive row satisfying these formulas also has `r<=t`, since `t-r=H-c+2k>=0`.

## 3. An exact negative-even selector on the balanced half

Assume a boundary row from (2) satisfies

`7<=c`, `c+1<=p/3`, `2k<=c`.                         (3)

Put

`S=c+1`, `alpha=2k+1`,

`j=floor((p-S)/(2S))`.

Then `j>=1` and there is a unique integer `v` with

`p=(2j+1)S+v`, `0<=v<2S`.

Let `epsilon` be the parity of `v`, so `epsilon in {0,1}`, and set

`E=j+(v-epsilon)/2`,

`z=c+1+epsilon`, `w=v-epsilon`.                       (4)

These formulas are integral and require no search. Since `p` is odd, `v` and `c` have the same parity, although the score estimate below does not need that extra refinement.

Use the scalar `n=-2j` modulo `p`. The proposed new-value counts are

`R=j alpha`, `T=2j(S-k)`.                            (5)

To check they are the actual least residues, observe that

`-2j r==-2j(H-k)==j(2k+1)=R (mod p)`,

`-2j t==-2j(p-S+k)==2j(S-k)=T (mod p)`.

Both are positive. Because `alpha<=S` and `(2j+1)S<=p`,

`(2j+1)alpha<=p`,

which is equivalent to `R<=r=(p-alpha)/2`. Similarly, `S-k<=S` gives

`(2j+1)(S-k)<=p`,

equivalently `T<=p-S+k=t`. Thus (5) supplies valid new-value occurrences, each below `p`.

The old-support coefficients from (4) satisfy

`2E+z=p-2jc`, `w-2E=-2j`.

Consequently

`E(e1+e2)+z s+w g=-2jc s-2j g` in the group,

and this cancels the sum of (5) by the `-2j` multiple of (1).

Every donor count is available:

- `E>=j>=1`; also `2E=2j+v-epsilon<p`, since `p-2E=(2j+1)c+1+epsilon>0`;
- `0<=z=c+1+epsilon<=c+2`;
- `0<=w=v-epsilon<p`, since `p-w=(2j+1)S+epsilon>0`.

Thus

`e1^E e2^E s^z g^w x^R y^T`                         (6)

is an occurrence-valid, nonempty zero-sum subsequence of `UV`.

Its length simplifies exactly to

`boxed{p+3j+v-epsilon.}`                              (7)

In particular, the boundary coordinate `k` cancels from the score.

## 4. The score is always short under the stated hypotheses

We show

`3j+v-epsilon<=H-1`,

so (7) is at most `m-1`. Using `2H=p-1` and `p=(2j+1)(c+1)+v`, the desired inequality is equivalent to

`6j+v-2epsilon<=(2j+1)(c+1)-3`.                      (8)

Because `v<2c+2`, one has `v<=2c+1`. Hence the left side of (8) is at most `6j+2c+1`. The remaining sufficient inequality is

`(2j-1)c>=4j+3`.

For every `c>=7` and `j>=1`,

`(2j-1)c-(4j+3)>=7(2j-1)-4j-3=10(j-1)>=0`.

This proves (8) and the short score.

> **Balanced-band theorem.** No type-two first-corridor companion can survive when
>
> `boxed{7<=c, c+1<=p/3, 0<=2k<=c}`
>
> in the boundary parameterization (2).

The theorem follows from one exact quotient/remainder selector and a parity-adjusted occurrence vector. It uses no prime enumeration and no classification of the new values.

## 5. Scope and relation to the remaining frontier

The doubling theorem covers every allowed positive overlap `c`, independent of the balanced-band assumptions. It reduces the full rank-three type-two multiplicity problem to (2).

The second theorem removes only the stated balanced moderate-overlap band. It does not remove the high-`k` half, overlaps below seven, or overlaps with `c+1>p/3`. The separately proved extreme-row packet `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md` treats coordinate rigidity on a different part of the surviving strip and preserves its exact scalar-route obstruction.

All theorem authority here is the symbolic occurrence-level argument. No full exceptional-type closure, first-corridor theorem, or `D_3(C_7^3)` value is claimed.
