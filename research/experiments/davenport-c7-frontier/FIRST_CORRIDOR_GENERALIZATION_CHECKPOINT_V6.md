# First-corridor Davenport generalization checkpoint — 2026-09-04 V6

Status: **live theorem-development checkpoint after consolidation of both radial directions and all-type rank-two interior elimination. No `D_3` closure, all-prime `D_k` formula, or novelty/priority claim.**

## 1. Current local theorem target

For prime `p>=7`, prove in the first maximal corridor

`C_1(p)=(p+1,(3p-1)/2,3p-2)`

that a maximal pair whose maximal atom has support four must satisfy

`|supp(UV)|>=7`.

At exact support six, the companion is either

- support three/rank two, sharing exactly one unsaturated maximal-atom value; or
- support four/rank three, sharing both unsaturated values.

## 2. Canonical maximal atom

Write

`p=2H+1`, `m=(3p-1)/2=3H+1`,

and

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`, `1<=a<=H`.

The pair depth criterion, antipodal-shell theorem, and simultaneous quotient-atom theorem remain the structural base.

## 3. Exact radial arithmetic in both overlap directions

The live branch now contains exact shortest-cost formulas for radial synthesis from the actual pair resources.

### Light direction

If the companion contributes `c` copies of `s`, then

`lambda_{a,c}(D)=min (z+q+2[a^(-1)q]_p)`

over

`0<=q<=p-a`, `0<=z<=a+c`, `z+q==D (mod p)`.

### Heavy direction

If the companion contributes `c` copies of `g`, then

`mu_{a,c}(D)=min (z+q+2[a^(-1)(q-D)]_p)`

over

`0<=q<=p-a+c`, `0<=z<=a`, `z+q==D (mod p)`.

Both formulas are exact by saturated-coordinate forcing.

These replace ad hoc radial identities by one-dimensional arithmetic oracles.

## 4. All-type light-share interior theorem

For a light-share rank-two companion

`V=s^c x^r y^t`,

write

`r=H+1-c+d`, `t=2H-d`.

The interior is `d>=c`.

Put

`k=floor((c-1)/a)`.

The exact light radial theorem realizes `2c s` at cost at most

`2c+2k`.

Doubling the companion relation then gives an actual zero-sum of length at most

`2H+2k`.

If `a>=2`, every possible interior has `c<=H-1`, hence

`2k<=H`,

so the zero-sum has length at most `3H=m-1` and is forbidden.

Therefore:

> **For every canonical support-four type `a>=2`, every light-share rank-two survivor lies on the boundary strip `0<=d<c`.**

For `a=1`, the same argument works exactly through

`c<=floor(H/2)+1`.

Thus `a=1` is the unique canonical type with a possible genuinely high-overlap interior.

## 5. All-type heavy-share interior theorem

For a heavy-share companion

`V=g^c x^r y^t`,

pair capacity gives

`c<=a-1`.

Since `a<=H`, the pair contains at least `2c` literal copies of `g`. If `d>=c`, doubling gives

`2c g+(2d-2c+1)x+(p-2d-2)y=0`.

The resulting actual zero-sum has length exactly

`p-1`,

strictly below `m`.

Therefore:

> **For every canonical support-four type `a`, every heavy-share rank-two survivor lies on the boundary strip `0<=d<c`.**

No exceptional maximal type exists on the heavy side.

## 6. Audited first four light-share layers

The principal `a=1` and `a=2` light-share lanes now both eliminate

`c=1,2,3,4`

for every prime `p>=7`.

Hence in both lanes any hypothetical survivor has

`c>=5`.

The `a=1,c=4` proof is independently hostile-audited through prime `5000`; the independent scalar scan over 388365 multiplicity rows leaves exactly three resonances, all killed by occurrence-level depth replay with positive mutation controls.

The `a=2,c=4` proof has one scalar resonance at `p=13`, killed by two structurally different exact depth implementations.

The exact `a=2` overlap ceiling then closes the entire rank-two support-three `a=2` face at `p=7` and `p=11`.

## 7. What remains in rank two

The rank-two equality face is no longer a bulk multiplicity search.

Remaining mechanisms are:

1. **light-share boundary strips** `0<=d<c` for all types surviving the overlap selector;
2. **heavy-share boundary strips** `0<=d<c` for all types, except the already closed `a=2` heavy layer;
3. the **exceptional high-overlap `a=1` light interior** beyond `c=floor(H/2)+1`.

The `c=4` theorem gives the clearest boundary template so far:

- extreme boundary rows controlled by denominators `c+1`;
- inner rows controlled by denominators `c-1`;
- finitely many arithmetic resonances discharged by exact depth.

The next rank-two goal is a uniform boundary multiplier/stability lemma, not more isolated `c` layers.

## 8. Rank-three equality face

The support-four rank-three companion remains the qualitatively hardest local mechanism.

It shares both unsaturated maximal-atom values and, by the antipodal-depth theorem, remains an atom of unchanged length in each quotient modulo the two saturated directions.

Thus it is a bi-minimal four-support circuit. The correct next interface is a two-kernel coefficient-box problem:

> classify multiplicity boxes whose intersection with each of the two quotient relation planes contains no proper positive relation.

This should be attacked using quotient atomicity and the graded depth constraints, not an unrestricted `C_p^3` search.

## 9. Distance estimate

The prime-uniform first-corridor support-seven theorem now appears to require roughly **two to four major structural steps**, depending on whether the boundary lemma simultaneously handles light and heavy overlap:

- one uniform rank-two boundary theorem;
- one treatment of the exceptional high-overlap `a=1` interior, unless absorbed by the same theorem;
- one rank-three bi-minimal circuit theorem;
- possibly one short cleanup across overlap-selector residue classes.

The full generalized Davenport formula remains a major stage beyond this local theorem: other corridors, maximal atoms of larger support, and the global positive-gain conformal augmentation/refactor mechanism remain.

## 10. Publication gate

The project has now crossed an important qualitative threshold. The first-corridor lane contains several reusable prime-uniform theorems rather than only exact finite closures:

- support-four maximal-atom classification;
- exact depth and antipodal shell;
- simultaneous quotient atomicity;
- exact light and heavy radial lifting costs;
- all-type interior elimination in both overlap directions;
- hostile-audited boundary eliminations.

This is **strong enough to support a serious paper architecture**, but the recommended top-tier submission gate is still:

1. close the full prime-uniform first-corridor support-seven theorem; and
2. state the radial/boundary mechanism as a coherent theorem across support-four types rather than as a sequence of layer results.

At that point a standalone paper becomes plausibly worthwhile, subject to a real MathSciNet/zbMATH-level novelty audit. An exact `D_3(C_7^3)` result or prime-uniform `D_k(C_p^3)` stabilization theorem would make the top-tier case substantially stronger.

## Claim ceiling

No line here claims:

- `D_3(C_7^3)` is known;
- the candidate all-prime generalized Davenport formula is proved;
- the first-corridor support-seven theorem is closed;
- public web search certifies novelty or priority.
