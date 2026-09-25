# Type `a=2` extreme rank-three boundary: full elimination — V1

Status: **proved for every prime `p>=11` and independently internally audited**. The entire extreme multiplicity row `c=H-1,d=1,r=1,t=p-1` is eliminated, without a plane or affine-sum hypothesis on the high-multiplicity value. The proof is structural and prime-uniform. It uses an established Bernoulli-pairing theorem, exact donor certificates, and two symbolic residue endpoints; no enumeration of hypothetical companions supplies theorem authority.

This result closes one multiplicity row. It does not close the other rank-three `a=2` rows, the first-corridor theorem, or a generalized Davenport formula.

## 1. Setup and prior proved interfaces

Let `p=2H+1>=11` be prime, `u=H+1=2^(-1)` in `F_p`, and `m=p+H=3H+1`. In the basis `(e1,e2,g)`, set

`s=(u,u,1)`,

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`,

`V=s^(H-1)g x y^(p-1)`.

Assume `V` is zero-sum, `x,y` are distinct new values, and its displayed support has rank three. The companion relation is

`x=y-(H-1)s-g`.                                      (1)

The actual shared donor in `UV` is

`B=e1^(p-1)e2^(p-1)g^(p-1)s^(H+1)`.

Suppose for contradiction that `UV` has no nonempty zero-sum of length below `m`. Write `y=(A,B_0,C)`; the subscript distinguishes a coordinate from the donor sequence.

The proved note `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md` supplies three interfaces for this exact row:

1. Every coordinate of `y` is nonzero.
2. A value with `A+B_0=0` is impossible.
3. A value with `A+B_0+C=1` is impossible.

The third interface invokes Proposition 1.8 of Batyrev--Hofscheier, described precisely in Section 3 below. The current proof handles the entire complement of those previously eliminated slices.

Put

`T=1-A-B_0-C`.

Hence `A B_0 C T !=0`. For `1<=j<=p-1`, saturated basis completion gives an available zero-sum with length

`L_j=j+[-jA]_p+[-jB_0]_p+[-jC]_p`.                  (2)

Here and below `[z]_p` is the least nonnegative residue. All four terms in (2) are positive; all three donor counts are at most `p-1`. Complementary indices satisfy

`L_j+L_(p-j)=4p`, `L_j==jT (mod p)`.

Short-freeness therefore forces

`p+H<=L_j<=3p-H`.                                    (3)

## 2. An exact two-pattern rigidity theorem

Let `q=[jT]_p`. Since `T!=0`, these `q` run through `1,...,p-1`. Bounds (3) permit the following lifts of `q`:

- `L_j=2p+q` when `1<=q<=H-1`;
- `L_j=p+q` when `H+2<=q<=p-1`;
- at `q=H`, either `L_j=2p+H` or `L_j=p+H`;
- at `q=H+1`, either `L_j=p+H+1` or `L_j=2p+H+1`.

Complementarity links the last two choices. Thus there are exactly two possible global patterns.

**Pattern I (centered pattern).** For every nonzero `j`,

`L_j=2p+[2jT]_p-[jT]_p`.                            (4)

Indeed `[2q]_p-[q]_p` is `q` for `q<=H` and `q-p` for `q>=H+1`.

**Pattern II (two-point anomaly).** Equation (4) holds except at the two indices with `jT=H` and `jT=H+1`. At the first index its right-hand side is reduced by `p`; at the second it is increased by `p`.

In particular the unique index `j_0` satisfying

`j_0 T=H`

has `L_(j_0)=m` under Pattern II. No residue endpoint has been discarded.

## 3. Pattern I forces three precise coordinate families

We use the established Bernoulli-pairing theorem in Proposition 1.8 of Victor Batyrev and Johannes Hofscheier, *A generalization of a theorem of G. K. White*, [arXiv:1004.3411, p. 3](https://arxiv.org/pdf/1004.3411). It states that for unit residues `a_i` modulo `n`, the identity

`sum_i B1(t*a_i/n)=0` for every integer `t`

forces their multiset to partition into pairs summing to zero modulo `n`. Here `B1(z)={z}-1/2` off the integers and `B1(z)=0` at integers. This external theorem is not a theorem proved or first claimed in this note.

Under Pattern I, apply it to the six unit residues

`(1,-A,-B_0,-C,T,-2T)`.

For nonzero `j`, their least residues sum to

`L_j+[jT]_p+[-2jT]_p=3p`

by (4). Thus their Bernoulli sum is zero. At multiples of `p`, all terms are zero by definition; periodicity covers every integer. Every entry is a unit because `A B_0 C T!=0` and `p` is odd.

The two labeled entries `T` and `-2T` cannot pair with each other, since their sum is `-T!=0`. Consequently, among the original four entries `(1,-A,-B_0,-C)`, one equals `-T`, another equals `2T`, and the other two are opposites. Distinct labeled occurrences are used even when some values coincide. Locating the entry `1` yields exactly these possibilities, up to permuting coordinates:

`y=(1,b,-2b)`, or `y=(2,b,-b)`, or `y=(u,b,-b)`,        (5)

with `b!=0`. If `1` belongs to the opposite pair, the first family results. If `1=-T`, then `T=-1` and one coordinate of `y` is `2`; if `1=2T`, then `T=u` and one coordinate is `u`.

## 4. A half-interval lemma

Write `I={1,...,H}`. If a nonzero multiplier `D` satisfies `D I=I`, then `D=1`; if `D I=-I`, then `D=-1`. To see this, sum the members modulo `p` and use

`sum_(i=1)^H i=H(H+1)/2 !=0 (mod p)`.

Therefore:

- unless `D=-1`, some `j in I` has `[Dj]_p in I`;
- unless `D=1`, some `j in I` has `[Dj]_p in -I`.

For example, failure of the first assertion puts the `H` distinct values of `D I` inside the `H`-element set `-I`, hence gives equality and the stated exceptional multiplier. These are exact set arguments, without a search over primes or values.

## 5. Every permutation of the first family is eliminated

The exchange of `e1,e2` is a symmetry of the donor. Thus it suffices to handle the following three forms. All unspecified donor counts are zero.

### 5.1. `y=(1,b,-2b)`

Unless `b=-1`, Section 4 supplies `1<=j<=H` and `v=[jb]_p` with `1<=v<=H`. Then

`s y^j e1^(H-j) e2^(H-v) g^(2v-1)`                 (6)

is zero-sum. The first two coordinates each sum to `u+H=p`; the third is `1-2v+(2v-1)=0`. Its length is

`p-1+v<=p+H-1=m-1`.

Every exponent is nonnegative, with `2v-1<=p-2`. The exception `b=-1` has `A+B_0=0`, already excluded in Section 1.

### 5.2. `y=(1,-2b,b)`

Unless `2b=1`, Section 4 supplies `1<=j<=H` with `w=[2jb]_p in {H+1,...,p-1}`. Put `v=[jb]_p`. Then

`s y^j e1^(H-j) e2^(w-u) g^(p-v-1)`                (7)

is zero-sum: its second coordinate is `u-2v+w-u=0` modulo `p`, and the other coordinates cancel directly. Its length is

`p-1+w-v`.

When `v<=H`, this is `p-1+v<=m-1`; when `v>=H+1`, it is `v-1<=p-2`. All displayed exponents are in the actual donor ranges. The exceptional multiplier is `b=u`, which gives `y=(1,-1,u)` and is already excluded by the plane interface.

### 5.3. `y=(b,-2b,1)`

Choose any integer `v` with `ceil(u/2)<=v<=H`, and let `j=[v b^(-1)]_p`, so `1<=j<=p-1`. Then

`s y^j e1^(H-v) e2^(2v-u) g^(p-j-1)`               (8)

is zero-sum of length `p-1+v<=m-1`. The interval is nonempty, `2v-u>=0`, and all capacities are respected. In particular the third coordinate is `1+j+(p-j-1)=p`.

Swapping `e1,e2` in these three cases covers all coordinate permutations, including coincidences among the coordinate values.

## 6. Every permutation of the other two families is eliminated

If the distinguished coordinate `2` or `u` is third, (5) has first-coordinate sum zero and is already excluded. The donor symmetry reduces the other placements to the following forms.

For `y=(2,b,-b)`, put `j=H`, `v=[Hb]_p`. If `v>=2`, then

`s^2 y^H e2^(p-v-1) g^(v-2)`                       (9)

is zero-sum of length `H+2+p-3=m-1`. Its first coordinate is `2u+2H=2p`; its other coordinates cancel modulo `p`. If `v=1`, then `b=H^(-1)=-2`, so the plane interface excludes `y=(2,-2,2)`.

For `y=(u,b,-b)`, unless `2b=-1`, Section 4 supplies `1<=ell<=H` with `v=[2ell b]_p in I`. Then

`s y^(2ell) e1^(H-ell) e2^(H-v) g^(v-1)`            (10)

is zero-sum of length `2H+ell<=3H=m-1`. The first coordinate is `u+ell+H-ell=p`, and the other two cancel directly. All new-value occurrences are available because `2ell<=p-1`. If `2b=-1`, then `b=-u`; the plane interface excludes `y=(u,-u,u)`.

This completes the elimination of Pattern I.

## 7. Pattern II: exact minimality forces a sparse normalized tuple

Let `j=j_0` be the anomaly index with `jT=H` and `L_j=m`. Set

`a=[-jA]_p`, `b=[-jB_0]_p`, `c=[-jC]_p`.

Thus `j,a,b,c` are in `1,...,p-1` and their sum is `m`.

First, `c=1`. If `c>=2`, replace one `e1`, one `e2`, and two `g` occurrences in the saturated completion by two `s` occurrences, using `2s=e1+e2+2g`. The available zero-sum

`y^j s^2 e1^(a-1) e2^(b-1) g^(c-2)`

has length `m-2`, a contradiction. Therefore

`c=1`, `j+a+b=3H`.                                  (11)

At index `2j`, the residue `2jT=2H=-1` is not an anomaly endpoint. Hence Section 2 gives

`L_(2j mod p)=2p-1`.

Doubling the four residues `j,a,b,1` from length `m` reduces their sum by `p` for every entry exceeding `H`. Since `2m-(2p-1)=p`, exactly one of `j,a,b` exceeds `H`.

If `j<=H`, exactly one of `a,b` exceeds `H`. Use one `s` and no `g` to complete `y^j`. The saturated pair counts are `[a-u]_p,[b-u]_p`, whose sum is `a+b-2u+p`. This gives length

`j+1+a+b-2u+p=3H=m-1`.

Consequently

`j>H`, `1<=a,b<=H`.                                  (12)

Now consider the index `p-j`. Its saturated target is `(p-a,p-b,p-1)`. If both `a,b<=H-1`, use three `s` occurrences. Since `3u=H+2` modulo `p`, the donor counts

`e1: H-1-a`, `e2: H-1-b`, `g: p-4`, `s: 3`

are all available. Together with `y^(p-j)`, their length is

`p-j+3+(H-1-a)+(H-1-b)+(p-4)=3H-1=m-2`.

Thus one of `a,b` equals `H`. By donor symmetry, set `a=H`, `b=v`. Equations (11)--(12) give

`j=2H-v`, `1<=v<=H-1`.                               (13)

Multiply the six residues in Section 3 by `j`. Since `jT=H` and `-2H=1`, their normalized tuple is exactly

`(j,H,v,1,H,1)`.                                     (14)

Its least-residue sum is `2p` at multiplier `n=1`, `4p` at `n=p-1`, and `3p` at every other nonzero multiplier. This follows directly from the signs and locations of the two anomalies in Section 2.

## 8. Two symbolic endpoints rule out the anomalous tuple

Let `n=2t` be any even integer with `2<=n<=p-3`. In (14), each `H` entry contributes `p-t` and each `1` contributes `n`. Its required total `3p` gives

`[nj]_p+[nv]_p=p-n`.                                (15)

Since `j+v=2H=-1` modulo `p`, and neither `j` nor `v` is zero, equation (15) is equivalent to

`[nv]_p<p-n`.                                       (16)

Indeed the two positive residues on the left of (15) sum either to `p-n` or to `2p-n`; the former occurs exactly under (16). Equality `[nv]_p=p-n` would force `nj=0`, which is impossible.

Take `n=p-3`. Then `[ -3v ]_p` is `1` or `2`. As `1<=v<=H-1`, one has `0<3v<2p-2`, so

`3v=p-1` or `3v=p-2`,

and therefore `v=floor(p/3)`. The prime `p>=11` is not `3`.

Next take `n=p-5`, also even and within the range of (16). It requires

`[-5v]_p<5`.                                        (17)

If `p=3l+1`, then `v=l` and `[-5v]_p=l+2`; condition (17) forces `l<=2`, hence `p<=7`. If `p=3l+2`, then `v=l` and `[-5v]_p=l+4`; for `p>=11` this is at least `7`, contradicting (17). The displayed residues are between `1` and `p-1` in their stated ranges.

Both alternatives contradict `p>=11`. Thus Pattern II is impossible.

## 9. Conclusion and an optional `p=7` anomaly certificate

All coordinates nonzero and `T!=0` led to exactly two patterns. Sections 3--6 exclude the first, and Sections 7--8 exclude the second. The prior interfaces handle the discarded zero-coordinate, plane, and affine-sum slices. Therefore:

> **Extreme-row elimination theorem.** For every prime `p>=11`, no zero-sum companion `V=s^(H-1)g x y^(p-1)` with the stated new-support and rank-three hypotheses can make `UV` free of nonempty zero-sums of length below `m`.

For `p=7` alone, the surviving endpoint possibility in Section 8 is `H=3,v=2,j=4`. Then `(a,b,c)=(3,2,1)` gives `y=(1,3,5)` and, by (1), `x=(0,2,2)`. The sequence

`x s^3 e1^2 g^2`

is zero-sum of length `8<m=10`. Swapping `e1,e2` gives the other coordinate ordering. This certifies the `p=7` anomalous subcase only; the theorem above retains `p>=11`, because its prior plane-interface proof was stated in that range.

## 10. Provenance, failed-route correction, and audit boundary

The exact two-pattern reduction explains why forcing `T=0` from saturated pure-power tests would have been invalid. Even when `T!=0`, a centered pattern can pass all those tests; pairing then yields the additional three families in (5). Nor can the two-point anomaly be suppressed: it needs the separate saturated-donor improvement and endpoint argument.

The Bernoulli theorem is an attributed external ingredient. The two-pattern reduction, donor-family certificates, and anomaly normalization were developed in internal collaboration between an inverse zero-sum specialist and the coordinating researcher. The coordinator supplied the decisive `p-3,p-5` endpoint argument, which the specialist checked independently. These role descriptions record the internal review process, not external referee approval or a novelty certificate.

Independent internal full-proof audit: GREEN. A separately tasked auditor checked every occurrence certificate, the six-entry pairing classification, both residue patterns, the anomaly normalization, and both symbolic endpoints, and independently opened Proposition 1.8 in its primary source. No global claim ledger or manuscript authority is promoted by this note.
