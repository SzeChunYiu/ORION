# Exact radial lifting cost for every support-four maximal type — V1

Status: **proved prime-uniform structural theorem**. This gives the exact shortest realization of a multiple of the shared light direction from the actual resources of a canonical support-four maximal pair. It unifies the radial synthesis used separately in the `a=1` and `a=2` lanes. It does not by itself close the support-six equality face or determine a generalized Davenport constant.

## 1. Canonical maximal atom and radial problem

Let `p>=5` be prime and let

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

where

`g=s-a^(-1)(e1+e2)`, `1<=a<=(p-1)/2`.

Suppose a compatible companion contributes exactly `c` additional copies of the light value `s`. Thus the pair contains the radial resources

`e1^(p-1)e2^(p-1)s^(a+c)g^(p-a)`.

For `D in {0,...,p-1}`, define `lambda_{a,c}(D)` to be the minimum number of terms in a subsequence of these resources whose sum is `D s`.

Put

`u=[a^(-1)]_p`.

## 2. Exact formula

> **Theorem.** For every `D`,
>
> `lambda_{a,c}(D)` equals
>
> `boxed{ min_{0<=q<=p-a, 0<=z<=a+c, z+q == D (mod p)} (z+q+2[u q]_p). }`
>
> Here `q` is the number of copies of `g` and `z` the number of actual copies of `s`.

This is an exact minimum, not merely an upper bound.

## 3. Proof

Take any subsequence of the radial resources. Let

- `alpha` be its number of `e1` terms;
- `beta` its number of `e2` terms;
- `z` its number of `s` terms;
- `q` its number of `g` terms.

The resource bounds are

`0<=alpha,beta<=p-1`, `0<=z<=a+c`, `0<=q<=p-a`.

Its sum is

`(alpha-u q)e1+(beta-u q)e2+(z+q)s`.

For this to equal `D s`, the two saturated coordinates must vanish modulo `p`. Hence

`alpha == u q (mod p)`, `beta == u q (mod p)`.

Because `alpha,beta` both lie in the complete least-residue interval `0,...,p-1`, they are forced uniquely:

`boxed{alpha=beta=[u q]_p.}`

The radial coordinate is then exactly the congruence

`z+q == D (mod p)`.

Therefore every radial representation has term length

`z+q+2[u q]_p`

for a feasible pair `(q,z)` in the displayed box. Conversely, every feasible `(q,z)` produces an actual subsequence

`e1^[u q]_p e2^[u q]_p s^z g^q`

with sum `D s` and exactly that length. Minimizing proves the formula.

## 4. Equivalent one-dimensional form

For a fixed `q`, the congruence determines the least nonnegative candidate

`z_q=[D-q]_p`.

Thus

`boxed{lambda_{a,c}(D)=min_{0<=q<=p-a, [D-q]_p<=a+c} ([D-q]_p+q+2[u q]_p).}`

The minimization contains at most `p-a+1` scalar trials and is independent of the two new companion values.

This is the exact radial analogue of the one-parameter support-four depth formula.

## 5. Recovery of the previous synthesis identities

### Type `a=1`

Here `u=1`, `g=s-e1-e2`. For the low-overlap target `D=2c` with `2c<p`, choosing

`q=c-1`, `z=c+1`

gives

`lambda_{1,c}(2c)<=4c-2`.

In the range used by `RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md`, the checker confirms this is the exact radial cost. Thus the old realization

`(c+1)s+(c-1)g+(c-1)e1+(c-1)e2=2c s`

is the optimizer rather than an ad hoc certificate.

### Type `a=2`

Here `u=2^(-1)`. At target `D=2c`, the exact formula recovers the costs used in the `a=2` lane:

- `c=1`: `lambda_{2,1}(2)=2`;
- even `c>=2`: `lambda_{2,c}(2c)=3c-2` throughout the exact light-overlap range;
- odd `c>=3`: `lambda_{2,c}(2c)=3c-1` throughout the exact light-overlap range.

The identity `2s=2g+e1+e2` is therefore the first nontrivial instance of the general radial formula.

## 6. General doubling interface

In a first-corridor light-share support-three companion

`V=s^c x^r y^t`,

write

`r=H+1-c+d`, `t=2H-d`, `p=2H+1`.

Whenever `d>=c` and `2c<p`, doubling the companion relation gives the actual new-value residues

`A=2d-2c+1`, `B=p-2d-2`.

Therefore the exact radial theorem turns the doubled-relation test into the scalar inequality

`boxed{lambda_{a,c}(2c)+p-2c-1 < m,}`

because `A+B=p-2c-1`, where `m=3H+1` is the inherited short-free threshold plus one.

Equivalently,

`lambda_{a,c}(2c) < H+2c+1`.

Thus every canonical support-four type now has an exact arithmetic discriminator for whether **all interior rows `d>=c` die at once**. The previous `a=1` low-overlap and `a=2` all-overlap interior theorems are special cases.

## 7. Strategic consequence

The remaining prime-uniform first-corridor problem can now be split cleanly into two layers:

1. **radial arithmetic:** evaluate `lambda_{a,c}(2c)` (or other scalar targets) from the exact one-dimensional formula and remove full multiplicity regions;
2. **boundary geometry:** only after radial pruning, use atom relations, mixed new-value subsums, and quotient atomicity on the surviving boundary rows.

This is preferable to deriving a separate lifting identity for every support-four type `a`.

## Verification receipt

`check_support4_exact_radial_lifting_cost_v1.py` verifies the formula against an occurrence-level shortest-path dynamic program for every support-four type and admissible `c,D` on the bounded prime set through `31`. It also checks the one-dimensional formula through prime `101`, recovers the stated `a=1` and `a=2` target costs, and replays the doubling discriminator.

The checker is regression only; theorem authority is the coordinate-forcing proof above.

## Boundary

- The theorem computes radial lifting cost only; mixed `x,y` geometry is not encoded in `lambda`.
- Passing the doubling discriminator does not prove that a companion exists.
- Failure of the doubling discriminator does not imply existence; another scalar multiple or a mixed-depth argument may still eliminate the row.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
