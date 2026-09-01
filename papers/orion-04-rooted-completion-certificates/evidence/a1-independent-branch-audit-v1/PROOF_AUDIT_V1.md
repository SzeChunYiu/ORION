# ORION-04 A1 independent branch-cover proof audit

**Status:** `PASS__INDEPENDENT_COVER_RECONSTRUCTION_MATCHES_COMMITTED`  
**Scientific authority delta:** `NONE`  
**External / human peer-review authority:** `false`  
**Target D4 execution performed by this audit:** `false`

## 1. Scope and independence boundary

Issue `SzeChunYiu/ORION-paper#49` asks the ORION-04 A1 lane for an independent mathematical audit that reconstructs the logical chain leading to the 60-pattern / 78-branch cover without treating the current scripts as authority. PR #2031 independently regenerated the 60 multiplicity patterns but deliberately left the branch partition `NOT_REGENERATED` rather than tune a new program until it emitted 51 and 27.

This packet addresses that branch-reconstruction gap. The generation step uses only the mathematical premises stated in the manuscript and its parent theorem:

1. a hypothetical length-31 total-zero 5-short-free sequence has point multiplicities in `{1,2,4}`;
2. the support-`s` counts `(a1,b2,c4)` satisfy
   `a1+b2+c4=s` and `a1+2b2+4c4=31`;
3. the parent result excludes support at most 13;
4. `eta(C_5^2)=13`;
5. the projective-line local restriction may be re-derived from primitive addition modulo 5;
6. a hypothetical obstruction cannot be contained in a rank-two subgroup, because its length 31 already exceeds `eta(C_5^2)`.

`reconstruct_branch_cover_v1.py` imports none of the production generators, C engines, branch lists, fingerprints, or generator outputs. It uses its own audit-local case names. Only after the independent set has been generated does the comparison layer read `FULL_CUBE_COVER.json` and `PROJECTIVE_LINE_ATLAS.json`.

This is an independent reconstruction process, not a claim that an external human referee has reviewed the theorem. Whether repository governance chooses to count it toward the issue's reviewer requirement is a separate authority decision; this file does not self-award that status.

## 2. Primitive projective-line check

Take one projective line in `C_5^3`. Its four nonzero points can be written as `x,2x,3x,4x`. For each point, the saturation lemma leaves multiplicity in `{0,1,2,4}`. The audit enumerates all `4^4=256` local multiplicity states and, for every state, every submultiset of size 1 through 5. A submultiset `(t1,t2,t3,t4)` is rejected exactly when

` t1 + 2 t2 + 3 t3 + 4 t4 == 0 (mod 5) `.

Exactly **21** local states survive. This enumeration is from primitive `Z/5` arithmetic; it does not read the committed atlas to decide which states survive.

Two consequences follow directly from those 21 states:

- a multiplicity-four point is isolated on its projective line: no other occupied projective point can coexist with it;
- no valid line state contains two points of multiplicity at least two.

Hence all high-multiplicity points (multiplicity 2 or 4) are pairwise projectively distinct. The independently generated 21-state set is then compared with `PROJECTIVE_LINE_ATLAS.json`; the sets are equal with no missing or extra state.

## 3. The 60 multiplicity patterns

Solving the two equations gives

`b2 = 31 - s - 3 c4`,

`a1 = 2 s - 31 + 2 c4`.

Nonnegativity and support `14 <= s <= 31` produce exactly **60** patterns: **42** for supports 14--22 and **18** for supports 23--31. This agrees with PR #2031's independently derived pattern count, but the branch audit recomputes the pattern set itself rather than importing that PR.

## 4. Supports 14--22: 42 patterns become 51 branches

Let `H` be the high-multiplicity support and let its sequence mass be `M_H = 2 b2 + 4 c4`.

### Case L1: `c4 <= 2`

For every admissible support-14--22 pattern with `c4 <= 2`, direct substitution gives `M_H >= 14`. If `H` had rank at most two, all of those high-multiplicity terms would lie in a copy of `C_5^2`; because `M_H >= 14 >= eta(C_5^2)`, that subsequence would contain a nonempty zero sum of length at most five. This contradicts 5-short-freeness. Therefore `rank(H)=3` and there is one rank-three high-set branch for each such pattern.

### Case L2: `c4 >= 4`

The multiplicity-four points alone contribute mass at least `4*4=16`. If their span had rank at most two, `eta(C_5^2)=13` would again force a short zero sum inside that subsequence. Therefore the multiplicity-four set has rank three and supplies one rank-three four-set branch for each such pattern.

### Case L3: `c4 = 3`

The three multiplicity-four points contribute exactly 12 terms, one below the `eta(C_5^2)=13` threshold. Their rank is therefore a genuine unresolved split:

- rank three gives the four-set rank-three branch;
- rank two puts the three four-points in one plane. Any multiplicity-two point in that same plane would raise the plane subsequence mass from 12 to at least 14 and contradict `eta(C_5^2)=13`. Thus every doubleton is outside the plane. If no doubleton exists, at least one singleton is outside, because the entire length-31 obstruction cannot lie in a rank-two subgroup. Two independent four-points normalize the plane and one outside support point supplies the third basis direction, producing the plane-plus-outside branch.

There are exactly **9** admissible `c4=3` patterns across supports 14--22. Therefore the 42 patterns contribute one branch each plus one additional plane branch for those 9 patterns:

**42 + 9 = 51 branches.**

The important point is that `51` is a consequence of the `c4=3` rank split; it is not an input constant in the reconstruction.

## 5. Supports 23--31: 18 patterns become 27 branches

For these 18 patterns, `c4 <= 2`. Let `h = b2+c4` be the number of high-multiplicity support points and again let `M_H = 2 b2 + 4 c4`.

### Case U1: `h >= 3`, `rank(H)=3`

Three independent high points supply a basis. Because the projective-line audit established pairwise projective distinctness and `c4 <= 2`, the possible multiplicity profiles of a high basis are determined by `c4`:

- `c4=0`: `(2,2,2)`;
- `c4=1`: `(4,2,2)`;
- `c4=2`: `(4,4,2)`.

This gives one high-set rank-three branch whenever `h>=3`.

### Case U2: `rank(H)=2`

A rank-two high set lies in a copy of `C_5^2`. It is possible only when `M_H < eta(C_5^2)=13`; if `M_H >= 13`, the high subsequence already forces a short zero sum. Since `M_H` is even, the allowed rank-two cases have `M_H <= 12`.

When `h>=2` and `M_H<13`, pairwise projective distinctness gives two independent high points spanning the high plane. At least one singleton must lie outside that plane, otherwise the whole obstruction would remain rank two. This gives the high-plane-plus-singleton branch.

When `h=2`, rank three is impossible, so this is the only high-set branch. When `h>=3` and `M_H<13`, both the rank-three and rank-two cases are retained.

### Case U3: `h=1`

There is one high point. Two singleton support points extend it to a full basis, giving the one-high-plus-two-singletons branch.

### Case U4: `h=0`

All 31 support points are singletons. Three singleton support points form a full basis, giving the all-singleton branch.

Applying these rules to the 18 upper-support patterns gives **27 branches**. No branch count is supplied to the generator; it follows from the rank and `eta` tests.

## 6. Atomic count table

| support | patterns | reconstructed branches |
|---:|---:|---:|
| 14 | 4 | 5 |
| 15 | 5 | 6 |
| 16 | 6 | 7 |
| 17 | 5 | 6 |
| 18 | 5 | 6 |
| 19 | 5 | 6 |
| 20 | 4 | 5 |
| 21 | 4 | 5 |
| 22 | 4 | 5 |
| **14--22** | **42** | **51** |
| 23 | 3 | 4 |
| 24 | 3 | 5 |
| 25 | 3 | 5 |
| 26 | 2 | 4 |
| 27 | 2 | 3 |
| 28 | 2 | 3 |
| 29 | 1 | 1 |
| 30 | 1 | 1 |
| 31 | 1 | 1 |
| **23--31** | **18** | **27** |
| **total** | **60** | **78** |

## 7. Post-generation comparison

Only after the reconstruction is complete, the audit maps its own case names to the committed cover's labels and compares tuples

`(support, a1, b2, c4, branch_case)`.

The result is exact:

- generated patterns: 60; committed patterns: 60; missing 0; extra 0;
- generated branches: 78; committed branches: 78; missing 0; extra 0;
- generated projective-line states: 21; committed states: 21; missing 0; extra 0.

The comparison therefore checks the entire abstract rank/plane partition rather than only checking the published totals 51 and 27.

## 8. Hostile sensitivity controls

Four local mutations are required to fail:

1. omit one generated branch: branch count becomes **77**;
2. alter the multiplicity equation to total length 30: admissible pattern count becomes **56**;
3. delete the `c4=3` plane split: total branch count becomes **69**;
4. weaken the rank-two exclusion threshold by replacing `eta=13` with `eta=15`: two mass-14 upper patterns acquire spurious plane branches and the total becomes **80**.

All four are rejected by the comparison. These are structural cover controls. The separate A1 mutation that forges a zero-solution digest belongs to the survivor/certificate layer and is deliberately not claimed here.

## 9. What this closes, and what it does not

This packet closes the **previously unregenerated 78-branch mathematical-cover reconstruction** to machine-checkable local strength and provides a proof narrative for why the 51/27 partition follows from the stated lemmas.

It does **not** independently rerun the target zero-survivor computation, validate every lower-level search certificate, or test the forged-zero-solution-digest mutation. It also does not create novelty, priority, venue, journal, external-replication, or human-peer-review authority. Those boundaries remain explicit rather than being inferred from a successful local audit.

The intended integration is complementary to PR #2031: that PR supplies independent pattern regeneration and the priority audit; this packet supplies the branch-cover reconstruction it intentionally left open.
