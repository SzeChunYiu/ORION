# Positive-even selector for arbitrary rank-two opposite boundary layers — V1

Status: **proved prime-uniform complementary selector, complete square-root overlap range, and a high-relative-overlap reduction**. The theorem treats arbitrary overlap `c` through explicit capacity inequalities. In particular, for both exceptional light types `a=1,2`, every rank-two light-share companion with `2<=c` and `4c^2<=p` is impossible. For type `a=2`, the opposite boundary half with `p/3<c<=H` reduces to `r<(H+1)/2`.

These are structural occurrence certificates. No finite enumeration supplies their authority. The remaining exceptional faces, full first-corridor theorem, and generalized Davenport values remain unproved by this note.

## 1. Boundary and donor-capacity statement

Let `p=2H+1>=7` be prime and `m=p+H`. Consider a relation

`c s+r x+t y=0`,

where `2<=c<=H` and

`r=H+1-e`, `t=p-f`, `e,f>=1`, `e+f=c+1`, `e>f`.

Thus this is the strict opposite half of the boundary used in the balanced-selector notes. Put

`alpha=2e-1`, so `2r=p-alpha` and `alpha+2f=2c+1`.

The opposite-half assumption gives

`c+1<=alpha<=2c-1`, `f<=floor(c/2)`.

Define

`j=ceil(p/(2c))`, `w=2jc-p`, `n=2j`.

The division remainder satisfies

`1<=w<=2c-1`.

The scalar is nonzero: since `c>=2`,

`2j<=2ceil(p/4)<p`.

Assume the two explicit capacity inequalities

`(2j-1)alpha>=p`, `j alpha<=p-1`.                       (1)

Suppose an old-support donor, disjoint from the available `x^r y^t`, realizes `w s` using at most `w+E(w)` terms. Then (1) supplies an actual zero-sum of length at most

`boxed{p-j+E(w).}`                                     (2)

In particular, it contradicts `(m-1)`-short-freeness whenever

`boxed{E(w)<=H+j-1.}`                                  (3)

This statement needs the displayed group relation and actual occurrence capacities. It does not need a classification of `x,y`, or an assertion that every index-one multiplier fits.

### Proof

The least positive residues of the multiplied relation are

`D=[nc]_p=w`,

`A=[nr]_p=p-j alpha`,

`B=[nt]_p=p-2jf`.

Indeed, `2jc=p+w` and `2jr=jp-j alpha`. The upper inequality in (1) proves `A>=1`; the lower one is exactly

`p-j alpha<=(p-alpha)/2=r`.

For the other new value,

`2jf<=jc=(p+w)/2<p`,

because `f<=floor(c/2)` and `w<=2c-1<p`. Thus `B>=1`. Also `2jf>=f`, so `B<=p-f=t`. Every stated residue is consequently positive, correctly unwrapped, and within its available multiplicity.

Finally,

`D+A+B=w+2p-j(alpha+2f)`

`=w+2p-j(2c+1)=p-j`.

Replace the `D s` term by its donor representation and adjoin `x^A y^B`. This proves (2), and (3) gives length at most `m-1`.

## 2. Type a=2: every capacity-compatible row is eliminated

Use the actual donor

`B=e1^(p-1)e2^(p-1)g^(p-2)s^(c+2)`,

where `e1+e2=2(s-g)`. This is the canonical maximal atom together with all shared `s` occurrences.

Set

`q=2ceil(max(w-c-2,0)/2)`, `z=w-q`.

The donor subsequence

`e1^(q/2)e2^(q/2)g^q s^z`

has sum `w s` and length `w+q`. Its counts are explicit. If `w<=c+2`, then `q=0` and `z=w`. Otherwise `q` is `w-c-2` or `w-c-1`, and hence `z` is `c+2` or `c+1`. In particular, `0<=z<=c+2`.

Moreover,

`q<=c-2<=H-2<p-2`.                                    (4)

For (4), the case `c=2` has `q=0`; otherwise the rounded quantity is the smallest even integer at least a nonnegative integer bounded by `c-3`, and is at most `c-2`. Thus the `g` and saturated counts fit as well.

Taking `E(w)=q` in (2) gives length at most

`p-j+c-2<=p+H-j-2<m`.

Therefore **every type-two opposite boundary row satisfying (1) is impossible**, for arbitrary `2<=c<=H`. The actual type-two overlap ceiling, `c<=2floor(H/2)`, can be imposed separately when applying this theorem to a hypothetical companion.

## 3. Type a=1: exact score and an automatic range

In saturated coordinates,

`U=f1^(p-1)f2^(p-1)f3^(p-1)s`, `s=f1+f2+f3`.

The enlarged donor has `c+1` copies of `s`. Set

`q=max(w-c-1,0)`, `z=w-q`.

Then `f1^q f2^q f3^q s^z` has sum `w s` and length `w+2q`. Here `0<=z<=c+1` and `q<=c-2<=p-1`, so every occurrence fits.

Consequently the same scalar has exact constructed score

`boxed{p-j+2max(w-c-1,0).}`

It is short whenever

`2max(w-c-1,0)<=H+j-1`.                                (5)

In particular, (5) is automatic if `c<=H/2`, since

`2max(w-c-1,0)<=2c-4<=H-4`.

Thus the type-one theorem retains the exact score condition outside this automatic range. No type-two surcharge is silently substituted for the type-one surcharge.

## 4. A complete prime-uniform range of entire overlap layers

Assume `2<=c` and `4c^2<=p`. Then

`j=ceil(p/(2c))>=2c`.

This forces (1) for every opposite-half value of `alpha`. For its upper inequality,

`j alpha<=j(2c-1)=p+w-j<=p-1`,

because `w<=2c-1<=j-1`. For its lower inequality,

`(2j-1)alpha-p >=(2j-1)(c+1)-(2jc-w)`

`=2j-c-1+w>=2j-c>=0`.

Also `4c^2<=p` with `c>=2` implies `c<=H/2`. Sections 2 and 3 therefore eliminate the entire opposite boundary half for both types.

To assemble the complete layer, use the already proved results with their actual hypotheses:

- For type `a=2`, `RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md` eliminates every multiplicity interior throughout its allowed overlap range. The balanced boundary is eliminated by `A2_RANK2_BALANCED_BOUNDARY_SELECTOR_V1.md` whenever `c<=p/3`.
- For type `a=1`, the same interior note applies when `c<=floor((p+3)/4)`. The balanced boundary is eliminated by `A1_RANK2_BALANCED_BOUNDARY_SELECTOR_V1.md` whenever `c<=p/7`.

All these hypotheses follow from `4c^2<=p`, since `4c^2>=7c` for `c>=2` and `4c^2>=4c-3`.

> **Entire-layer theorem.** Let `a` be `1` or `2`. A first-corridor exact-support-six maximal pair with canonical support-four maximal atom of type `a` cannot have a rank-two, support-three, light-share companion whose shared multiplicity satisfies
>
> `boxed{2<=c, 4c^2<=p.}`

The earlier `c=1,2,3,4` theorems remain independent and can cover additional primes outside this new range. Unlike the earlier balanced selectors alone, the entire-layer theorem leaves no opposite-half multiplicity row at these overlaps. Its number of covered overlap layers grows without bound with `p`.

## 5. Type a=2 high relative overlap forces small r

Suppose

`p/3<c<=H`, `e>f`.

Then `j=2`. Since `alpha>c>p/3`, the first inequality in (1), namely `3alpha>=p`, is automatic. The second is

`2alpha<=p-1`, equivalently `alpha<=H`.

Section 2 thus proves:

> **High-overlap reduction.** Every surviving type-two opposite-half boundary row with `p/3<c<=H` must satisfy
>
> `boxed{alpha>H}`, equivalently `boxed{r<(H+1)/2.}`

The eliminating scalar in this range is simply `n=4`. This conclusion applies beyond the square-root overlap range, but does not eliminate its small-`r` remainder or assert anything new about the balanced high-overlap half.

## 6. Failed extension and exact residual scope

The two inequalities (1) cannot be removed. In particular, a rank-two companion with `r=1` admits no relation multiplier other than `n=1` satisfying `[nr]_p<=r`. At the type-two top-overlap row

`p==1 (mod 4)`, `(c,r,t)=(H,1,p-1)`,

this blocks every nontrivial relation-scalar certificate. The original scalar has light residue `c`, and its literal donor completion gives length exactly `m`, not a forbidden short zero-sum. This is a structural limitation of scalar-only proofs, not evidence that such a full companion exists.

For type one, the actual light-overlap range can exceed `H`; those larger overlaps are outside the present positive-even setup. Even within `c<=H`, both (1) and the exact score condition (5) remain required outside their proved automatic ranges.

The remaining faces therefore include small-new-multiplicity mixed geometry, type-one large relative overlap, and portions of both boundary halves beyond the established selectors. The complete first-corridor support-seven theorem and any `D_k(C_p^3)` equality require additional arguments.

## 7. Mathematical review

The producing agent and a separately tasked proof auditor checked the residue formulas, scalar nonvanishing, both new-value capacities, donor reconstruction, rounding, strict score, square-root assembly, and the high-overlap reduction. The root integrates this additive proof note. This is internal proof review, not external referee approval or a novelty certificate.

The proof uses the earlier structural radial and interior theorems, with their scope retained, and elementary arithmetic. No new external theorem, prime sweep, vector enumeration, or finite-search authority is invoked.
