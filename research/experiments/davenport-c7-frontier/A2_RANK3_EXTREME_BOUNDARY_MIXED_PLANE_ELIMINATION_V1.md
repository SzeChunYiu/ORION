# Type `a=2` extreme rank-three boundary: a mixed plane-family elimination — V1

Status: **proved prime-uniform conditional elimination, further rigidity restrictions, and an exact scalar-route barrier**. The extreme multiplicity row `c=H-1,d=1,r=1,t=p-1` cannot survive if its high-multiplicity new value has first-coordinate sum zero, has any zero coordinate, or has total coordinate sum one. The proof removes an exceptional centered residue with a genuinely mixed `xy` certificate. The last extension invokes a precisely stated established Bernoulli-pairing theorem. This note does not classify the high-multiplicity value of every surviving companion.

This note does not close the full exceptional `a=2` face, the first-corridor support-seven theorem, or any generalized Davenport value.

## 1. Setup and statement

Let `p=2H+1>=11` be prime, `m=3H+1`, and `u=2^(-1)=H+1` in `F_p`. In the basis `(e1,e2,g)`, put

`s=(u,u,1)`,

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

Consider the zero-sum companion

`V=s^(H-1) g x y^(p-1)`,

where `x,y` are distinct new values and the displayed support has rank three. Its relation is

`x=y-(H-1)s-g`.                                      (1)

The overlap `H-1` is within the exact light-overlap ceiling for both residue classes of odd primes. The actual combined old-support donor is

`B=U s^(H-1)g=e1^(p-1)e2^(p-1)g^(p-1)s^(H+1)`.

> **Theorem.** If `y=(A,-A,kappa)` in these coordinates, then `UV` contains a nonempty zero-sum of length less than `m`.

The theorem is uniform in `A` and `kappa`, subject only to the displayed hypotheses. It is conditional on the first-coordinate sum of `y` being zero.

## 2. Only third coordinates one and two need treatment

Suppose for contradiction that `UV` is `(m-1)`-short-zero-free. Apply Corollary 2 of `A2_SHARED_DONOR_PLANE_RIGIDITY_V1.md` to the subdonor

`B'=U s^(H-1)`

and the occurrence `y`. With `c=H-1`, that corollary gives

`1<=kappa<=2`.                                       (2)

Using `B'` here leaves the additional shared `g` occurrence unused, so this application cannot double-count an occurrence.

Also `A!=0`. Indeed, if `A=0`, both `y` and, by (1), `x` lie in the plane spanned by `s,g`; the displayed support would then have rank at most two.

## 3. A parity identity for the saturated pair

For a nonzero `P` let

`d=min([P]_p,[-P]_p)`, `1<=d<=H`,

and define

`S_k(P)=[P-ku]_p+[-P-ku]_p`.

Elementary residue arithmetic gives

`S_k(P)=p-k` if either

- `k` is even and `k<=2d`, or
- `k` is odd and `k<=2(H-d)+1`;

otherwise `S_k(P)=2p-k`.

This is the pair-cost identity established in Section 2 of `A2_SHARED_DONOR_PLANE_RIGIDITY_V1.md`. For the adjacent pair `k=H,H+1`, at least one is in its low case. This also follows directly: when `H=2q`, failure at the even count `H` requires `d<=q-1`, while failure at the odd count `H+1` requires `d>=q+1`; when `H=2q+1`, the respective failures require `d>=q+2` and `d<=q`. Simultaneous failure is impossible.

## 4. Third coordinate two is excluded by two copies of `y`

Suppose `y=(A,-A,2)`. The target `-2y` has third coordinate

`C=p-4`.

Select `k` from `{H,H+1}` so that `S_k(-2A)=p-k`, as Section 3 allows. Since `H>=5`,

`C=2H-3>=H+1>=k`.

Represent `-2y` with `k` copies of `s`, `C-k` copies of `g`, and the forced saturated counts

`[-2A-ku]_p`, `[2A-ku]_p`.

Every count is available in `B`: `k<=H+1`, `0<=C-k<=p-1`, and each saturated count lies in `[0,p-1]`. Adjoining the two available copies of `y` gives a nonempty zero-sum of length

`2+C+S_k(-2A)=2p-k-2<=2p-H-2=3H=m-1`.

Thus `kappa=2` is impossible.

## 5. Third coordinate one: singleton certificates and one precise gap

Now let `y=(A,-A,1)` and put

`alpha=min([A]_p,[-A]_p)`, `1<=alpha<=H`.

By (1), the target `-x` is

`((H-1)u-A,(H-1)u+A,H-1)`.

For an integer `0<=L<=H-1`, set

`k=H-1-L`.

Use `k` copies of `s`, `L` copies of `g`, and saturated counts

`a=[Lu-A]_p`, `b=[Lu+A]_p`.                            (3)

These occurrences sum to `-x`, and every count lies within `B`. The only issue is choosing `L` such that `a+b=L`, rather than the higher residue-sum level `L+p`.

- If `L=2v`, then `Lu=v` modulo `p`; the equality `a+b=L` holds exactly when `alpha<=v`.
- If `L=2v+1`, then `Lu=H+1+v` modulo `p`; the equality holds exactly when `alpha>=H-v`.

Both assertions follow by checking whether the two least residues in (3) straddle zero or `p`; exchanging `A` and `-A` merely interchanges `a,b`.

Choose the largest admissible even `L` or the largest admissible odd `L`:

| Parity of `H` | Even choice and covered `alpha` | Odd choice and covered `alpha` | Sole uncovered value |
|---|---|---|---|
| `H=2q` | `L=2q-2`, `alpha<=q-1` | `L=2q-1`, `alpha>=q+1` | `alpha=q` |
| `H=2q+1` | `L=2q`, `alpha<=q` | `L=2q-1`, `alpha>=q+2` | `alpha=q+1` |

For every covered value, adjoining `x` to these donor occurrences yields a zero-sum of length

`1+k+L+(a+b)=H+L<=2H-1<m`.

Consequently the only case requiring another argument is

`alpha=ceil(H/2)`.                                   (4)

No interval endpoint is being discarded: the table lists the complete one-value gap for this certificate construction.

## 6. The exceptional residue is removed by a mixed `xy` certificate

Under (4), one has

`2A==H or -H (mod p)`.

Indeed this is immediate for even `H`; for odd `H`, twice the centered magnitude is `H+1`, which is congruent to `-H` modulo `p`.

The target `-(x+y)` has third coordinate `H-2`. Use `H-2` copies of `s` and no copies of `g`. The remaining saturated coordinates are

`u-2A`, `u+2A` modulo `p`.

Because `u=H+1` and `2A==+/-H`, their least residues are exactly `0` and `1`. Therefore, for one of the two saturated basis vectors,

`boxed{x y s^(H-2) e_i}`

is a zero-sum subsequence of `UV`, of length

`2+(H-2)+1=H+1<m`.

All occurrences are present: `x` once, `y` once, at most `H+1` copies of `s`, and one saturated basis occurrence. This resolves the exact gap left by Section 5 and proves the theorem.

## 7. An exact obstruction to relation-multiplier-only proofs

The extreme multiplicity row is intrinsically degenerate for overlap-plane relation multiples. Its admissible multiplier set is

`Q={n in F_p : [n]_p<=1 and [-n]_p<=p-1}={0,1}`.

Thus scalar multiplication of the companion relation produces no nontrivial new-value subsequence beyond the full new-value part `x y^(p-1)`.

There is a stronger geometric statement. In the quotient by the old overlap plane `<s,g>`, equation (1) gives `x_bar=y_bar!=0`. A new-value subsequence `x^i y^j`, with `0<=i<=1` and `0<=j<=p-1`, enters that plane precisely when `i+j==0 (mod p)`. The only possibilities are `(i,j)=(0,0)` and `(1,p-1)`.

This does not say the pair is compatible: Sections 5–6 construct certificates whose saturated donor counts are unequal, so their new-value sums need not lie in `<s,g>`. It says that restricting the donor to equal `e1,e2` counts loses the mixed mechanism.

For completeness, neither of the two surviving plane cases creates a short zero-sum merely by optimizing the enlarged donor:

- A zero-sum wholly in `B` has length at least `2p-(H+1)=m`. To see this, all coordinate counts are below `p` and the circuit relation gives, for an `s`-count `z`, length `2p-z` or `3p-z`; since `z<=H+1`, both bounds follow.
- The full new-value part has length `p` and needs donor sum `(H-1)s+g`, whose third coordinate is `H`. A donor representation has `s_count+g_count` congruent to `H` and nonnegative; hence its total length is at least `H`. The literal representation has exactly `H` terms. Thus the best length in this case is exactly `p+H=m`.

These are prime-uniform route obstructions, not computational failures and not counterexamples to the desired theorem.

## 8. Every coordinate of the high-multiplicity value is nonzero

The shared donor contains `p-1` copies of each of `e1,e2,g`. Write `y=(A,B,C)` and suppose exactly `q` of these three coordinates are nonzero, with `1<=q<=2`. The case `q=0` already supplies the one-term zero-sum `y`.

For each `1<=j<=p-1`, take `j` copies of `y` and `[-j y_i]_p` copies of every corresponding saturated basis value. This is an available zero-sum, of length

`L_j=j+sum_i [-j y_i]_p`.

Its complementary index satisfies

`L_j+L_(p-j)=(q+1)p`.                                (5)

Put `T=1-A-B-C` in `F_p`. If `T!=0`, the congruence `L_j==jT (mod p)` gives `p-1` distinct residues and therefore `p-1` distinct integers. Thus

`max L_j-min L_j>=p-2`.

Together with (5), this implies

`min L_j<=q*p/2+1<=p+1<m`.

If `T=0`, all the positive `L_j` are multiples of `p`, and (5) gives `min L_j<=(q+1)p/2`; integrality in multiples of `p` then gives `min L_j<=p<m`.

Either case is a contradiction. Hence:

> **Nonvanishing-coordinate restriction.** Every surviving extreme-row value `y=(A,B,C)` must satisfy `ABC!=0`.

The additional shared `g` occurrence matters here: it makes the `g` capacity `p-1`, so all displayed least-residue counts are available.

## 9. Half-interval rigidity removes the permuted standard families

Suppose next that

`y=(1,B,-B)`, `B!=0`.

If there were no `ell` with

`1<=ell<=H`, `1<=[ell B]_p<=H`,

the two sets of size `H` would satisfy

`B*{1,...,H}={H+1,...,2H}=-{1,...,H}`.

Summing their residues gives

`(B+1)*H(H+1)/2==0 (mod p)`.

The factor `H(H+1)/2` is nonzero in `F_p`, so this forces `B=-1`.

For `B!=-1`, select such an `ell` and write `v=[ell B]_p`. Then

`boxed{s y^ell e1^(H-ell) e2^(H-v) g^(v-1)}`            (6)

is an available zero-sum. Its first two coordinates are both `u+H=0` modulo `p`; its third coordinate is `1-v+(v-1)=0`. Its length is

`1+ell+(H-ell)+(H-v)+(v-1)=2H=p-1<m`.

Every count is nonnegative and at most the actual capacity in `UV`.

The only half-interval obstruction, `B=-1`, gives `y=(1,-1,1)`, already eliminated by Sections 2–6. Exchanging `e1` and `e2` proves the same result for `y=(B,1,-B)`.

> **Permuted-family restriction.** No extreme-row companion can have `y=(1,B,-B)` or `y=(B,1,-B)`.

This is an exact interval-invariance argument. It does not assume that a general high-multiplicity value has one of these standard forms.

## 10. An established pairing theorem closes the whole affine sum-one slice

This section uses an external structural theorem, separately from the elementary arguments above. Define the periodic Bernoulli function

`B1(z)={z}-1/2` for nonintegral `z`, and `B1(z)=0` for integral `z`.

The result needed here is: if integers `a_1,...,a_d` are units modulo `n` and

`sum_i B1(t*a_i/n)=0` for every integer `t`,

then their multiset can be partitioned into pairs summing to zero modulo `n`. This is Proposition 1.8 of Victor Batyrev and Johannes Hofscheier, *A generalization of a theorem of G. K. White*, [arXiv:1004.3411, p. 3](https://arxiv.org/pdf/1004.3411). The four-entry case is credited there to Morrison and Stevens, *Terminal quotient singularities in dimensions three and four* (1984), Corollary 1.3. We use this established theorem; we do not claim to reprove it here.

Assume `y=(A,B,C)` with

`A+B+C=1` in `F_p`.

Section 8 already disposes of every zero coordinate, so suppose `ABC!=0`. For the saturated-donor lengths of that section one has

`L_j=j+[-jA]_p+[-jB]_p+[-jC]_p`,

`L_j+L_(p-j)=4p`,

`L_j==j(1-A-B-C)=0 (mod p)`.

Short-freeness would force

`m<=L_j<=4p-m`.

Since `p<m<2p` and `2p<4p-m<3p`, the only multiple of `p` in this interval is `2p`. Hence

`L_j=2p` for all `1<=j<=p-1`.                         (7)

Apply the cited theorem to the four unit residues

`(1,-A,-B,-C)` modulo `p`.

Equation (7) gives the required Bernoulli-sum identity at every nonzero residue `j`; it also holds at multiples of `p` by the definition of `B1`. Periodicity covers all integer arguments.

The entry `1` must be paired with one of `-A,-B,-C`. The other two entries must pair with each other. Therefore `y` has one of the three forms

`(1,B,-B)`, `(A,1,-A)`, `(A,-A,1)`.

Sections 2–6 and 9 eliminate all three. We have proved:

> **Affine sum-one elimination.** No extreme-row companion can have `y_1+y_2+y_3=1`.

The affine sum-one hypothesis is essential to this reduction. Short-freeness alone has not been shown to force that hypothesis.

## 11. Scope, review, and next interface

The result eliminates every high-multiplicity value in the coordinate plane `Pi={(A,-A,kappa)}` on the single extreme rank-three row, as well as every value with a zero coordinate and the whole affine sum-one slice. A survivor `y=(A,B,C)` must therefore satisfy all of

`ABC!=0`, `A+B!=0`, `A+B+C!=1`.

These are necessary restrictions, not a classification or a claim that any survivor exists. The plane condition is not automatic. Other rank-three multiplicity rows, rank-two high-overlap rows, and the global corridor theorem remain open here.

Sections 2–9 use the existing shared-donor plane bound once and then only occurrence-valid residue identities. Section 10 explicitly invokes the established Bernoulli-pairing theorem and checks all its hypotheses. No prime sweep or coordinate enumeration supplies theorem authority.

An independently tasked proof-audit agent checked the plane-family certificates, the exact centered-residue gap, the `xy` exceptional certificate, the zero-coordinate argument, and the half-interval permutation argument. The reviewer also opened the primary Bernoulli-pairing source independently and checked the complete Section 10 hypothesis mapping. This is internal mathematical review, not an external referee or a novelty certificate.
