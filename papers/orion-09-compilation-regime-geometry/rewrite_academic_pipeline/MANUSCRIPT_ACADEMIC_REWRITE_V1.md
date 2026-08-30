# Compilation Regime Geometry: Exactness, Search Complexity, and Recognizability Across Compiler Families

## Abstract

Compiler benchmarks report which method is cheaper on tested inputs. A regime map asks a structural question: where is a simple incumbent already exact, which transformations leave that region, how large an exact search family is sufficient, and can the regions be recognized without rerunning the optimizer? We develop compilation regime geometry as a falsifiable mapping programme and compare its components across four exact compiler families.

The results show that the components vary independently. For a TARE-derived grammar, support two is sufficient for every instance in an explicit objective cone, although the closed-form vocabulary of profitable trades remains incomplete. In a rank-2 shared-Tag grammar, successive proofs tighten a valid support-five bound to the intrinsic all-size value one. In SixLCU, donor exactness is characterized by a low-order predicate even though optimal witnesses can have larger global structure. In stabilizer-state preparation, an initial natural feature vocabulary has an irreducible error floor of 43 among 1,146 cases. An expanded 127-feature vocabulary admits an exact four-feature separator on the frozen \(n\le3\) domain, and exhaustive search proves that no one-, two-, or three-feature separator suffices. That separator does not transfer to unseen \(n=4\): its 32 errors among 120 cases match a parent-cell baseline, while a different lattice-derived parent makes only 3 errors.

The cross-family conclusion is asymmetric. The mapping questions transfer; simple answers do not. Exact normal forms, compact boundary certificates, and out-of-domain laws are distinct scientific objects. Regime geometry is therefore useful precisely when it records both provable compression and the structural complexity that survives.

## 1. Introduction

A compiler benchmark gives an ordering on a finite panel. It does not explain when the incumbent is exact, why a more expensive method helps, or whether the observed boundary persists beyond the tested inputs.

A regime map decomposes that explanation into five components:

1. an incumbent-exact region;
2. exact witness classes that leave it;
3. a sufficient or intrinsic search normal form;
4. a structural classifier or cost rule;
5. prospective validation on frozen new inputs.

These components should not be collapsed. A search normal form can remain exact after a proposed classifier is refuted. A compact classifier can be exact on a finite domain but fail on a larger one. A donor region can have a low-order certificate even when its optimal witness is global.

We study these distinctions across TARE/R6M, a shared-Tag rank-2 grammar, SixLCU, and stabilizer-state preparation. The goal is not a universal phase-diagram theorem. It is an evidence discipline for turning exact optimization into structural claims that can fail separately.

## 2. Constructing a regime map

### 2.1 Incumbent region

For a frozen grammar and objective, the incumbent region contains only inputs on which exact equality with the unrestricted referee is established. A tie does not create a new method, and a finite panel does not become an all-instance theorem without a proof.

### 2.2 Trade discovery

A proposed restricted family is frozen before hostile evaluation. A strict exact-referee gap becomes a counterexample and a new trade class. Later repairs must continue to cover earlier witnesses.

### 2.3 Search normal form

A support or search bound is promoted only after finite local checks are composed into an all-size argument. A first valid bound is not assumed tight. The intrinsic support number is the smallest bound for which sufficiency and a matching necessity witness are both established.

### 2.4 Recognizability

A structural predicate is evaluated relative to a declared feature vocabulary. Zero finite-domain error establishes exactness on that domain. It does not establish transfer to a larger domain unless the rule is proved or prospectively confirmed there.

### 2.5 Objective indexing

A geometry belongs to a grammar–objective pair. Reweighting frame, restoration, routing, or tag costs can change profitable trades and required support. Transfer across objectives therefore needs its own theorem or counterexample search.

## 3. TARE: exact support with an evolving trade vocabulary

For the frozen R6M support-count objective, every admitted instance has an exact optimum with frame support at most two. Later counterexamples repeatedly enlarge the vocabulary needed to describe profitable trade configurations, but none refutes the support-two theorem.

This separation is important. The normal-form layer is exact; the explanation layer remains open. Several finite classifier repairs reach zero error on their registered panels and are then refuted by new hybrid witnesses. The correct disposition is not that the support theorem failed, but that the current closed-form trade vocabulary is incomplete.

Objective reweighting identifies a theorem-valid cone. Support at most two is sufficient for every instance when
\[
t_c\ge2t_r
\qquad\text{and}\qquad
t_{nc}\ge2t_r,
\]
where \(t_c\) and \(t_{nc}\) are central and noncentral frame coefficients and \(t_r\) is the restoration coefficient. A registered reweighted objective outside the cone contains a support-three witness. Support-two exactness is therefore not objective-free.

## 4. Shared-Tag rank-2 grammar: valid bound versus intrinsic bound

An early semantics-derived argument gives an all-size support ceiling of five. A proof ladder then tightens the ceiling through four, three, and two to one.

The final result shows that every instance in the declared grammar has an exact optimum with support at most one. Exact lower evidence rules out support zero in general, so the intrinsic support number is
\[
\kappa=1.
\]

The tightening requires a new transformation that localizes each block to one anticommuting core and then relocates the shared Tag. The earlier production-inferred syndrome rank of five is therefore a sound theorem-discovery signal but a loose intrinsic bound.

The comparison with R6M shows that production semantics can coincide with intrinsic support in one family and overestimate it in another. Rank should be treated as a candidate certificate, not a universal formula.

## 5. SixLCU: low-order certificate, larger witnesses

For SixLCU, exact enumeration first identifies failures of the donor and a sequence of corrective trade classes. The resulting theorem states that donor cost equals unrestricted cost if and only if a declared predicate \(P0\) holds for every admitted batch and every size.

The predicate is low-order even though optimal correcting witnesses can require larger or global block structure. Certificate arity and witness arity are therefore different axes. A compact test can determine which regime an input belongs to without reconstructing the full optimum.

## 6. Stabilizer-state preparation: feature-relative refutation

The stabilizer-state preparation study uses exact state graphs for \(n=1\) through \(4\). The donor-exact region contracts with size, and four trade classes are witnessed.

In the first natural positive-conjunction vocabulary, no exact separator exists. Twelve feature cells contain both donor-exact and non-exact cases, which gives a vocabulary-relative irreducible floor of 43 errors among 1,146 cases. Searching harder over the same vocabulary cannot remove that floor.

This is a structural negative, not merely a failed classifier fit. It shows that the selected coordinates do not contain enough information to determine the regime labels on the frozen domain.

## 7. Exact local revival under an expanded vocabulary

A later expanded vocabulary contains 127 candidate features. On the frozen \(n\le3\) domain, 1,146 instances occupy 1,109 feature cells. Exhaustive search establishes:

- no single feature separates the labels;
- none of the 8,001 feature pairs separates them;
- none of the 333,375 feature triples separates them;
- one four-feature subset yields zero mixed cells.

The exact minimum separator complexity in this vocabulary is therefore four. The result revives recognizability on the frozen domain without overturning the earlier negative: the first vocabulary was insufficient, while the enlarged vocabulary contains a domain-local separator.

Mechanism attribution remains adverse. Removing either of two blocks from a previously proposed three-block explanation still permits zero error. The minimum witness uses no coordinate from one claimed state block. The data support a four-feature separator, not the earlier decomposition of why it works.

## 8. Failure on unseen size

The four-feature rule is evaluated on unseen \(n=4\) cases. It makes 32 errors among 120 cases. This equals the error of a parent-cell lookup baseline, and a label-shuffle calibration gives no evidence that the rule performs beyond that baseline. A different lattice-derived parent makes only 3 errors.

The exact \(n\le3\) separator is therefore not a transferred law. It is a domain-local classification theorem over the frozen small-state space.

This negative is scientifically useful. It distinguishes three achievements that would otherwise be conflated:

1. exact separability on a finite domain;
2. minimal separator complexity in a declared vocabulary;
3. prospective transfer to a larger domain.

Only the first two are established.

## 9. Cross-family synthesis

The four families occupy different positions.

- TARE has a small all-size support normal form and an evolving trade vocabulary.
- The shared-Tag grammar collapses to intrinsic support one.
- SixLCU has an exact low-order donor boundary despite larger witnesses.
- Stabilizer-state preparation has a four-feature exact small-domain boundary that fails on unseen size.

These results show that normal-form complexity and boundary recognizability are independent. Neither implies cross-domain transfer. The transferable object is the mapping workflow, not one universal geometric answer.

## 10. Limitations

The results concern exact, deliberately frozen grammars. They do not estimate prevalence in production chemistry or hardware-constrained compilation. Exact referees exist only at tractable scales or where analytic proofs replace enumeration.

Feature-relative non-separability does not rule out every possible representation. Conversely, an exact finite-domain separator does not imply a general law. Several lanes were motivated by earlier failures, so the programme is sequential rather than one fixed preregistered battery.

Exact structural cost is not physical runtime or quantum advantage. Routing, architecture, fault tolerance, measurement, and other resources can reorder practical choices.

## 11. Conclusion

Compilation regime geometry separates incumbent exactness, trade structure, normal-form complexity, recognizability, and prospective transfer. Across four compiler families, these components do not move together. Some grammars admit exact small-support normal forms, some admit compact boundaries, and one admits an exact small-domain separator that fails immediately at larger size. A regime map is therefore valuable not because it guarantees a simple phase diagram, but because it makes each proposed compression falsifiable and preserves the complexity that remains.
