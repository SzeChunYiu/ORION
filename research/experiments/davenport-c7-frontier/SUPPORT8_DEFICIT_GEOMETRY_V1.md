# Support-8 deficit geometry for a length-37 `C_7^3` obstruction — V2

Status: **analytic reduction plus exact finite projective classification**. This does not yet eliminate all support-8 lifts.

Let `B` be zero-sum over `C_7^3`, `|B|=37`, and `z(B)<=3`. Existing reductions imply:

- `B` is 7-short-zero-free;
- every element has multiplicity at most 6;
- every one-dimensional subgroup contains at most 6 terms;
- every two-dimensional subgroup contains at most 18 terms.

Assume `|supp(B)|=8` and write the eight actual support multiplicities as `m_i`.

## Donor rank-two upgrade: Property C of `C_7^2`

The rank-two group `C_7^2` has Property D, hence Property C. Together with `eta(C_7^2)=19`, this says that a 7-short-zero-free sequence of length 18 in a plane is of the form `T^6` with `|T|=3`; in particular it has at most three distinct support values.

Therefore a plane containing **four or more actual support values** of `B` cannot carry 18 terms. Its occupancy is at most 17.

This donor theorem improves the raw `eta` plane bound exactly where the support geometry needs it.

## Deficit budget

Define

\[
d_i=6-m_i\in[0,5].
\]

Since `sum m_i=37`,

\[
\sum_{i=1}^8 d_i=48-37=11.
\]

This small total deficit converts subgroup occupancy bounds into incidence restrictions.

### At most one duplicated projective direction

If two distinct actual support elements lie on one projective direction, their combined occupancy is at most 6. Relative to the capacity `6+6=12`, that pair consumes deficit at least 6. Two disjoint duplicated directions would therefore consume at least 12 total deficit, exceeding the global budget 11.

Thus at most one projective direction can be represented by two distinct support values.

The exact local 7-short-zero-free check is stronger. Normalize a duplicated pair as `x` and `a x` with `a in F_7^*\{1}` and multiplicities `r,s`. Exhausting the finite one-dimensional states gives 18 oriented admissible `(a,r,s)` states, and every admissible duplicated pair has

\[
r+s\le5.
\]

The surviving scalar-ratio orbits under swapping are represented by ratios `2` and `3`; ratio `-1=6` never survives. See `check_support8_deficit_v1.py`.

### No plane contains five actual support elements

If five actual support elements lie in one two-dimensional subgroup, Property C upgrades its occupancy bound to at most 17. Relative to capacity 30 this costs at least 13 deficit, already larger than the global budget 11.

Hence every plane contains at most four actual support elements.

### A four-support plane costs at least seven deficit

If a plane contains four actual support values, its capacity is 24 and Property C forces occupancy at most 17. Thus its four deficits satisfy

\[
\sum_{i\in P}d_i\ge 7.
\]

This replaces the earlier weaker lower bound 6.

If two four-secants intersect in one support point `x` and the eighth support point outside their union is `y`, then adding the two plane inequalities gives

\[
14\le (11-d_y)+d_x.
\]

Hence

\[
d_x-d_y\ge3.
\]

In particular `d_x>=3`, so the common support value has multiplicity

\[
m_x=6-d_x\le3.
\]

Two support-disjoint four-secants are impossible a fortiori.

## Two projective geometry types

Every support-8 obstruction is therefore of one of the following forms.

**Type A — eight distinct projective directions.** The projected 8-set in `PG(2,7)` has no five collinear.

**Type B — one duplicated projective direction.** There are seven projected directions, exactly one represented by two scalar-distinct actual support values. A projective line through the doubled direction can contain at most two further projected support points, because three further directions would give five actual support elements in one plane.

The remainder of this file classifies Type A projective supports.

## Every Type-A support contains a projective frame

A projective frame in `PG(2,7)` is a four-point set with no three collinear.

Take any noncollinear triple `A,B,C` in the rank-three support. If a fourth support point lies outside the three sides `AB union AC union BC`, then `A,B,C,D` is a frame.

Otherwise every extra point lies on one of the three sides. If there are extra points `X in AB\{A,B}` and `Y in AC\{A,C}` on two different sides, then `B,C,X,Y` has no three collinear and is a frame. Thus, in a frame-free set, all extra points must lie on at most one side of the initial triangle. The entire set is then contained in one projective line plus the opposite vertex. Since Type A has at most four support points on any line, such a set has size at most five, contradicting size eight.

Therefore every Type-A support contains a projective frame, and frame normalization is globally complete.

## Exact projective classification

`generate_support8_projective_sets_v1.py` fixes the frame

`e1,e2,e3,(1,1,1)`,

enumerates every frame-containing 8-point set with no five collinear, and quotients by all internal ordered frames. `PGL(3,7)` acts sharply transitively on ordered projective frames, so the quotient is exact.

The generator obtains:

- projective points in `PG(2,7)`: **57**;
- normalized frame-containing candidates: **286,395**;
- projective equivalence classes: **350**;
- maximum line occupancy 2: **1** class;
- maximum line occupancy 3: **180** classes;
- maximum line occupancy 4: **169** classes.

The 350 classes have the following four-secant counts:

- no four-secant: **181** classes;
- one four-secant: **146** classes;
- two four-secants: **23** classes.

Among the last 23 classes, the two four-secants are disjoint on the support in **3** classes and intersect in a support point in **20** classes.

The three disjoint-four-secant classes are analytically impossible. For the remaining classes, the stronger Property-C deficit filter gives exact ordered deficit-profile counts:

- no four-secant: **25,488** profiles per class;
- one four-secant: **8,264** profiles per class;
- two intersecting four-secants: **1,061** profiles per class;
- two disjoint four-secants: **0** profiles.

Thus the Type-A projective-class/profile universe is reduced to

\[
181(25488)+146(8264)+20(1061)=\mathbf{5,841,092}
\]

pairs before scalar/kernel filtering, down from the raw `350*25488=8,920,800`.

## Generalizable pattern

For a `p`-short-zero-free sequence over `C_p^3`, every projective direction has occupancy at most `p-1`, while the rank-two identity `eta(C_p^2)=3p-2` gives plane occupancy at most `3p-3`. If Property C is available for `C_p^2`, a plane containing at least four actual support values improves further to occupancy at most `3p-4`.

If a support of size `s` has total length `N`, its capacity deficit

\[
\Delta=s(p-1)-N
\]

pays for repeated projective directions and overfull projective incidences. A direction represented by `t` actual support values costs at least `(t-1)(p-1)` deficit. With Property C, a plane containing `t>=4` actual support values costs at least

\[
t(p-1)-(3p-4)=(t-3)(p-1)+1.
\]

This deficit-incidence principle is the prime-uniform mechanism to carry forward; the `p=7,s=8` case is its first exact nontrivial instance.

## Boundary

- Type A projective geometry is classified, but scalar/multiplicity lifts over the surviving 347 classes are not yet exhausted here.
- Type B (one duplicated direction) is structurally reduced but not yet projectively classified.
- Property C is donor structure; no ownership claim is made for it.
- No global claim about `D_3(C_7^3)` or the general `C_p^3` formula is made by this file alone.
