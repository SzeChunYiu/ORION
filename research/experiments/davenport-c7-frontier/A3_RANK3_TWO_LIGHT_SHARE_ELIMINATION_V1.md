# Type-three rank-three companions with two light shared copies — V1

Date: 2026-09-05. Baseline: `86f089ab`.
Status: **prime-uniform elimination of the complete `a=3,c=2` layer**.

## 1. Setup

Let `p=2H+1>=11` be prime, `m=p+H`, and

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`, `e1+e2=3(s-g)`.

Suppose `V=s^2 g^d x^r y^t` is a zero-sum of length `m`, with genuinely
new `x,y`, and `UV` contains no nonempty zero-sum shorter than `m`.
The overlap and shared-donor doubling reductions already proved at the
baseline give

`d in {1,2}`, `S=2+d`, `r=H-k`, `t=p-S+k`, `0<=k<S`.

Put `alpha=2k+1` and `f=S-k`. Then `2r=p-alpha`, `t=p-f`, and
`alpha+2f=2S+1`. The shared donor has capacities

`(e1,e2,s,g)=(p-1,p-1,5,p-3+d)`.

## 2. A flexible donor for either parity

For an integer `a>=2` with `B=p-aS>=3`, define

`E=max(ceil((p-2a-5)/3),ceil(ad/3))`,
`z=p-2a-3E`, `w=3E-ad`.

The first ceiling makes `z<=5`, and the second makes `w>=0`.
Both ceilings are at most `floor((p-2a)/3)`: this is immediate for
the first, and follows from `B>=3` for the second. Thus `z>=0` and
`E<p`. Also `w<=z+w=B<=p-2S<=p-3+d`. All donor counts fit.
Their old-support sum is `-a(2s+dg)` because

`3E+z=p-2a`, `w-3E=-ad`.

Whenever their least residues fit the new capacities, adjoining the
`-a` multiple of the new-value part therefore gives a zero-sum.

## 3. The balanced half: `alpha<=S`, equivalently `k=0,1`

Set `j=floor((p-S)/(2S))`. Except when `p=11,d=2`, one has `j>=1`.
Write

`p=(2j+1)S+v`, `0<=v<2S`.

Use the donor of Section 2 with `a=2j`; it applies since `B=S+v>=3`.
The new residues are `R=j alpha`, `T=2jf`, and they fit since

`(2j+1)alpha<=(2j+1)S<=p`, `(2j+1)f<=(2j+1)S<=p`.

The total length is `p+j+2E`. It remains to prove `2E<=H-j-1`.
Write the two ceilings defining `E` as

`E1=ceil((p-4j-5)/3)`, `E2=ceil(2jd/3)`.

Using `ceil(b/3)<=(b+2)/3` for integer `b`, a sufficient condition
for the first bound is

`p<=10j+3`.                                           (1)

For `d=1`, the decomposition is `p=6j+3+v`, `v<=5`.
Condition (1) follows for `j>=2`; at `j=1`, the only primes are
`11,13`, and both satisfy (1).

For `d=2`, it is `p=8j+4+v`, `v<=7`. Condition (1) follows for
`j>=4`. At `j=3`, the only primes are `29,31`; at `j=2`, the only
prime is `23`; all satisfy (1). At `j=1`, prime `13` satisfies it,
leaving `17,19`. Together with the missing `j=0` case, the only
rows deferred are therefore `d=2`, `p=11,17,19`, `k=0,1`.

For `E2`, a sufficient condition is

`3p-8jd-6j-17>=0`.                                    (2)

When `d=1,j>=2`, substitute `p>=6j+3` to bound its left side by
`4j-8>=0`. At `d=1,j=1`, `p>=11` verifies (2) directly.
When `d=2,j>=3`, use `p>=8j+4` to obtain `2j-5>=0`.
At `d=2,j=2`, the only prime is `23`; at `d=2,j=1`, the smallest
prime is `13`. Both satisfy (2). Thus both ceilings meet the score
bound in every nondeferred row, giving length at most `m-1`.

## 4. The complementary half: an odd selector for `p>=41`

If `alpha>S`, there are only three structural pairs:

`(S,alpha,f)=(3,5,1),(4,5,2),(4,7,1)`.

Choose `q` to be the least positive odd integer strictly greater than
`p/alpha`. Then

`q-2<p/alpha<q`, `q<p/alpha+2`.

The strict inequalities hold because `p>=41` is prime and `alpha` is
`5` or `7`. In particular `3<=q<p`. We show `B=p-qS>=3`.
For `(S,alpha)=(3,5),(4,7)`, the bound

`B>p(1-S/alpha)-2S`

already exceeds `3` at `p=41`. For `(4,5)` it is positive, so the
odd integer `B` is at least one. If `B=1`, then `p=4q+1`, while
`p>5(q-2)` gives `q<11`. As `q` is odd, this would imply `p<=37`,
a contradiction. Thus the donor of Section 2 with `a=q` always applies.

The new least residues are

`R=(q alpha-p)/2`, `T=qf`.

Here `0<R<alpha<=r`, since `alpha<=7`, `k<=3`, and `H>=20`.
Also `f<=2` and `q<p/5+2` give

`(q+1)f<2p/5+6<=p`,

so `T<=t`. No unrecorded modular wrap occurs in these counts.
The total length simplifies to

`(p+q)/2+2E`.

The donor bound `E<=floor((p-2q)/3)` makes this at most

`7p/6-5q/6 < (3p-1)/2=m`.

This completes every complementary-half row for `p>=41`.

## 5. Explicit small-prime remainder

The following table has only occurrence certificates, not candidate support
vectors. The first six rows are the balanced exceptions. The remaining
rows cover exactly `alpha>S` at the eight primes `11<=p<41`. Most use
the same least-odd selector of Section 4; five exceptional scalar choices
are recorded explicitly. Their existence was obtained by modular arithmetic,
not a search over companions.

In each row, `c=2`, `r=H-k`, `t=p-2-d+k`; the occurrence vector is
`(E,E,z,w,R,T)`. Its columns satisfy

`3E+z==2n`, `w-3E==dn`, `R==rn`, `T==tn` modulo `p`.

They are nonnegative, bounded by `(p-1,p-1,5,p-3+d,r,t)`, and their
sum is strictly below `m`. These equalities prove that the corresponding
occurrences sum to zero independently of the coordinates of `x,y`.

| p | d | k | n | E | z | w | R | T | Length |
|---|---|---|---|---|---|---|---|---|---|
| 11 | 2 | 0 | 7 | 0 | 3 | 3 | 2 | 5 | 13 |
| 11 | 2 | 1 | 3 | 2 | 0 | 1 | 1 | 2 | 8 |
| 17 | 2 | 0 | 15 | 3 | 4 | 5 | 1 | 8 | 24 |
| 17 | 2 | 1 | 15 | 3 | 4 | 5 | 3 | 6 | 24 |
| 19 | 2 | 0 | 11 | 0 | 3 | 3 | 4 | 13 | 23 |
| 19 | 2 | 1 | 5 | 3 | 1 | 0 | 2 | 4 | 13 |
| 11 | 1 | 2 | 8 | 1 | 2 | 0 | 2 | 3 | 9 |
| 11 | 2 | 2 | 4 | 1 | 5 | 0 | 1 | 3 | 11 |
| 11 | 2 | 3 | 6 | 0 | 1 | 1 | 1 | 5 | 8 |
| 13 | 1 | 2 | 10 | 1 | 4 | 0 | 1 | 3 | 10 |
| 13 | 2 | 2 | 10 | 2 | 1 | 0 | 1 | 6 | 12 |
| 13 | 2 | 3 | 9 | 0 | 5 | 5 | 1 | 4 | 15 |
| 17 | 1 | 2 | 12 | 2 | 1 | 1 | 4 | 5 | 15 |
| 17 | 2 | 2 | 6 | 3 | 3 | 4 | 2 | 5 | 20 |
| 17 | 2 | 3 | 14 | 2 | 5 | 0 | 2 | 3 | 14 |
| 19 | 1 | 2 | 14 | 2 | 3 | 1 | 3 | 5 | 16 |
| 19 | 2 | 2 | 6 | 3 | 3 | 2 | 4 | 7 | 22 |
| 19 | 2 | 3 | 16 | 3 | 4 | 3 | 1 | 3 | 17 |
| 23 | 1 | 2 | 18 | 3 | 4 | 4 | 1 | 5 | 20 |
| 23 | 2 | 2 | 18 | 4 | 1 | 2 | 1 | 10 | 22 |
| 23 | 2 | 3 | 18 | 4 | 1 | 2 | 6 | 5 | 22 |
| 29 | 1 | 2 | 22 | 4 | 3 | 5 | 3 | 7 | 26 |
| 29 | 2 | 2 | 22 | 5 | 0 | 1 | 3 | 14 | 28 |
| 29 | 2 | 3 | 24 | 5 | 4 | 5 | 3 | 5 | 27 |
| 31 | 1 | 2 | 24 | 4 | 5 | 5 | 2 | 7 | 27 |
| 31 | 2 | 2 | 24 | 5 | 2 | 1 | 2 | 14 | 29 |
| 31 | 2 | 3 | 26 | 6 | 3 | 8 | 2 | 5 | 30 |
| 37 | 1 | 2 | 28 | 5 | 4 | 6 | 4 | 9 | 33 |
| 37 | 2 | 2 | 28 | 6 | 1 | 0 | 4 | 18 | 35 |
| 37 | 2 | 3 | 30 | 6 | 5 | 4 | 6 | 7 | 34 |

## 6. Review and scope

The separately tasked selector specialist and proof auditor each read the
complete proof, re-derived its inequalities, and directly replayed all 30
displayed vectors. Both checked that the table is exactly the declared
remainder. Their internal mathematical reviews passed. This is not external
referee certification; the prime-uniform conclusion rests on the proof.

This proof replaces the overly rigid light-count residue choice in the
original negative-even `J` interface by an interval of possible shared
donors, and uses an odd scalar when the even capacity interval is insufficient.
The failed floor extensions at `j=0` and the exact small-prime score
exceptions have been retained explicitly rather than hidden in a prime scan.

The theorem closes only the two-light-share layer of exceptional type three.
Together with the separate one-light-share and `c>=3` proofs it completes
that exceptional rank-three face. The full first-corridor support-seven
theorem, exceptional type-two closure, and every `D_3(C_7^3)` assertion remain
outside this result.
