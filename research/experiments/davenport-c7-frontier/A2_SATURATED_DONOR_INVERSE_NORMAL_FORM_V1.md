# An exact saturated-donor inverse normal form in `C_p^3` — V1

Status: **proved prime-uniform inverse classification and independently internally audited**. This theorem identifies every value whose full `p-1`-fold power can be adjoined to the indicated donor while preserving the short-zero-sum boundary. It does not assume a companion relation, a second new value, atomicity, or a support-rank condition on that value.

The theorem is a generalized structural normal form for this donor problem. It is not the generalized Davenport formula and does not settle all first-corridor multiplicities.

## 1. Exact theorem

Let `p=2H+1>=7` be prime, `m=p+H=3H+1`, and `u=H+1=2^(-1)` in `F_p`. In the basis `(e1,e2,g)` of `C_p^3`, set

`s=(u,u,1)`,

`B=e1^(p-1)e2^(p-1)g^(p-1)s^(H+1)`.

For an arbitrary group element `y`, the following are equivalent:

1. `B y^(p-1)` contains no nonempty zero-sum of length at most `m-1`.
2. `y=(A,-A,1)` for some `A!=0` in `F_p`.

All occurrences in the statement are actual sequence occurrences. There is no new-support assumption: values coinciding with a donor value are also covered and necessarily fail condition 1.

The prime lower bound is attained by explicit endpoint certificates, not by an enumerative classification at small primes.

## 2. Saturated completion excludes every zero coordinate

Write `y=(A,B_0,C)`. If `y=0`, its singleton is a zero-sum. Otherwise let `q` be the number of its nonzero coordinates. For `1<=j<=p-1`, saturated basis completion is available with length

`L_j=j+[-jA]_p+[-jB_0]_p+[-jC]_p`.

The complementary length is

`L_j+L_(p-j)=(q+1)p`.

Put `T=1-A-B_0-C`. If `T!=0`, then `L_j==jT (mod p)` gives `p-1` distinct lengths, so their range is at least `p-2`. Complementarity identifies the sum of their minimum and maximum with `(q+1)p`; therefore

`min_j L_j<=q p/2+1`.

For `q<=2`, this is at most `p+1<m`. If instead `T=0`, all `L_j` are positive multiples of `p`; complementarity gives a minimum at most `p` when `q<=2`. Thus every survivor has `A B_0 C!=0`.

## 3. A pure-power plane lemma

Suppose `A+B_0=0`. Then `A!=0`. Corollary 2 of `A2_SHARED_DONOR_PLANE_RIGIDITY_V1.md`, applied to the subdonor

`e1^(p-1)e2^(p-1)g^(p-2)s^(H+1)`

with `c=H-1`, implies that the least residue of `C` is `1` or `2`. Its hypotheses hold for every `p>=7`; the additional available `g` occurrence is not needed in that application.

We show that `C=2` is impossible using only powers of `y` and the donor.

For `p>=11`, choose `k` from `{H,H+1}` so that

`[-2A-ku]_p+[2A-ku]_p=p-k`.                         (1)

Such a choice always exists. Indeed, for a nonzero `P` with centered magnitude `d=min([P]_p,[-P]_p)`, the pair sum `[P-ku]_p+[-P-ku]_p` is `p-k` if `k` is even and `k<=2d`, or if `k` is odd and `k<=2(H-d)+1`; otherwise it is `2p-k`. For consecutive counts `H,H+1`, the failure inequalities for their opposite parities are incompatible. This is also proved in Section 3 of `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md`.

Adjoin `y^2`, `s^k`, the two saturated counts in (1), and `g^(p-4-k)`. All counts are available because `p-4>=H+1` for `p>=11`. Their length is

`2+(p-4)+(p-k)=2p-k-2<=m-1`.

For `p=7`, put `alpha=min([A]_7,[-A]_7)`. If `alpha` is `2` or `3`, use `y s^4 g` and saturated counts `[-A-2]_7,[A-2]_7`, whose sum is `3`. This gives length `9<m=10`. If `alpha=1`, use `y^2 s^3` and saturated counts `[-2A-5]_7,[2A-5]_7`, whose sum is `4`; this again gives length `9`. These cases cover the three possible centered magnitudes, with sign merely exchanging `e1,e2`.

We have proved the following exact necessary plane restriction, without another new value:

`A+B_0=0` implies `C=1`.                              (2)

## 4. The affine sum-one slice leaves precisely the stated family

Suppose `T=0`. All coordinates are nonzero by Section 2. Saturated completion gives

`L_j+L_(p-j)=4p`, `L_j==0 (mod p)`.

If there is no short zero-sum, both complementary lengths are at least `m`, so the only possible multiple of `p` is

`L_j=2p` for every `1<=j<=p-1`.

Apply Proposition 1.8 of Batyrev--Hofscheier, *A generalization of a theorem of G. K. White*, [arXiv:1004.3411, p. 3](https://arxiv.org/pdf/1004.3411), to the four unit residues `(1,-A,-B_0,-C)`. That established theorem says that an identically zero sum of periodic first Bernoulli functions on unit residues forces a partition into opposite pairs. Here the least-residue sum `2p` is precisely the required Bernoulli identity at nonzero arguments; at multiples of `p` all Bernoulli terms vanish by definition. The source credits the four-entry donor to Morrison--Stevens, Corollary 1.3 (1984); Batyrev--Hofscheier state and prove its arbitrary-entry version.

Thus `y` is a permutation of `(1,b,-b)`, with `b!=0`. If the coordinate `1` is third, this is the stated family. By symmetry of `e1,e2`, the other placements reduce to `y=(1,b,-b)`.

Unless `b=-1`, some `1<=j<=H` has `v=[jb]_p in {1,...,H}`. Otherwise multiplication by `b` sends the lower half of `F_p^*` onto the upper half, and summing those sets forces `b=-1` (the half-interval lemma in Section 4 of `A2_RANK3_EXTREME_FULL_ELIMINATION_V1.md`). For such `j,v`, the sequence

`s y^j e1^(H-j) e2^(H-v) g^(v-1)`                   (3)

is zero-sum of length `2H=p-1<m`. Every count is available. If `b=-1`, then `y=(1,-1,1)` already belongs to the stated family. This proves necessity throughout `T=0`.

## 5. The `T!=0` slice is empty: precise pure-donor dependency map

For clarity, the following application identifies exactly which parts of the accompanying proof are used, and why no companion relation or occurrence of `x` enters.

With `A B_0 C T!=0`, the lengths satisfy

`m<=L_j<=4p-m`, `L_j==jT (mod p)`, `L_j+L_(p-j)=4p`.

Sections 2--3 of `A2_RANK3_EXTREME_FULL_ELIMINATION_V1.md` prove from these identities alone that exactly one of two cases occurs:

- The centered pattern holds at every index; Bernoulli pairing on the six units `(1,-A,-B_0,-C,T,-2T)` then forces a permutation of `(1,b,-2b)`, `(2,b,-b)`, or `(u,b,-b)`.
- There is the exact two-point anomaly, with `L_j=m` at `jT=H` and the opposite extra lift at `jT=H+1`.

For the centered case, the certificates in Sections 5--6 of that note all use only `s`, `y`, and the saturated basis donor. The exceptional cases referred there to the plane interface are explicitly

`(1,-1,2)`, `(1,-1,u)`, `(2,-2,2)`, `(u,-u,u)`,

their `e1,e2` swaps, and the forms `(b,-b,2)` or `(b,-b,u)` where the distinguished coordinate is third. Each has `A+B_0=0` and `C` equal to `2` or `u`. Since `u>=4`, Section 3 excludes all of them. In particular none is the surviving plane family with `C=1`. Thus the entire centered case is ruled out without using `x` or the whole-plane companion theorem.

For the anomalous case, Sections 7--8 of that note again use only `s`, `y`, and the saturated donor. A short donor substitution at the unique minimal index forces `[-jC]_p=1`; doubling and an `s` substitution force `j>H`; an `s^3` substitution at `p-j` then forces, after exchanging the first two coordinates, the normalized six-tuple

`(j,H,v,1,H,1)`, `j=2H-v`, `1<=v<=H-1`.

For every even `2<=n<=p-3`, its exact Bernoulli sum requires

`[nv]_p<p-n`.

Taking `n=p-3` gives `v=floor(p/3)`; taking `n=p-5` contradicts this whenever `p>=11`. These are symbolic endpoint choices valid uniformly in the prime.

When `p=7`, their sole residual possibility is `(H,v,j)=(3,2,4)`, hence `y=(1,3,5)` or its first-two-coordinate swap. The pure certificate

`y s e1^2 g`                                         (4)

has zero group sum and length `5<m=10`; its swapped version treats the other ordering. Thus this endpoint also uses no `x`.

This completes necessity for all primes `p>=7`.

## 6. Converse: the whole family actually survives

Let `y=(A,-A,1)`, with `A!=0`, and consider an arbitrary nonempty zero-sum subsequence of `B y^(p-1)`. Let its `y` count be `j`, its `s` count be `z`, its `g` count be `w`, and its first two saturated counts be `a,b`. Thus

`0<=j,w,a,b<=p-1`, `0<=z<=H+1<p`.

The first two coordinates force

`a=[-jA-zu]_p`, `b=[jA-zu]_p`.

If `j>=1`, then `jA!=0` and the pair-cost identity from Section 3 gives

`a+b>=p-z`.

The third coordinate gives `j+z+w==0 (mod p)`. It is positive because `j>=1`, so `j+z+w>=p`. The total zero-sum length is therefore

`j+z+w+a+b>=p+(p-z)>=2p-(H+1)=m`.

If `j=0` and `z=0`, the three saturated basis coordinates, each used fewer than `p` times, force `a=b=w=0`; this is the empty subsequence and was excluded. Hence for a nonempty zero-sum with `j=0` one has `z>=1`. Now the forced pair sum is `p-z` when `z` is odd, and `2p-z` when `z` is even; in either case it is at least `p-z`. Also `z+w` is a positive multiple of `p`. The same lower bound `2p-z>=m` follows.

All possible zero-sums have been considered. This proves condition 1 and the equivalence.

## 7. Companion consequence and exact scope

Return to an extreme companion

`V=s^(H-1)g x y^(p-1)`

with `x=y-(H-1)s-g`. Since its combined donor is exactly `B`, short-freeness would force the normal form `y=(A,-A,1)`. The existing mixed argument in Sections 5--6 of `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md` then excludes this remaining family by an `x` singleton completion, except for the centered residue `|A|=ceil(H/2)`, where the explicit sequence

`x y s^(H-2) e_i`

is zero-sum of length `H+1<m`. Those sections depend only on `H>=3`, so apply at `p=7` as well as at larger primes. Thus this inverse theorem supplies an all-prime `p>=7` closure of the single extreme row.

The classification applies to the fully saturated basis donor with precisely `H+1` available copies of `s` and a full `p-1`-fold power of one value. Lower `y` multiplicities or lower shared-donor capacities are not silently included. The full rank-three `a=2` boundary and rank-two high-overlap cases remain separate.

The converse preserves the previously discovered pure-power obstruction as an exact theorem: on this donor, every member of the family survives every pure-power donor test. A second new value and its actual companion relation are necessary to eliminate that family in the extreme-row problem.

## 8. Verification and provenance

The infinite-prime proof is the written necessity and converse, with every external Bernoulli hypothesis mapped explicitly. The endpoint certificates at `p=7` are direct equations, not an exhaustive search. The accompanying full-elimination note contains the general occurrence formulas and the detailed two-pattern and endpoint proofs.

The generalized inverse statement was identified by the coordinating researcher after observing that the newly proved elimination mechanisms used no second new value. The inverse specialist checked this dependency and supplied the endpoint completions. The team developed and cross-checked the necessity, converse, and exact scope. No external referee approval or novelty certification is asserted.

Independent full internal audit: GREEN. A separately tasked auditor checked the exact written necessity dependency map, all exceptional plane coordinates, both `p=7` endpoint branches, the affine-sum-one pairing, the complete converse including donor-only zero-sums, and the all-prime extreme-row consequence. No first-corridor or generalized Davenport value is claimed.
