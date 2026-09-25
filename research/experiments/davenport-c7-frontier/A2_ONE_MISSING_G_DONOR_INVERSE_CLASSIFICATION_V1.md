# The type-two inverse classification survives one missing g occurrence — V1

Status: **proved exact prime-uniform inverse classification**. The fully saturated donor theorem remains true when `g^(p-1)` is replaced by `g^(p-2)`. This is the capacity needed by the rank-two companion problem.

## 1. Exact statement

Let `p=2H+1>=7` be prime, `m=3H+1`, `u=H+1=2^(-1)` in `F_p`, and `s=(u,u,1)` in the basis `(e1,e2,g)`. For `3<=K<=H+1`, put

\[
B^-_K=e_1^{p-1}e_2^{p-1}g^{p-2}s^K.
\]

Then `B^-_K y^(p-1)` has no nonempty zero-sum shorter than `m` if and only if one of the following holds:

1. `y=(A,-A,1)` with `A!=0`.
2. `y=(3^(-1),-3^(-1),2)` or its first-two-coordinate swap, and either `K=3` or `(p,K)=(11,4)`.

This is the same exact family and exceptional capacity as in `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md`. The new assertion is that necessity already holds for the smaller donor. No companion relation, rank condition on `y`, or atomicity hypothesis is imposed.

## 2. Recover the formal saturated profile from actual occurrences

Write `y=(A,B_0,C)` and

\[
L_j=j+[-jA]_p+[-jB_0]_p+[-jC]_p,
\qquad T=1-A-B_0-C.
\]

Sections 2–3 of `A2_SATURATED_VALUE_THREE_PLANE_RIGIDITY_V1.md` use exactly `B^-_2` and prove

\[
AB_0C\ne0,\qquad
L_j\ge m+2\ \text{if }jC\ne-1,
\qquad L_j\ge m\ \text{if }jC=-1.
\tag{1}
\]

The missing `g` occurrence is handled explicitly. When the formal third count `c_j=[-jC]_p` is at least two, the actual zero-sum

\[
y^j e_1^{[-jA]_p-1}e_2^{[-jB_0]_p-1}
g^{c_j-2}s^2
\]

has length `L_j-2` and third count at most `p-3`. At the remaining seam `c_j=1`, the unmodified completion is available. The zero-coordinate argument in the cited note excludes the two exceptional indices together with their negatives before using complementary lengths; it does not assume a full `g` donor.

Formal residue arithmetic still gives

\[
L_j+L_{p-j}=4p,\qquad L_j\equiv jT\pmod p.
\]

In particular, (1) proves the exact input

\[
m\le L_j\le4p-m
\tag{2}
\]

for the two-pattern argument of `A2_RANK3_EXTREME_FULL_ELIMINATION_V1.md`, Sections 2–3. Its use of (2) is an integer-profile argument, independent of whether the unmodified completion itself is available at every index.

## 3. Affine and centered profiles use no missing occurrence

If `T=0`, Section 5 of the three-plane note proves `L_j=2p` for every nonzero `j`. The four-entry Bernoulli pairing therefore gives a coordinate permutation of `(1,b,-b)`, `b!=0`. If the coordinate `1` is third, this is the first family in the theorem. Otherwise the symmetry of `e1,e2` reduces to `y=(1,b,-b)`. Unless `b=-1`, the half-interval lemma supplies `1<=j,v<=H` with `v=[jb]_p`. Then

\[
s y^j e_1^{H-j}e_2^{H-v}g^{v-1}
\]

is zero-sum of length `p-1<m`. Its `g` count is at most `H-1<=p-2`. At `b=-1`, the value is already `(1,-1,1)`.

If `T!=0`, (2) gives exactly the centered profile or the two-point anomaly. In the centered profile, the six-entry Bernoulli argument gives a coordinate permutation of

\[
(1,b,-2b),\qquad(2,b,-b),\qquad(u,b,-b).
\]

The donor theorem is [Batyrev–Hofscheier, Proposition 1.8](https://arxiv.org/pdf/1004.3411): unit residues with identically zero periodic first-Bernoulli sum pair into opposites. The four-entry application uses `(1,-A,-B_0,-C)`; the six-entry application uses `(1,-A,-B_0,-C,T,-2T)`. All entries are nonzero modulo the prime, and the respective least-residue sums are `2p` and `3p` at nonzero multipliers. At zero multipliers the Bernoulli terms vanish. This is the same verified donor application as in the existing notes.

For completeness, the occurrence audit of Sections 5–6 of the extreme-full-elimination note is:

| Coordinate placement | Certificate there | Maximum `s` count | Actual `g` count |
|---|---|---:|---|
| `(1,b,-2b)` | equation (6) | 1 | `2v-1<=p-2` |
| `(1,-2b,b)` | equation (7) | 1 | `p-v-1<=p-2` |
| `(b,-2b,1)` | equation (8) | 1 | `p-j-1<=p-2` |
| `(2,b,-b)` | equation (9) | 2 | `v-2<=p-3` when that certificate is used |
| `(u,b,-b)` | equation (10) | 1 | `v-1<=H-1` |

The selectors, nonnegative axis counts, and short lengths in those equations are unchanged. The exceptional multipliers and placements in this list are exactly `y=(A,-A,2)` or `y=(A,-A,u)`. The table also applies after swapping the first two coordinates. Thus the centered-profile reduction needs no `g^(p-1)` occurrence.

## 4. The anomalous profile also uses only the smaller donor

Sections 7–8 of the extreme-full-elimination note begin at the anomalous index `j` with `L_j=m` and positive completion counts `(a,b,c_j)`. Their normalization proceeds as follows:

1. If `c_j>=2`, the substitution in Section 2 gives an actual zero-sum of length `m-2`, so `c_j=1`.
2. The profile at `2j` shows exactly one of `j,a,b` exceeds `H`. If `j<=H`, a one-`s`, zero-`g` completion has length `m-1`. Hence `j>H` and `a,b<=H`.
3. At `p-j`, if `a,b<=H-1`, the three-`s` completion uses `g^(p-4)` and has length `m-2`. Thus, after swapping the axes, `a=H`, `b=v`, `j=2H-v`, `1<=v<=H-1`.

All these counts lie in `B^-_K` when `K>=3`. The resulting normalized six-tuple is `(j,H,v,1,H,1)`. At every even `2<=n<=p-3`, its exact residue profile forces

\[
[nv]_p<p-n.
\]

The two symbolic endpoints `n=p-3,p-5`, evaluated in Section 8 of the cited note, contradict this for every `p>=11`. No donor occurrences are used in that final integer contradiction.

At `p=7`, their only remaining tuple gives `y=(1,3,5)` or its first-two-coordinate swap. The pure certificate

\[
y s e_1^2g
\]

has sum `(7,7,7)` in the chosen coordinates and length five, below `m=10`. It uses one `g`. The swapped certificate is identical in scope. The entire anomalous profile is therefore excluded using the smaller donor.

## 5. The remaining two plane families and exact exceptions

After Sections 3–4, only the main family and the plane forms `(A,-A,2)`, `(A,-A,u)` remain. Sections 3–5 of `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md` use the following actual third counts:

| Step | `s` count | `g` count | Consequence |
|---|---:|---:|---|
| Exclude third coordinate `u` | 2 | `H-2` | length `m-1` for every `A!=0` |
| Restrict third coordinate `2` | 3 | 0 | only `A=+/-3^(-1)` can remain |
| Remove that exception at four copies | 4 | 1 | succeeds unless `p=11` |
| Remove the `p=11` exception | 5 | 0 | length `14<m=16` |

Each `g` count is at most `p-2`, including at `p=7`. Those residue identities and their exact exceptional congruence are unaffected by deleting the last `g` occurrence. They prove exactly the necessity claimed in Section 1, with the required `K` in each row.

For sufficiency, the complete all-subsequence proofs in Sections 6–8 of that same note establish short-freeness for the larger donor `e1^(p-1)e2^(p-1)g^(p-1)s^K y^(p-1)` in every stated family and capacity. Deleting one occurrence preserves short-freeness. This proves the converse for `B^-_K` without an additional classification assumption.

## 6. Audit and boundary

The new proof step is a capacity audit and a replacement of the formal-profile starting argument with the already proved original-donor seam bound. Every exceptional family, the `p=7` anomaly, and the `p=11,K=4` converse are retained. The external Bernoulli proposition was reopened in its primary source and its unit and all-multiplier hypotheses were checked.

No prime or vector enumeration is proof authority. This result does not extend to unsaturated powers of `y`; the complementary-index profile uses all `p-1` copies. It supplies an exact inverse theorem for the rank-two saturated boundary, not the full first corridor or a generalized Davenport equality. Internal review is by the producing researcher; no independent audit or novelty certification is asserted.
