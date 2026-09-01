# ORION-04 A1 — independent mathematical review worksheet V1

**Purpose:** make the remaining human mathematical proof audit in
`SzeChunYiu/ORION-paper#49` small, explicit and falsifiable. This worksheet is
**not** a completed review and does not check that issue box. A reviewer must fill
it from the stated mathematical premises rather than accepting program output as
an authority.

**Target:** the finite-cover part of the claimed upper obstruction for
`D_4(C_5^3)=30`: reduction to 60 admissible multiplicity patterns and an exhaustive
78-case rank/plane cover. The separate zero-survivor/certificate layer remains a
separate obligation.

## Review discipline

For each item below, the reviewer should record `PASS`, `FAIL`, or
`CANNOT_CHECK`, give a short derivation, and cite the mathematical source used.
Counts printed by a generator are not a derivation. If a numerical census is used
as a convenience, the reviewer must state why the enumerated set equals the
mathematically intended set.

A single `FAIL` or unresolved load-bearing `CANNOT_CHECK` keeps the theorem audit
open. No majority vote or deletion of the failed branch is permitted.

## Dependency DAG

```text
P0  parent corridor: support >= 14
 |
 +--> P1 multiplicities in {1,2,4}
 |     a1+b2+c4=s, a1+2b2+4c4=31
 |       |
 |       +--> P2 exactly 60 patterns on s=14..31
 |              |-- 42 on s=14..22
 |              `-- 18 on s=23..31
 |
 +--> L1 projective-line restriction
 |     exactly 21 admissible line states
 |     => multiplicity-4 point isolated on a line
 |     => two multiplicity>=2 points are not projectively collinear
 |
 +--> L2 eta(C5^2)=13
       |
       +--> BLOW supports 14..22
       |     c4<=2: high mass >=14 => high set rank 3
       |     c4>=4: four-set mass >=16 => four-set rank 3
       |     c4=3: rank-3 OR rank-2 plane + outside point
       |     => 51 branches
       |
       `--> BUP supports 23..31
             classify high-set rank/size and eta-eligible plane cases
             rank3 / rank2+outside singleton / one-high+2 singletons /
             all-singleton basis
             => 27 branches

P2 + L1 + BLOW + BUP
       |
       `--> C0 exact cover: 60 patterns, 78 branches, no omitted pattern/case
```

## A. Parent/corridor binding

- [ ] **A1.1** Verify from the parent theorem/lemma that every target candidate
  entering this cover has support at least 14.
- [ ] **A1.2** Verify no later case assumes support >=14 for a reason circularly
  dependent on the 78-branch computation.

Reviewer derivation / source:

> _blank_

## B. Multiplicity equations and 60-pattern census

For nonnegative integers `(a1,b2,c4)`, independently solve

`a1 + b2 + c4 = s`,

`a1 + 2 b2 + 4 c4 = 31`,

for every `14 <= s <= 31`.

- [ ] **B1.1** Derive why only multiplicities `1,2,4` remain in this corridor.
- [ ] **B1.2** Verify every nonnegative solution is admissible at this reduction
  stage and no additional solution is silently filtered.
- [ ] **B1.3** Count **42** solutions with `14 <= s <= 22`.
- [ ] **B1.4** Count **18** solutions with `23 <= s <= 31`.
- [ ] **B1.5** Confirm total **60**.

Useful hand derivation: eliminating `a1` gives

`b2 + 3 c4 = 31-s`,

so for fixed support `s`, `c4` ranges from `0` through
`floor((31-s)/3)` and `b2=31-s-3c4`, with
`a1=s-b2-c4` required nonnegative. The reviewer should check the endpoint
conditions rather than trusting this sentence.

Reviewer table / derivation:

> _blank_

## C. Projective-line restriction

On a projective line through a nonzero point `x`, the four scalar positions are
`x,2x,3x,4x`. For each position allow only the remaining multiplicities
`0,1,2,4`. Independently check which occupancy/multiplicity states contain **no**
nonempty zero-sum submultiset of length at most five.

- [ ] **C1.1** Explain why checking the four scalar positions captures every
  projective-line collision relevant to this reduction.
- [ ] **C1.2** Reconstruct the admissible state set and confirm its cardinality is
  **21**.
- [ ] **C1.3** Deduce that a multiplicity-4 point cannot share such a line with
  another occupied point.
- [ ] **C1.4** Deduce that two multiplicity>=2 points cannot be projectively
  collinear.
- [ ] **C1.5** State precisely what these consequences do **not** prove (for
  example, they do not by themselves force three high points to have rank 3).

Reviewer derivation:

> _blank_

## D. Rank-2 zero-sum threshold

- [ ] **D1.1** Verify the exact external theorem used here is
  `eta(C_5^2)=13` with the convention needed by this proof.
- [ ] **D1.2** Confirm that a subsequence of mass at least 13/14 is being compared
  with the theorem using the correct inclusive/exclusive convention; record the
  exact threshold in words.
- [ ] **D1.3** Verify every use of the threshold concerns a subsequence confined to
  a rank-2 subgroup/plane of the correct group.

Reviewer theorem citation / convention check:

> _blank_

## E. Supports 14–22: 51 branches

Let the **high set** be the support points of multiplicity 2 or 4, with high
mass `M=2 b2 + 4 c4`.

- [ ] **E1.1 (`c4<=2`)** For every one of the 42 lower-support patterns with
  `c4<=2`, verify `M` is large enough that a rank<=2 high set contradicts the
  rank-2 short-zero threshold. Conclude the high set has rank 3.
- [ ] **E1.2 (`c4>=4`)** Verify four multiplicity-4 points contribute mass at
  least 16; use the projective-line restriction and rank-2 threshold to justify
  the required rank-3 branch.
- [ ] **E1.3 (`c4=3`)** Verify exactly **9** lower-support patterns have `c4=3`.
- [ ] **E1.4** For each `c4=3` pattern, justify the split: the three four-points
  either have rank 3, or lie in a rank-2 plane.
- [ ] **E1.5** In the rank-2 case, show a multiplicity-2 point cannot also lie in
  that plane without crossing the rank-2 short-zero threshold.
- [ ] **E1.6** Explain why an occupied point outside the plane exists and supplies
  the third direction needed by the branch.
- [ ] **E1.7** Count `42 + 9 = 51` lower-support branches and verify the split does
  not omit or double-count a pattern/case.

Reviewer derivation:

> _blank_

## F. Supports 23–31: 27 branches

Let `h=b2+c4` be the number of high points and `M=2b2+4c4` their mass.

- [ ] **F1.1** Verify the 18 upper-support patterns have the high-point
  multiplicity restrictions used by the case split (including the bound on
  `c4`).
- [ ] **F1.2 (`h>=3`)** Justify the rank-3 branch; where a rank-2 high plane is
  still compatible with the eta threshold, justify the separate plane + outside
  singleton branch.
- [ ] **F1.3 (`h=2`)** Use projective distinctness to justify rank 2 and the
  required outside singleton/basis completion.
- [ ] **F1.4 (`h=1`)** Justify the one-high + two-singleton basis case.
- [ ] **F1.5 (`h=0`)** Justify the all-singleton full-basis case.
- [ ] **F1.6** Check that eta removes every upper rank-2 case whose high mass is
  too large, and only those cases.
- [ ] **F1.7** Independently count exactly **27** upper-support branches.

Reviewer branch table / derivation:

> _blank_

## G. Exact-cover audit

- [ ] **G1.1** Construct a reviewer-owned table keyed by
  `(support,a1,b2,c4,mathematical case)` rather than production branch labels.
- [ ] **G1.2** Verify all 60 multiplicity patterns appear at least once.
- [ ] **G1.3** Verify case splits are mutually exclusive where intended and
  collectively exhaustive.
- [ ] **G1.4** Confirm total branch count **78 = 51 + 27**.
- [ ] **G1.5** If comparing with the committed cover, do the comparison only
  **after** the reviewer-owned table is complete; report missing and extra tuples,
  not only counts.

Reviewer result:

> _blank_

## H. Explicitly outside this worksheet

The following remain separate obligations and **must not** be inferred from a
clean 60/78 review:

- [ ] every one of the 78 mathematical branches has zero admissible survivor;
- [ ] every excluded branch has the independently required proof/certificate;
- [ ] certificate replay is independently checked;
- [ ] one-shot authorization/custody requirements are satisfied;
- [ ] the final archived theorem packet binds source, inputs, certificates,
  outputs and hashes.

## Reviewer disposition

Reviewer identity / affiliation (if applicable): _blank_

Review date: _blank_

Disposition: `PASS / FAIL / CANNOT_CHECK` — _blank_

Load-bearing unresolved items: _blank_

A `PASS` here can support only the issue #49 **independent mathematical proof
 audit of the 60-pattern/78-branch cover**. It does not by itself establish the
zero-survivor/certificate requirement or the final exact theorem.
