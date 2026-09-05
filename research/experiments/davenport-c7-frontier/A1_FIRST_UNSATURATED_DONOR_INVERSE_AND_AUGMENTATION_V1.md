# Type one: deleting one high-power occurrence preserves the sharp inverse theorem

Status: **proved exact prime-uniform inverse classification and sharp augmentation threshold for the first unsaturated donor**. Two available sum-direction terms suffice to recover the same inverse family as in the saturated case, despite the missing complementary endpoint. This also excludes a high-overlap part of the type-one rank-two `t=p-2` boundary. It does not close all type-one companions or the first corridor.

## 1. Exact statement

Let `p=2H+1>=7` be prime, let `(f1,f2,f3)` be a basis of `C_p^3`, and put

\[
s=f_1+f_2+f_3,\qquad m=p+H,\qquad
z_0=\left\lfloor\frac{p+1}{4}\right\rfloor+1.
\]

For an integer `K>=2` and `y in C_p^3`, define

\[
F_K^-(y)=f_1^{p-1}f_2^{p-1}f_3^{p-1}s^K y^{p-2}.
\]

**Theorem.** The sequence `F_K^-(y)` has no nonempty zero-sum of length below `m` if and only if

\[
2\le K\le\left\lfloor\frac{p+1}{4}\right\rfloor,
\qquad y\text{ is a coordinate permutation of }(1,b,-b),\quad b\ne0.
\tag{1}
\]

In particular `F_(z0)^-(y)` contains a short zero-sum for every `y`. No companion relation or atomicity assumption is used. The theorem deliberately assumes `K>=2`; it makes no inverse claim at `K=1`.

Write `[a]_p` for the least nonnegative residue of a field element, and write `y=(A,B,C)`.

## 2. Complementary indices still exclude zero coordinates

For each actual power `1<=j<=p-2`, the saturated basis completes `y^j` to a zero-sum of length

\[
L_j=j+[-jA]_p+[-jB]_p+[-jC]_p.
\tag{2}
\]

The same expression defines the formal number `L_(p-1)`, but that endpoint is not assumed available. In the core `2<=j<=p-2`, both complementary indices are actual.

Suppose exactly `q` coordinates of `y` are nonzero. If `q=0`, the singleton is zero. If `q=1`, core complementarity gives `L_j+L_(p-j)=2p`, hence a length at most `p<m`. If `q=2`, it gives `L_j+L_(p-j)=3p=2m+1`. Short-freeness would put every core length in the two-element set `{m,m+1}`.

Put `T=1-A-B-C` in `F_p`. If `T!=0`, the core lengths have distinct residues `jT`; at least four such indices cannot occupy two integers. If `T=0`, these lengths are multiples of `p`, whereas neither `m` nor `m+1` is. Thus short-freeness forces `ABC!=0`.

## 3. One sum-direction term leaves only three possible slopes

All three completion counts in (2) are now positive. Replacing one of each basis term by one `s` saves two terms. Therefore

\[
L_j\ge m+2\qquad(1\le j\le p-2).
\tag{3}
\]

Core complementarity gives

\[
L_j\in[m+2,4p-m-2]
 =[2p-(H-1),2p+(H-1)]\qquad(2\le j\le p-2).
\tag{4}
\]

If `T!=0`, the `p-3` distinct core residues must fill exactly the `p-3` nonzero residues represented by `[-(H-1),H-1]`. The two omitted nonzero residues are `+/-H`. Since the omitted multipliers are `+/-1`, this forces `T=H` or `T=H+1`. Hence

\[
\boxed{T\in\{0,H,H+1\}.}
\tag{5}
\]

This keeps the unavailable `p-1` endpoint out of the interval count.

## 4. The zero slope gives the exact family

For `T=0`, (4) contains only one positive multiple of `p`, namely `2p`; thus every core `L_j` equals `2p`. The actual endpoint `L_1` is also a multiple of `p`, is at least `m+2>p`, and is at most `3p-2`. Therefore `L_1=2p`, and formal complementarity gives `L_(p-1)=2p` too.

The unit tuple `(1,-A,-B,-C)` consequently has zero periodic Bernoulli sum at every nonzero multiplier. At multiples of `p`, every Bernoulli summand is zero by definition, and periodicity covers all integers. Proposition 1.8 of [Batyrev--Hofscheier](https://arxiv.org/pdf/1004.3411) states that such a tuple of units can be paired into opposite residues. All its unit hypotheses hold because `ABC!=0` and `p` is prime.

The entry `1` pairs with a negative coordinate of `y`, leaving its other two coordinates opposite. Thus `y` is a coordinate permutation of `(1,b,-b)`, with `b!=0`.

## 5. The negative-half slope is impossible with two light terms

Suppose `T=H`. Formula (4) uniquely fixes the core value of `L_j` from its residue. The actual endpoint satisfies `L_1>=m+2`, `L_1<=3p-2`, and `L_1==H`, hence `L_1=2p+H`; complementarity fixes the formal opposite endpoint. Together these facts give, for every `1<=j<=p-1`,

\[
L_j=2p+[2jT]_p-[jT]_p.
\tag{6}
\]

Indeed `[2a]_p-[a]_p` is the centered representative of `a`. Adding `[jT]_p+[-2jT]_p` to (6) gives `3p`. Apply the same Bernoulli pairing proposition, now to the six units

\[
(1,-A,-B,-C,T,-2T)=(1,1,-A,-B,-C,H).
\]

The residue `H` cannot pair with either `1`, and the two `1` entries cannot pair with each other. Opposite pairing therefore forces `y` to be a permutation of `(1,1,H)`.

In that orientation the actual subsequence

\[
\boxed{y^{p-3}s^2 f_1 f_2 f_3^{H-3}}
\tag{7}
\]

is zero-sum of length `p+H-2=m-2`. The third coordinate vanishes because `3H==H-1 (mod p)`; the other two vanish directly. Its counts fit `K>=2`, `p-3<=p-2`, and `H>=3`. Basis permutation handles every orientation. This excludes `T=H`.

## 6. The positive-half slope is impossible by the third and fifth powers

Suppose `T=H+1=u`. The actual endpoint now satisfies `L_1=2p+u`, while (4) gives `L_2=2p+1`. Consequently

\[
2L_1-L_2=3p.
\tag{8}
\]

For each of the four unit residues in `(1,-A,-B,-C)`, doubling subtracts one `p` exactly when the positive residue is at least `u`. The residue `1` does not wrap. Equality (8) therefore forces all three negative-coordinate residues to wrap, so the positive integer representatives obey

\[
1\le A,B,C\le H,\qquad A+B+C=u.
\tag{9}
\]

The ordinary sum in (9) follows as well from `L_1=1+3p-A-B-C=2p+u`.

Both indices `3` and `5` are in the core, including at `p=7`. Their forced lengths are

\[
L_3=m+2,\qquad L_5=m+3.
\tag{10}
\]

If all three basis counts at either index were at least two, two copies of `s` would save four terms and give a short zero-sum. Therefore one coordinate `alpha` satisfies `3 alpha=-1`, and another coordinate `beta` satisfies `5 beta=-1`. They are different coordinates, since a common nonzero value would imply `2 alpha=0`.

By (9), `3 alpha<=3H<2p-1`, so the positive representative is `alpha=(p-1)/3`. Also `5 beta+1` is a positive multiple of `p`, giving `beta>=(p-1)/5`. It follows that

\[
\alpha+\beta\ge\frac{8(p-1)}{15}>\frac{p-1}{2}=H.
\]

But the third coordinate is at least one and the sum in (9) is `H+1`, so `alpha+beta<=H`. This contradiction excludes the last nonzero slope in (5).

## 7. The augmentation threshold and converse use available powers

The only possible values are now the family (1). The interval proof in `A1_SATURATED_AUGMENTATION_ELIMINATION_V1.md`, Section 5, chooses a multiplier

\[
1\le j\le p-z_0,\qquad [jb]_p\in[z_0,p-z_0]
\]

and uses

\[
s^{z_0}y^j
f_1^{p-j-z_0}f_2^{p-[jb]_p-z_0}f_3^{[jb]_p-z_0}.
\tag{11}
\]

Its exact length is `2p-2z0<m`. For `p>=7`, one has `z0>=3`, so `j<=p-3<p-2`: the same certificate is available in the first unsaturated donor. The cited note proves the intersection for all primes, including the equality case at seven. Thus `K>=z0` is impossible.

For completeness, existence of the intersection follows by sizes in `F_p^*` whenever `p+2>3z0`. The prime congruence classes give this inequality except at `p=7`. At seven, disjointness would force `b{1,2,3,4}={1,2,5,6}`; taking sums gives `3b=0`, impossible. This supplies every occurrence in (11) without a search.

The converse already holds with the larger power `p-1`, as proved for all subsequences in the cited note, Section 5.1; deleting one `y` preserves it. More directly, for `y=(1,b,-b)`, any zero-sum with a positive `y` count and `ell` copies of `s` has length at least `2p-2ell>=2p-2K>=m`. This follows by adding the first coordinate's positive multiple of `p` to the positive multiple of `p` from the other two coordinates. Donor-only nonempty zero-sums have length `3p-2ell` and obey the same bound. This proves both directions of (1).

## 8. Type-one rank-two consequence

Let

\[
U=f_1^{p-1}f_2^{p-1}f_3^{p-1}s,\qquad
V=s^c x^r y^{p-2},\qquad r=H+2-c>0.
\]

If

\[
\boxed{\left\lfloor\frac{p+1}{4}\right\rfloor\le c\le H+1,}
\tag{12}
\]

then the actual product contains `F_(z0)^-(y)` because `c+1>=z0`. It therefore has a nonempty zero-sum shorter than `m`. This excludes the complete displayed high-overlap range of the `t=p-2` boundary, including `r=1`.

Lower overlaps and smaller powers need their own arguments. The theorem does not infer any forbidden alternative factorization from the selected corridor triples.

## 9. Proof checks

The argument was checked locally for the omitted endpoint, zero-coordinate case, both centered slopes, the six-unit Bernoulli hypothesis, actual third/fifth powers at seven, and every multiplicity in (7) and (11). The primary Bernoulli source was reopened and its arbitrary-even-length statement checked. No prime sweep, independent-agent review, external referee approval, or global Davenport-value claim is asserted.
