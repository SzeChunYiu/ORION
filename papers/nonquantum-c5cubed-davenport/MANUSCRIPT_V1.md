# A One-Unit Generalized-Davenport Corridor in `C_5^3`

## Saturation defects and the unresolved `D_4` boundary

**Non-quantum paper — rigorous manuscript draft**

## Abstract

Let `D_k(G)` denote the least length forcing `k` pairwise disjoint nonempty zero-sum subsequences. For the elementary abelian group `G=C_5^3`, the early generalized Davenport constants determine an unusually narrow tail problem. Combining exact registered values `D_2(C_5^3)=20` and `D_3(C_5^3)=25` with the Freeze–Schmid recurrence and lower bound yields, for every `k>=4`,

`5k+10 <= D_k(C_5^3) <= 5k+11`.

Thus every later constant lies in a corridor of width one. Moreover, if the single unresolved value satisfies `D_4(C_5^3)=30`, then the lower line propagates exactly and

`D_k(C_5^3)=5k+10`

for every `k>=2`. The remaining decision can be phrased as a short-zero-sum obstruction. A hypothetical upper-line extremal produces a length-31 total-zero sequence with no nonempty zero-sum subsequence of length at most five. We prove a general saturation-defect lemma for odd-prime elementary abelian groups: if a saturated `p`-short-free sequence contains a nonzero point `x` with multiplicity `m<p`, saturation forces a witness `x^m R` with `|R|<=p-1-m`, `x` absent from `R`, and `sigma(R)=-(m+1)x`; in particular multiplicity `p-2` is impossible. For `C_5^3`, this removes multiplicity three and sharply constrains all low-multiplicity support points. Independent exact local replay closes support strata through ten, while a larger existing computational frontier, with independent internal state-engine replays but explicitly pending external mathematical replay, eliminates every support stratum through 22. Consequently any unresolved length-31 obstruction must have support at least 23 according to that bounded computation. The exact `D_4` value remains open. We therefore present the width-one tail theorem and saturation-defect structure as established mathematics, the support-23 frontier as bounded computational evidence, and `31 in C_0(C_5^3)` as the decisive unsolved gate. This distinction is essential: polishing a near-solution cannot replace the final combinatorial argument.

## 1. Introduction

Generalized Davenport constants measure how long a sequence over a finite abelian group must be before several disjoint zero-sum subsequences are unavoidable. Freeze and Schmid developed much of the general structure, including recurrence inequalities and eventual linearity. Rank-two groups admit particularly clean formulas. Rank at least three is more delicate: the expected linear behavior can begin late, and small generalized constants can depart from the eventual progression.

The group `C_5^3` is a compact test case. Its exponent is five and rank is three. The registered exact values

`D_2=20`,

`D_3=25`

already show that the sequence is not following the naive rank-two lower line at `k=2,3`. Yet the increment from `D_2` to `D_3` is exactly the exponent. This raises a precise question:

> Has the eventual step-five regime begun by `k=2`, or is there one final defect at `D_4`?

The answer is controlled by a single bit. Current donor inequalities give

`30 <= D_4(C_5^3) <= 31`.

If `D_4=30`, every later constant is forced onto the line `5k+10`. If `D_4=31`, the lower-line onset has not yet been established and the recurrence alone does not determine the later exact tail.

A second formulation converts the `D_4` question into a structural zero-sum problem. Under the registered extremal reduction, an upper-line obstruction supplies a sequence `S` of length 31 with

`|S|=31`,

`sigma(S)=0`,

and no nonempty zero-sum subsequence of length at most five.

The paper develops two complementary tools around this object. First, a symbolic saturation-defect lemma constrains every low-multiplicity support point. Second, exact finite searches, organized by multiplicity and rank rather than by a blind 31-term search, remove a large initial region of the obstruction space.

The main claim boundary is equally important. The general recurrence and lower bound are donor mathematics. The current support-at-least-23 frontier is computational evidence whose repository authority explicitly remains below theorem status pending external replay. Most importantly, the paper does **not** claim exact `D_4`. That open bit is the difference between a strong specialist manuscript and the top-tier combinatorial result we ultimately seek.

### 1.1 Contributions

**N1 — width-one tail theorem.** For every `k>=4`, `D_k(C_5^3)` lies between `5k+10` and `5k+11`.

**N2 — conditional exact tail.** If `D_4=30`, then `D_k=5k+10` for every `k>=2`.

**N3 — odd-prime saturation-defect lemma.** Saturation forces a bounded local defect certificate at every support point below full multiplicity and excludes multiplicity `p-2`.

**N4 — exact low-support elimination.** For the length-31 total-zero 5-short-free obstruction, the symbolic lemma plus isolated dual exact replay eliminates support at most ten.

**N5 — larger bounded computational frontier.** A separately recorded, rank-normalized family of independent exact state-engine replays eliminates support strata 11 through 22 as bounded computational evidence, placing any surviving obstruction at support at least 23 if those replay records are accepted. This frontier is not promoted to theorem authority in the present manuscript.

## 2. Generalized Davenport notation and donor results

For a finite abelian group `G`, let `D_k(G)` be the least integer `ell` such that every sequence of length at least `ell` contains `k` pairwise disjoint nonempty zero-sum subsequences.

The paper uses two Freeze–Schmid results as donors.

First, their lower-bound machinery specialized to `C_5^3` gives

`D_k(C_5^3) >= 5k+10`

for the range used here.

Second, their Proposition 3.1(3) states, in the notation `s_{<=l}(G)` for the least length forcing a zero sum of length at most `l`, that

`D_{k+1}(G) <= max{D_k(G)+l, s_{<=l}(G)-1}`.

An earlier ORION draft mistakenly treated a recurrence of this form as internal novelty; the repository's hostile prior-art audit killed that claim and corrected the proposition number and notation. We preserve that correction here.

For `C_5^3`, the classical short-zero-sum threshold at `l=5` is

`s_{<=5}(C_5^3)=33`.

The registered exact early constants are

`D_2(C_5^3)=20`,

`D_3(C_5^3)=25`,

and the registered short-zero-sum computation gives

`s_{<=6}(C_5^3)=24`.

The novelty status of the exact early constants remains subject to final primary-source review; the recurrence itself receives zero novelty credit.

## 3. The one-unit tail corridor

Using the `l=6` recurrence at `k=3`,

`D_4 <= max{D_3+6, s_{<=6}-1}`

`     = max{31,23}`

`     =31`.

The donor lower bound gives

`D_4>=30`.

Hence

`D_4 in {30,31}`.

**Theorem 1 (width-one generalized-Davenport corridor).** For every integer `k>=4`,

`5k+10 <= D_k(C_5^3) <= 5k+11`.

**Proof.** The lower bound is the donor specialization. The base upper bound is `D_4<=31=5*4+11`. Apply Proposition 3.1(3) with `l=5` and `s_{<=5}=33`:

`D_{k+1} <= max{D_k+5,32}`.

If `D_k<=5k+11` for `k>=4`, then

`D_k+5 <= 5(k+1)+11`,

and also

`32 <= 5(k+1)+11`.

Induction proves the upper line. ∎

The significance of the theorem is not the recurrence; it is the reduction of the entire tail to one bit at the first unresolved constant.

## 4. If `D_4=30`, the exact tail closes

**Theorem 2 (conditional exact lower line).** If

`D_4(C_5^3)=30`,

then for every `k>=2`,

`D_k(C_5^3)=5k+10`.

**Proof.** The cases `k=2,3` are the registered exact values and `k=4` is the hypothesis. Suppose the equality holds at some `k>=4`. The same `l=5` recurrence gives

`D_{k+1} <= max{5k+10+5,32}`

`          =5(k+1)+10`.

The donor lower bound gives the reverse inequality. ∎

No converse is inferred from `D_4=31`. An upper-line value at `k=4` does not, from this recurrence alone, force a permanent upper-line tail.

## 5. The `D_4` obstruction as a total-zero short-free sequence

The registered extremal reduction shows that an upper-line `D_4=31` obstruction would yield a sequence `S` over `C_5^3` with

`|S|=31`,

`sigma(S)=0`,

and no nonempty zero-sum subsequence of length at most five.

Call such a sequence **5-short-free**.

No point can have multiplicity five: five equal copies already sum to zero. Thus every support multiplicity is at most four.

The obstruction formulation connects to the `C_0(G)` framework for short zero sums. Existing literature already places `C_0(C_5^3)` in a narrow interval near `eta(C_5^3)`; that localization is donor mathematics and is not claimed here. The decisive question is specifically whether the length 31 total-zero case can exist.

## 6. Saturation and the defect lemma

A short-free sequence is **saturated** if appending any nonzero group element creates a zero-sum subsequence of length at most the exponent.

For a nonzero `x`, appending `x` creates a new short zero sum exactly when a subsequence `T|S` of length at most `p-1` sums to `-x`.

**Theorem 3 (saturation-defect lemma).** Let `p` be an odd prime and `S` a saturated `p`-short-free sequence over an elementary abelian exponent-`p` group. Suppose a nonzero support point `x` has multiplicity `m<p`. Then saturation forces

`T=x^m R`,

where

`|R|<=p-1-m`,

`x` does not occur in `R`,

and

`sigma(R)=-(m+1)x`.

**Proof.** Saturation provides `T|S`, `|T|<=p-1`, with `sigma(T)=-x`. If `T` used at most `m-1` copies of `x`, one remaining copy already present in `S` could be added to `T`, producing a zero-sum subsequence of `S` of length at most `p`, contradiction. Hence `T` uses all `m` copies. Writing `T=x^m R` gives the length and support restrictions and

`m x + sigma(R)=-x`. ∎

**Corollary 4.** Multiplicity `p-2` is impossible.

For `m=p-2`, `R` has size at most one and must sum to `x`; it can be neither empty nor a distinct point, contradiction.

For `p=5`, multiplicity three is therefore impossible in every saturated obstruction.

The remaining low-multiplicity certificates are explicit:

- multiplicity two: `|R|<=2`, `sigma(R)=2x`;
- multiplicity one: `|R|<=3`, `sigma(R)=3x`.

These identities are a candidate source of a reusable global obstruction theorem because low-multiplicity points are algebraically generated by very small subsets of the remaining sequence.

## 7. Why a support greater than eight obstruction is saturated

If a length-31 short-free total-zero sequence were extendable by one nonzero point while remaining 5-short-free, the result would be a length-32 short-free sequence. The donor Property-C classification for the extremal threshold forces such a length-32 sequence into a highly repeated support-eight form.

A candidate with support greater than eight cannot be a subsequence of such a support-eight extremal. Hence every unresolved obstruction in the larger-support branch is saturated and Theorem 3 applies.

This converts a global extremal problem into a multiplicity grammar.

## 8. Multiplicity grammar

For a saturated length-31 obstruction, let

- `a` be the number of support points of multiplicity one;
- `b` the number of support points of multiplicity two;
- `c` the number of support points of multiplicity four.

Multiplicity three is excluded. If support size is `s`, then

`a+b+c=s`,

`a+2b+4c=31`.

Equivalently,

`b+3c=31-s`,

`a=2s-31+2c`.

A multiplicity-four point cannot share its projective line with another support point; otherwise a zero sum of length at most five can be formed from four copies and a scalar mate. Moreover, sufficiently many high-multiplicity terms cannot remain in a rank-two subgroup because `eta(C_5^2)=13`. These observations justify the rank-normalized exact searches used below.

## 9. Exact support-at-most-ten exclusion

Support eight and nine are first reduced symbolically and then replayed by two independently represented exact state engines. The saturation-defect lemma eliminates every multiplicity-three branch.

At support ten, the length/support equations leave exactly two patterns:

`1 2^3 4^6`,

`1^3 4^7`.

Four multiplicity-four points force rank three, allowing a basis normalization. Two independently implemented exact reachability engines exhaust the normalized candidates. Both return zero solutions for both patterns. The complete registered row counts are retained in the reproducibility record.

**Theorem 5 (bounded support-ten exclusion).** Every length-31 total-zero 5-short-free sequence over `C_5^3`, if one exists, has support at least eleven.

Unlike the larger frontier below, this theorem is already bound through the signed M2/M3 source, independent generic and native campaign records used by the programme.

## 10. The current computational frontier reaches support 23

A subsequent bounded computation extends the same principle through support 22. It is not a blind enumeration of arbitrary 31-term sequences. Each support stratum is reduced by the multiplicity equations, projective-line exclusion and rank-two threshold; different basis normalizations are used depending on which high-multiplicity stratum is forced to span rank three. Independent exact state representations replay the registered finite searches.

The current receipt reports zero solutions for every support stratum 8 through 22 and states the bounded conclusion:

> Any length-31 total-zero sequence over `C_5^3` with no nonempty zero-sum subsequence of length at most five has support at least 23.

However, that same receipt deliberately records

`theorem_authority=false`

and

`external_replay_required=true`.

We preserve that status. In this manuscript the support-23 statement is **computational frontier evidence**, not an internally promoted theorem.

### 10.1 The next support stratum

At support 23 the multiplicity equations leave three patterns:

`1^15 2^8`,

`1^17 2^5 4`,

`1^19 2^2 4^2`.

Exploratory post-outcome work has found complete rank-normalization branches for these patterns and no survivor in the fast exact engine, but the heaviest branches have not yet received the fully independent replay required by this programme's scientific-authority rules. They are therefore omitted from the theorem list and retained only as a next-step research direction.

## 11. Relation to prior work

Freeze and Schmid own the generalized-Davenport recurrence, lower-bound framework and eventual-linearity setting used here. The broader `C_0(G)` literature already localizes possible short-zero-sum obstructions near `eta(G)` and includes a specific interval for `C_5^3`. Property C and exact short-zero-sum constants are likewise donor context.

Inverse generalized-Davenport problems remain active. Recent work has made progress for rank-two groups and elementary 2-groups, emphasizing how strongly extremal structure depends on rank and exponent. No exact parent for `D_4(C_5^3)` surfaced in the current hostile search, but “not found” is not a novelty certificate.

The potential residual contribution of a final paper depends on how far the last bit is closed:

- exact `D_4=30` would immediately close the entire lower-line tail by Theorem 2;
- an explicit `D_4=31` obstruction would decide the constant but would not by itself determine the exact later tail;
- a reusable symbolic impossibility theorem for the saturation-defect grammar could be more valuable than continuing one support stratum at a time.

## 12. Reproducibility

The width-one corridor is recorded by source, independent generic and native routes and evaluated through large finite `k` only as corroboration of the human induction. The saturation-defect result is separately bound, as are the support-eight/nine and support-ten exact searches. The support-23 frontier preserves its lower authority class and the identities of its independent state-engine replays.

`papers/verify_five_theory_upgrades.py` checks the authority boundaries rather than upgrading them: exact `D_4` and `C_0(31)` must remain false, and the support-23 frontier must retain `external_replay_required=true`.

A true top-tier submission should add an independently auditable proof/replay package for the final obstruction theorem and archive the exact submission commit.

## 13. Limitations

1. D_4(C_5^3) remains unresolved between 30 and 31.
2. `31 in C_0(C_5^3)` is not proved.
3. The width-one recurrence and lower bound are donor mathematics; the paper's value is their exact interaction with the early constants and the unresolved boundary.
4. The support-23 frontier is bounded computational evidence, not promoted theorem authority in the current repository.
5. Much of the finite support elimination was discovered before the formal publication wave and is not prospective evidence.
6. Author-side “not found” literature searches do not establish priority.

## 14. Discussion

The current state is unusually informative despite the single open bit. Every generalized Davenport constant from `k=4` onward lies on one of two adjacent lines. A lower-line `D_4` immediately collapses the uncertainty for the whole tail. The remaining obstruction is therefore not “compute more `D_k` values” but understand one extremal 31-term total-zero sequence.

The saturation-defect lemma provides a local grammar for that hypothetical object. Every singleton and double point must be explained by a tiny complementary subset; multiplicity three disappears; multiplicity-four points are projectively isolated. The computational frontier shows that combining these rules with exact subset-sum reachability is already strong enough to eliminate all low-support realizations through 22. The scientific challenge is to convert that accumulation into a global incompatibility.

This is the appropriate top-tier gate. JCTA- or Combinatorica-level positioning should rest on exact `D_4`, a reusable support-obstruction theorem, or another conceptual result of comparable force. Additional prose, more recurrence rows or one more bounded support stratum would not meet that criterion.

## 15. Conclusion

The generalized Davenport sequence of `C_5^3` is confined to a one-unit corridor after `k=3`, and one unresolved constant controls whether the lower-line arithmetic progression is already exact forever. Saturation turns the `D_4` obstruction into a highly constrained local defect system, and exact computation rules out a large low-support region. The final mathematical question remains stark: either construct the length-31 obstruction or prove it cannot exist. Until that bit is resolved, the manuscript is a rigorous account of a nearly closed extremal problem, not a completed top-tier theorem.

## Selected references

- M. Freeze and W. A. Schmid, _Remarks on a generalization of the Davenport constant_, Discrete Mathematics 310, 3373–3389 (2010), arXiv:0905.4248.
- Literature on `C_0(G)` and short zero sums, including the result localizing `C_0(C_5^3)` to the final five lengths below `eta(C_5^3)`, is a required donor in the final bibliography.
- Current inverse generalized-Davenport work on rank-two groups and elementary 2-groups is included as neighboring, not subsuming, literature.

---

## Publication decision record

**Stretch targets:** `Journal of Combinatorial Theory, Series A` and `Combinatorica`. JCTA's current author guidance expects a solution or significant step on an important open problem, a new proof technique, or another substantial combinatorial advance.  
**Current honest status:** `RIGOROUS_SPECIALIST_MANUSCRIPT__TOP_TIER_GATE_NOT_MET`.  
**Blocking reason:** exact `D_4(C_5^3)` or a reusable symbolic obstruction theorem is still missing; the support-23 computation is explicitly not theorem-authority evidence.  
**Do not waste effort on:** extra recurrence rows, cosmetic prose, or support-by-support computation that does not change the conceptual obstruction.  
**Minimum decisive closure:** prove `31 in C_0(C_5^3)` (forcing `D_4=30` and the exact tail), construct a valid upper-line extremal (`D_4=31`), or prove a reusable global incompatibility theorem for the saturation-defect grammar.
