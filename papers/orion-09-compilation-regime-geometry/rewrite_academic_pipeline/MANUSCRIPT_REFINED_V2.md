# Exact Normal Forms Do Not Imply Simple or Transferable Compilation Boundaries

## Abstract

Structural compiler claims often collapse three questions: how large an exact search family must be, whether incumbent-optimal inputs have a compact certificate, and whether that certificate transfers beyond the domain in which it was found. We separate these questions across four exact compiler families.

A TARE-derived grammar has an all-size support-two normal form in an explicit objective cone, even though successive hostile witnesses keep enlarging its closed-form trade vocabulary. A rank-2 shared-Tag grammar tightens from a valid support-five certificate to intrinsic support one. SixLCU admits an exact low-order incumbent boundary although corrective witnesses can have larger global structure. Stabilizer-state preparation shows the opposite failure mode. A natural feature vocabulary has an irreducible floor of 43 errors among 1,146 cases. An expanded 127-feature vocabulary contains an exact separator on the frozen \(n\le3\) domain, and exhaustive search proves its minimum size is four. On unseen \(n=4\), however, the separator makes 32 errors among 120 cases, equal to a parent-cell baseline, while a different lattice-derived parent makes 3.

The result is a cross-family separation theorem in empirical form: exact search compression, compact recognizability, and out-of-domain validity are independent properties. The reusable contribution is a falsifiable regime-mapping protocol, not a universal claim that compiler families possess simple phase boundaries.

## 1. The structural question behind a benchmark

A benchmark asks which compiler is cheaper on a panel. A structural analysis asks:

- When is the incumbent already exact?
- Which transformations are required outside that region?
- What restricted search family is sufficient for an exact optimum?
- Can regime membership be recognized without solving the full optimization again?
- Does the rule survive a frozen change of size or objective?

These questions form a regime map. The map is useful only when each component can fail without being silently repaired into another claim.

## 2. Three independent axes

We distinguish three axes.

**Normal-form complexity** is the smallest proved search or support family containing an optimum.

**Boundary complexity** is the smallest declared feature description that exactly separates incumbent-exact from non-exact inputs on a domain.

**Transfer** asks whether the same description remains valid under a frozen change of size, grammar, or objective.

A small normal form does not imply a simple boundary. A simple boundary does not imply a small witness. Exact finite-domain separation does not imply transfer.

## 3. TARE: simple support, incomplete explanation

For the R6M grammar, support two is sufficient for every admitted instance under the unit objective. Repeated hostile tests refute several proposed finite trade vocabularies and expose new hybrid configurations, but the support theorem remains intact.

The distinction is decisive. The optimizer can be searched inside a small exact family even while the current formula explaining when each trade is profitable remains incomplete.

Objective dependence is explicit. The support-two proof holds throughout
\[
t_c\ge2t_r,\qquad t_{nc}\ge2t_r.
\]
A registered objective outside this cone contains a support-three witness. The normal form belongs to a grammar–objective pair, not to the grammar alone.

## 4. Shared-Tag grammar: a loose certificate tightened to one

A semantics-derived certificate first bounds support by five. New transformations reduce the all-size ceiling through four, three, and two to one. A lower witness excludes zero support, establishing
\[
\kappa=1.
\]

The earlier rank-like certificate was valid but not intrinsic. It localized a route to a proof without measuring the final complexity. This family shows why the first finite bound should be treated as a discovery scaffold rather than a conclusion about optimal support.

## 5. SixLCU: boundary arity is not witness arity

SixLCU has an exact incumbent boundary described by a low-order predicate. The predicate determines whether donor and unrestricted cost agree for every admitted size, even though the corrective optimum outside the region may use larger global structure.

The result separates the size of a certificate from the size of what it certifies. Recognizing a regime can be simpler than constructing the optimal witness.

## 6. Stabilizer-state preparation: two honest answers

The first answer is negative. In a frozen natural feature vocabulary, twelve cells mix incumbent-exact and non-exact cases. The resulting irreducible floor is 43 errors among 1,146 instances. No classifier using only that vocabulary can be exact.

The second answer is a bounded revival. An expanded vocabulary contains 127 features. Exhaustive search rejects every one-, two-, and three-feature subset, then finds a four-feature subset with zero mixed cells on \(n\le3\). The minimum separator complexity in the expanded vocabulary is exactly four.

These answers are compatible. The first vocabulary is information-insufficient. The second is sufficient on the finite domain.

The proposed mechanism for the four-feature law does not survive its own ablations. Two of three claimed explanatory blocks are independently sufficient, and the minimum separator contains no coordinate from one block. The paper therefore reports exact separation without inflating it into the discarded mechanism story.

## 7. Prospective failure at \(n=4\)

On unseen \(n=4\), the four-feature separator makes 32 errors among 120 cases. A parent-cell lookup baseline makes the same number, and shuffle calibration does not distinguish the rule from the registered null. A different lattice-derived parent makes 3 errors.

The small-domain separator is therefore exact but non-transferable. The outcome rules out the inference that minimum finite-domain separator complexity identifies a stable law.

## 8. What transfers across families

The answers differ, but the workflow transfers:

1. freeze the incumbent and exact referee;
2. record exact counterexamples rather than smoothing them away;
3. prove a sufficient search family separately from a classifier;
4. identify boundary complexity relative to a declared vocabulary;
5. test objective and size changes prospectively;
6. retain finite-domain exactness and transfer failure as separate outcomes.

This workflow treats negative components as structural information. “No exact predicate in this vocabulary” and “exact here, not there” are both legitimate parts of a regime map.

## 9. Claim boundaries

The study does not establish that all compiler families have low-dimensional geometry. It does not infer production frequency from exact finite grammars. It does not equate structural objective cost with wall-clock performance or quantum advantage.

The stabilizer separator is exact only on the frozen \(n\le3\) domain. The TARE trade vocabulary is not yet proved complete. The shared-Tag support-one theorem and SixLCU boundary theorem apply only to their declared grammars and objectives.

## 10. Conclusion

Exact search compression, compact regime recognition, and out-of-domain validity are separate properties. TARE combines a simple normal form with an incomplete trade explanation; the shared-Tag grammar has intrinsic support one; SixLCU has a compact boundary despite global witnesses; and stabilizer-state preparation has an exact four-feature small-domain separator that fails at the next size. The strongest cross-family result is therefore methodological: a compiler regime map should record which compression is proved, which explanation remains open, and which apparent law does not transfer.
