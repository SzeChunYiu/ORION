# Type-three rank-three boundary with light overlap at least three — V1

Status: **proved prime-uniform branch elimination**. Every hypothetical
first-corridor, exact-support-six, rank-three companion of canonical maximal
type `a=3` with light overlap `c>=3` is impossible. The proof selects shared
donors using negative even and negative odd scalars, with a wrapped scalar on
the thin upper boundary. It does not claim the full first-corridor theorem or
any value of `D_3(C_7^3)`.

## 1. Setup and the precise scope

Let `p=2H+1>=11` be prime, `m=p+H`, and

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`,

where `e1+e2=3(s-g)`. Suppose

`V=s^c g^d x^r y^t`

has length `m`, where the four displayed multiplicities are positive and
`x,y` are the two genuinely new values. Suppose `UV` contains no nonempty
zero-sum of length below `m`.

The overlap bounds and shared-donor doubling theorem in
`A3_RANK3_SHARED_DONOR_NEGATIVE_EVEN_V1.md` give

`3<=c<=floor(H/2)`, `1<=d<=2`,

and, after ordering `r<=t`,

`S=c+d`, `r=H-k`, `t=p-S+k`, `0<=k<S`.

Write

`alpha=2k+1`, `f=S-k`.

Then

`2r=p-alpha`, `t=p-f`, `alpha+2f=2S+1`.

The proof below concerns these necessary multiplicity conditions alone. No
search over support vectors, prime values, or multiplier lists is used as
theorem authority.

## 2. A flexible shared-donor lemma

Let `a>=2` be an integer with `aS<=p-3`. Put

`B=p-aS`, `D=p-ac=B+ad`,

`E=max(ceil((D-c-3)/3), ceil(ad/3))`,

`z=D-3E`, `w=B-z=3E-ad`.

These define actual old-support occurrences: `E` copies of each saturated
value, `z` copies of `s`, and `w` copies of `g`.

Indeed `B>=3` implies

`ceil(ad/3)<=floor(D/3)`.

Also `c+3>=6` implies

`ceil((D-c-3)/3)<=floor(D/3)`.

Thus `E<=floor(D/3)<p` and `z>=0`. The two lower bounds defining `E` give
`z<=c+3` and `w>=0`. Finally

`w<=B<=p-2S<=p-3+d`.

The old-support sum is exactly the desired scalar multiple because

`3E+z=p-ac`, `w-3E=-ad`.

Hence

`E(e1+e2)+zs+wg=-a(cs+dg)`

in the group, and the old-support length is `B+2E`.

For `a=2j`, whenever the actual new counts are

`R=j alpha`, `T=2jf`,

the total zero-sum length is

`B+2E+R+T=p+j+2E`.                                      (1)

For odd `a=q`, whenever the actual new counts are

`R=(q alpha-p)/2`, `T=qf`,

the total length is

`B+2E+R+T=(p+q)/2+2E`.                                (2)

Every application below verifies the capacities of these new counts.

## 3. The right half: `alpha<=S`

First assume

`j=floor((p-S)/(2S))>=1`.

Use the even scalar `-2j`. Write

`p=(2j+1)S+v`, `0<=v<2S`.

Then `B=p-2jS=S+v>=S>=4`, so the donor lemma applies.
The new capacities follow from

`j alpha<=alpha(p-S)/(2S)<=(p-alpha)/2=r`,

where the second inequality is exactly `alpha<=S`, and

`2jf<=f(p-S)/S<=p-f=t`,

where the last inequality follows from `f<=S`.

We prove `2E<=H-j-1`, making (1) at most `m-1`.

The first ceiling in `E` is

`E1=ceil(((2j+1)d+v-3)/3)`.

Since `ceil(u/3)<=(u+2)/3` for integral `u`, it suffices that

`(2j+1)(3c-d-3)>=v+2`.

This holds because `j>=1`, `v<=2S-1`, and

`3(3c-d-3)-(2c+2d+1)=7c-5d-10>=1`

for `c>=3`, `d<=2`.

For the second ceiling `E2=ceil(2jd/3)`, it suffices that

`(6j+3)c+(-2j+3)d-6j-17>=0`.

At `j=1` the left side is `9c+d-23>=5`; increasing `j`
increases it by `6c-2d-6>=8`. Thus this bound also holds.

Consequently the entire right half is eliminated whenever `j>=1`.

There are only two possible triples with `j=0`: `(p,c,d)=(13,3,2)`
and `(17,4,2)`. To see this, `p>=4c+1` implies `p>=3(c+d)` for
`c>=5`; for `c=3,4` the same is true if `d=1`, leaving exactly
the two displayed prime values when `d=2`. Their right-half rows are
covered by the explicit table in Section 6.

## 4. The left half with `r>=alpha`

Suppose `alpha>S` and `r>=alpha`. Put

`j=floor(r/alpha)>=1`, `q=2j+3`,

and write `r=j alpha+u`, `0<=u<alpha`. Thus

`p=(2j+1)alpha+2u=(q-2)alpha+2u`.

### 4.1 If `p-qS>=3`, use the odd scalar `-q`

The donor lemma applies. Its new counts are

`R=(q alpha-p)/2=alpha-u`, `T=qf`.

Thus `1<=R<=alpha<=r`. Also `alpha>S` implies
`f<alpha/2`. Since `q>=5`,

`(q+1)f<=(q+1)(alpha-1)/2<=(q-2)alpha<=p`.

Hence `T<=p-f=t`.

The donor lemma gives `E<=D/3=(p-qc)/3`. Therefore (2) is at most

`7p/6+q(1/2-2c/3)`.

For `c>=3` this is strictly below `(3p-1)/2=m`. Thus this branch
contains a forbidden short zero-sum.

### 4.2 If `p-qS<=2`, use the even scalar `-2j`

Now `B=p-2jS>S>=4`, so the donor lemma again applies. The new
counts `R=j alpha` and `T=2jf` fit: `R<=r`, while
`2f<alpha` gives `T<R<=r<=t`.

For the first ceiling

`E1=ceil((p-(2j+1)c-3)/3)`,

the sufficient score inequality `2E1<=H-j-1` is

`p<=(8c-6)j+4c-5`.                                    (3)

Our branch gives `p<=qS+2`. The difference between the right
side of (3) and `qS+2` is

`(6c-2d-6)j+c-3d-7`.

This is nonnegative for `c>=3`, `d<=2`, `j>=1`, except
`c=3,d=2,j=1`, when it equals `-2`. In that exception
`p<=qS+2=27`; primality gives `p<=23<25`, which is the right
side of (3). Thus (3) holds in every case.

The second ceiling is `E2=ceil(2jd/3)`. Since
`p>(2j+1)S`, exactly the second-ceiling bound from Section 3
again gives `2E2<=H-j-1`.

Consequently (1) is at most `m-1`. This eliminates the other
branch, and therefore all left-half rows with `r>=alpha`.

## 5. The upper band: `r<alpha`

Assume first `p>=19`. Equivalently `3k+1>H`, so `k>=H/3`.
Since `S<=floor(H/2)+2`,

`f=S-k<=H/6+2`,

and hence `4f<=p` for `H>=9`. Also `3S<p`: for `H>=11`
this follows from `3S<=3H/2+6<2H+1`, while for `H=9`
it follows from `S<=6`; `H=10` gives the nonprime value `p=21`.

### 5.1 If `4r>=p`, use the scalar `-3`

Define

`E=max(ceil((p-4c-3)/3),d)`,

`z=p-3c-3E`, `w=3E-3d`,

`R=p-3r`, `T=3f`.

Here `r<alpha` means `3r<p`, so `R>=1`; `4r>=p`
gives `R<=r`, and `4f<=p` gives `T<=t`.

Because `3S<p`, the number `D=p-3c` is greater than `3d`.
Thus both lower bounds defining `E` are at most `floor(D/3)`.
It follows that `z>=0`; the first lower bound gives `z<=c+3`,
and the second gives `w>=0`. Finally

`w<=p-3S<=p-3+d`.

The old-support identities are `3E+z=p-3c` and `w-3E=-3d`.
The total zero-sum length is

`2p-3H+2E=H+2+2E`.

Both `ceil((p-4c-3)/3)` and `d` are at most `H-1`, so this
length is at most `3H=m-1`.

### 5.2 If `4r<p`, use the wrapped scalar `-4`

The overlap bounds leave only the following families. Write `H=2h`
or `H=2h+1` as indicated. In every row take `E=0`,
`w=p-4d`, `T=4f`, and the displayed `z,R`.

| `H` | `c` | `d` | `k` | `z` | `R` |
|---|---:|---:|---:|---:|---:|
| `2h` | `h-1` | 2 | `h` | 5 | 1 |
| `2h` | `h` | 1 | `h` | 1 | 1 |
| `2h` | `h` | 2 | `h` | 1 | 1 |
| `2h` | `h` | 2 | `h+1` | 1 | 5 |
| `2h+1` | `h` | 2 | `h+1` | 3 | 3 |

This list is exhaustive: `4r<p` forces `k>=h` when `H=2h`
and `k>=h+1` when `H=2h+1`; combine this with
`k<=c+d-1`, `c<=h`, and `d<=2`.

For primes `p>=19`, the even-`H` case has `p=4h+1>=29`,
so `h>=7`; the odd-`H` case has `h>=4`. These bounds verify
`z<=c+3`, `R<=r`, `T<=t`, and `0<=w<=p-3+d` in every row.
The old coefficients are `z=[-4c]_p`, `w=[-4d]_p`, while
the new coefficients are `R=[-4r]_p`, `T=[-4t]_p`.

Their total length is

`3p-4H=p+2<m`.

Thus the entire upper band is eliminated for `p>=19`.

## 6. Explicit small-prime occurrences

For `p=11` there is no `c>=3` under the overlap ceiling.
The following table covers both `j=0` exceptions from Section 3
and every `r<alpha` row for `p=13,17`. The scalar is `n`
modulo `p`; the occurrence vector is `(E,E,z,w,R,T)`.

| `p` | `c` | `d` | `k` | `n` | `E` | `z` | `w` | `R` | `T` | Length |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 13 | 3 | 2 | 0 | 5 | 0 | 2 | 10 | 4 | 1 | 17 |
| 13 | 3 | 2 | 1 | 6 | 1 | 2 | 2 | 4 | 2 | 12 |
| 13 | 3 | 2 | 2 | 4 | 3 | 3 | 4 | 3 | 1 | 17 |
| 13 | 3 | 1 | 2 | 10 | 1 | 1 | 0 | 1 | 6 | 10 |
| 13 | 3 | 1 | 3 | 9 | 0 | 1 | 9 | 1 | 4 | 15 |
| 13 | 3 | 2 | 3 | 9 | 0 | 1 | 5 | 1 | 8 | 15 |
| 13 | 3 | 2 | 4 | 7 | 1 | 5 | 4 | 1 | 6 | 18 |
| 17 | 4 | 2 | 0 | 5 | 0 | 3 | 10 | 6 | 4 | 23 |
| 17 | 4 | 2 | 1 | 3 | 4 | 0 | 1 | 4 | 2 | 15 |
| 17 | 4 | 2 | 2 | 3 | 4 | 0 | 1 | 1 | 5 | 15 |
| 17 | 3 | 1 | 3 | 14 | 1 | 5 | 0 | 2 | 3 | 12 |
| 17 | 3 | 2 | 3 | 14 | 2 | 2 | 0 | 2 | 6 | 14 |
| 17 | 3 | 2 | 4 | 13 | 0 | 5 | 9 | 1 | 4 | 19 |
| 17 | 4 | 1 | 3 | 14 | 1 | 2 | 0 | 2 | 6 | 12 |
| 17 | 4 | 1 | 4 | 13 | 0 | 1 | 13 | 1 | 4 | 19 |
| 17 | 4 | 2 | 3 | 4 | 4 | 4 | 3 | 3 | 5 | 23 |
| 17 | 4 | 2 | 4 | 13 | 0 | 1 | 9 | 1 | 8 | 19 |
| 17 | 4 | 2 | 5 | 6 | 2 | 1 | 1 | 1 | 11 | 18 |

Every row is an explicit certificate, checked by the four congruences

`3E+z == nc`, `w-3E == nd`, `R == nr`, `T == nt (mod p)`.

All counts fit the available occurrences, and the lengths are below
`m=19` or `m=25`, respectively. The table is a finite closure of
the explicit small exceptions to uniform inequalities, not a prime-search
inference.

## 7. Theorem and preserved failed route

The cases `alpha<=S`, `alpha>S` with `r>=alpha`, and `r<alpha`
cover every boundary row. Therefore no type-three rank-three boundary
with `c>=3` survives. Together with shared-donor doubling, this proves
that any remaining rank-three companion of maximal type `a=3` must
have `c<=2`.

The original negative-even `J` certificate in
`A3_RANK3_SHARED_DONOR_NEGATIVE_EVEN_V1.md` remains valid, but a
universal selector using its conditions alone cannot work: condition
`(J+1)k+J/2<=H` with even `J>=2` requires `3k+1<=H`.
The allowed boundary includes rows outside that band. The present proof
repairs the route by allowing a capacity-optimal donor residue, an odd
scalar in the low band, and wrapped new-value residues in the upper band.

The theorem is supported by the displayed algebra and explicit occurrences.
Any finite replay is regression only. The exceptional `c=1,2` rank-three
rows are outside this file's theorem; their disposition must be established
separately. No full first-corridor, `D_3(C_7^3)`, all-prime Davenport formula,
novelty, or priority claim is made.
