# First-corridor Davenport generalization checkpoint — 2026-09-04 V5

Status: **live theorem-development checkpoint after the first four light-share layers on both principal rank-two types and after extraction of an exact all-type radial cost theorem. No `D_3` closure or novelty/priority claim.**

## 1. Prime-uniform target

For prime `p>=7`, the current local target is:

> if a critical first-corridor maximal pair has a support-four maximal atom, then its pair support is at least seven.

The first maximal corridor is

`C_1(p)=(p+1,(3p-1)/2,3p-2)`.

At exact pair support six, the companion is either

1. support three/rank two, sharing exactly one unsaturated maximal-atom value; or
2. support four/rank three, sharing both unsaturated values.

The two saturated actual values are unavailable to the companion.

## 2. Canonical maximal atom and depth interface

Every support-four maximal atom is, up to automorphism,

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`, `1<=a<=(p-1)/2`.

For a companion `V`, pair short-freeness is equivalent to the graded inequalities

`|W|+rho_U(-sigma(W))>=|V|`

for every nonempty proper `W|V`.

The antipodal-depth theorem also forces `V` to remain an atom of unchanged length in the quotients modulo each saturated direction `<e1>` and `<e2>`.

## 3. `a=1` rank-two light-share face

Write the support-three equality companion as

`V=s^c x^r y^t`.

The live branch now contains symbolic prime-uniform eliminations of

`c=1,2,3,4`

for every prime `p>=7`.

Thus every hypothetical survivor satisfies

`boxed{c>=5.}`

The `c=2` theorem has an independent hostile audit of its sole scalar resonance `(13,2,6,11)` using occurrence-level maximal-atom depth and companion cardinality DPs.

The imported `c=4` theorem is also hostile-audited independently:

- every multiplicity row and every scalar multiplier are scanned through prime `5000`;
- across 388365 rows, exactly three arithmetic resonances remain:
  `(7,4,1,5)`, `(13,4,3,12)`, `(17,4,8,13)`;
- occurrence-level exact depth replays over deliberately enlarged parameter universes give zero theorem survivors at all three bases;
- positive threshold mutations leave 6, 72, and 6 states respectively.

The `c=4` proof reveals the first clear boundary pattern: the two endpoints are controlled by denominator `c+1=5`, the two inner boundaries by denominator `c-1=3`, while the interior is killed by doubling.

## 4. `a=2` rank-two face

The heavy-share support-three branch is already impossible for every odd prime `p>=5`.

For the light-share branch

`V=s^c x^r y^t`,

the live branch now eliminates

`c=1,2,3,4`

for every prime `p>=7`. Hence

`boxed{c>=5}`

for every hypothetical `a=2` light-share support-three equality companion.

The exact multi-copy overlap ceiling is

`c<=2 floor((p-1)/4)`.

Consequently:

- at `p=7`, the whole `a=2` support-three face is empty;
- at `p=11`, the whole `a=2` support-three face is also empty.

The `c=4` theorem leaves one scalar resonance `(13,4,3,12)`, killed by two independent exact depth implementations; the full graded survivor count is zero.

## 5. Uniform interior theorem

Let `p=2H+1`, `m=3H+1`, and write any light-share support-three multiplicity row as

`r=H+1-c+d`, `t=2H-d`.

If `d>=c`, doubling gives new-value residues

`A=2d-2c+1`, `B=p-2d-2`.

`RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md` proves:

- for `a=1`, throughout `c<=floor((p+3)/4)`, every survivor satisfies `d<c`;
- for `a=2`, throughout the entire exact light-overlap range, every survivor satisfies `d<c`.

Thus the `a=2` rank-two problem is globally reduced from a two-dimensional multiplicity region to at most `c` boundary rows for each overlap `c`.

## 6. Exact radial lifting theorem for every support-four type

A new all-type theorem now replaces ad hoc radial identities.

Suppose the pair contains radial resources

`e1^(p-1)e2^(p-1)s^(a+c)g^(p-a)`,

and set `u=a^(-1) mod p`. Let `lambda_{a,c}(D)` be the shortest number of these terms summing to `D s`.

Then exactly

`lambda_{a,c}(D)=min (z+q+2[uq]_p)`,

where

`0<=q<=p-a`, `0<=z<=a+c`, `z+q == D (mod p)`.

The proof is coordinate-forcing: any radial representation using `q` copies of `g` must use exactly `[uq]_p` copies of each saturated axis.

This gives a one-dimensional exact arithmetic oracle for every canonical support-four type and turns doubled-relation elimination into the explicit discriminator

`lambda_{a,c}(2c)+p-2c-1 < m`.

The earlier `a=1` and `a=2` radial costs are exact special cases.

## 7. Current unresolved local mechanisms

The first-corridor support-seven theorem is not yet closed. The genuine remaining mechanisms are:

1. **rank-two boundary/high-overlap family:**
   - `a=1` light-share with `c>=5`;
   - `a=2` light-share with `c>=5` for primes whose overlap ceiling permits it;
   - other support-four types surviving the exact inverse-residue overlap selector;
   - after radial pruning, the problem is concentrated on boundary rows rather than interiors.
2. **rank-three support-four companion:**
   - companion shares both unsaturated values;
   - it remains atomic after projection modulo each saturated direction;
   - this bi-minimal circuit classification is now the qualitatively hardest local mechanism, especially for the `a=2` model.

## 8. Next proof targets

Do **not** continue indefinitely as `c=5,c=6,...` isolated layers.

### Rank-two target

Extract a uniform boundary multiplier/stability lemma suggested by `c=4`:

> after exact radial pruning, endpoint and inner-boundary multiplicity rows either admit a short lifted scalar relation controlled by denominators near `c+1` and `c-1`, or fall into a bounded arithmetic resonance family that can be attacked by exact depth/mixed-subsum rigidity.

The exact radial cost `lambda_{a,c}` is the right arithmetic interface.

### Rank-three target

Turn simultaneous quotient atomicity into a coefficient-box theorem:

> a rank-three four-support companion whose two saturated quotients are both length-preserving atoms cannot satisfy the first-corridor overlap and depth constraints.

This should be attacked as a two-kernel/box-avoidance problem, not by an unrestricted `C_p^3` search.

## 9. Publication gate

The present package has crossed the threshold from a finite-computation dossier to reusable prime-uniform structure:

- canonical support-four classification;
- exact depth and antipodal-shell theorems;
- simultaneous quotient atomicity;
- exact all-type radial lifting cost;
- uniform interior reduction;
- several audited prime-uniform boundary eliminations.

However, it is **not yet** recommended as a separate top-tier standalone paper. The strongest publication target is to first close the full prime-uniform first-corridor support-seven theorem and formulate the radial/boundary mechanism across support-four types. That would produce a coherent theorem rather than a technical sequel to the existing `C_5^3` work.

A new exact generalized Davenport value such as `D_3(C_7^3)`, or a prime-uniform stabilization theorem for `D_k(C_p^3)`, would raise the publication case substantially further.

## Claim ceiling

No line here claims:

- `D_3(C_7^3)` is determined;
- the candidate all-prime `D_k(C_p^3)` formula is proved;
- every first-corridor support-six face is eliminated;
- the public-literature search certifies novelty or priority.
