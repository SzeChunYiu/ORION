# Compilation Regime Geometry: Exact Maps, Refutations and Transfer Across Quantum Compilation Families

## Abstract

Exact quantum compilation is usually studied by optimizing a fixed objective over a chosen family of constructions. We study a complementary question: what structural regimes determine when a restricted construction is already optimal, when a larger family is necessary, and when a compact structural rule ceases to exist? We call this object **compilation regime geometry** and operationalize it through five components: a donor-optimal region, exact trade or counterexample families, a proved sufficiency or normal-form bound where available, a structural membership rule when the representation supports one, and prospective tests that can refute transfer.

We apply this programme across several exact compilation families and retain both successful and failed components. In a shared-Tag TARE grammar, every optimum under the unit support-count objective admits frame support at most two for arbitrary system size, and that support bound remains valid throughout a proved coefficient cone; outside the cone, an exact support-three control appears. Successive compact closed-form explanations are nevertheless refuted by exact phantom and hybrid configurations, showing that a correct normal form need not imply a simple complete trade basis. In a rank-two grammar, an initially loose support bound is eventually sharpened to an intrinsic support number of one for all sizes. In a distinct LCU PREP/SELECT family, donor exactness is characterized exactly by a pair-derived condition for every admitted instance. A stabilizer-preparation family provides the critical negative transfer: the mapping procedure still applies, but no predicate in the frozen natural feature vocabulary separates donor-exact from donor-inexact cases exactly; mixed feature cells impose an irreducible 43/1146 classification error floor. A prospectively frozen enlarged vocabulary removes that floor on the complete small-size domain, where exactly four features suffice, but the resulting law fails to transfer to the next unseen size, matching a shuffle null there.

These results reject a universal low-order phase law. The contribution is instead a falsifiable methodology for mapping exact compilation families and for distinguishing intrinsic normal-form structure from representation-limited regime prediction. Failed transfers and refuted closed forms are part of the geometry rather than discarded anomalies.

## 1. Main results and assumptions

The paper makes four main claims.

**First, a regime map is a scientific object distinct from an optimizer.** For a fixed compilation grammar and objective, it asks where a restricted donor family is exact, what minimal structural departures are required outside that region, and which properties of the input can certify that regime without rerunning unrestricted optimization.

**Second, exact normal forms and compact regime explanations are logically distinct.** In the shared-Tag TARE family, support two is sufficient for every admitted size under the unit objective, yet simple closed-form explanations inside that support-two family are repeatedly refuted by exact counterexamples.

**Third, the mapping programme transfers even when the low-order hypothesis fails.** The LCU family admits a clean exact boundary, whereas stabilizer preparation does not admit an exact separator in the frozen feature vocabulary.

**Fourth, representation identifiability limits forecasting.** In the stabilizer-preparation study, opposite exact labels occur inside identical feature cells. No classifier restricted to that vocabulary can remove the resulting error floor by increasing training data or model complexity.

All theorems are indexed by their exact compilation grammar and objective. No result is transferred across objectives or compiler families without a new proof or experiment.

## 2. From exact optimization to regime geometry

Suppose an unrestricted exact compiler provides a reference optimum and a simpler donor family provides a restricted optimum. A conventional benchmark asks how often the donor matches the referee. Regime geometry asks for more structure:

1. **donor region:** characterize inputs on which the donor is exact;
2. **trade basis:** identify concrete structural configurations that improve on the donor;
3. **normal-form bound:** prove that optima can be found within a restricted structural class, where possible;
4. **membership rule:** determine whether input structure predicts the regime without solving the unrestricted problem;
5. **prospective falsifier:** commit a structural prediction before opening the exact referee on fresh cases.

These components can succeed independently. A family may have a tight normal form but no simple closed-form regime rule. A structural predictor may fit all known cases but fail on a new size. The framework is designed to preserve those distinctions.

## 3. Shared-Tag TARE: a sharp support bound with refuted explanations

The first family is a three-block shared-Tag exact compilation grammar under a unit support-count objective. The central all-size structural result is that every optimum has an equivalent optimum in which each auxiliary frame has support at most two.

This theorem substantially reduces the structural search space, but it does not close the regime classification. Early low-support donor formulas are refuted by exact instances in which a shared coupling coordinate produces a cheaper construction. An enlarged donor repairs that case and is then refuted by a converse mechanism in which support two on a favorable frame branch reduces global Tag or restoration cost. A later enlarged-borrow description closes the verified panel but is again refuted by exact hybrid configurations.

The sequence makes an important distinction visible. The support-two theorem survives every explanation refutation because all of the counterexamples remain inside the proved support-two normal form. Exact structural sufficiency is therefore stronger than any one human-readable decomposition of the optimum.

The theorem is also objective-indexed. For coefficients satisfying the registered cone conditions, support two remains sufficient for every size. A reweighted objective outside that cone produces an exact support-three case. The normal form is therefore not a grammar-only invariant.

## 4. Rank-two compilation: loose proof coordinates need not be intrinsic

A second compilation grammar initially admits an all-size support bound of five through a conserved-syndrome argument. Subsequent exact theorem work sharpens the intrinsic support number to one.

This gap is scientifically useful. A sound proof coordinate can certify an upper bound without identifying the smallest true normal form. The rank of the proof representation is therefore not automatically the intrinsic compilation complexity.

This case acts as a warning against reading the first successful theorem as a phase boundary. A regime map should distinguish a bound derived from a proof technique from a tight structural property of the compiler family.

## 5. LCU PREP/SELECT: an exact structural boundary

The third family is materially different from the shared-Tag grammars. Here the full mapping programme produces a cleaner result: donor exactness is characterized by a pair-derived structural condition for every admitted batch and size.

This is the positive transfer case. The regime boundary is not a fitted classifier over exact labels; it is an all-instance statement tied to the family semantics. The compact rule is therefore a genuine property of this compilation object rather than an empirical convenience.

The contrast with the other families is central to the paper. Regime geometry does not predict that every family has a simple boundary. It provides a procedure that can establish such a boundary when it exists and expose the obstruction when it does not.

## 6. Stabilizer preparation refutes the universal low-order hypothesis

The strongest negative transfer comes from stabilizer-state preparation. The same five-component mapping programme can be applied, but a compact exact predicate does not emerge in the frozen natural feature vocabulary.

The initial direct size transfer already fails. More importantly, the failure is not repaired by simply enlarging formula size over the same information. The frozen feature representation contains mixed cells: instances with identical visible features but opposite exact donor-optimality labels. Across the complete finite study, these mixed cells impose an irreducible error floor of 43 errors among 1146 decisions for any rule restricted to that vocabulary.

This is an information boundary, not an optimization failure. A more sophisticated classifier operating on the same representation cannot make the labels a function of information that does not separate them.

The result falsifies the tempting cross-family slogan that regime boundaries are universally low-order. The correct synthesis is conditional: some compiler families admit compact structural phase rules; others require richer state or retain unavoidable ambiguity under a chosen representation.

## 7. What transfers across families

The common object is therefore methodological rather than one universal formula.

Across the studied families, useful regime analysis asks:

- What is the strongest native donor family?
- Is there an exact structural witness for donor failure?
- Can all optima be normalized into a smaller class?
- Is the regime label identifiable from a compact input representation?
- Does the proposed structure predict fresh exact outcomes before the referee is opened?

The answers differ by family. TARE has a strong normal form but a nontrivial evolving trade basis. The rank-two grammar shows that a theorem-derived support coordinate can be loose. LCU admits a clean exact donor boundary. Stabilizer preparation shows that the chosen compact representation can be non-identifying.

Those differences are the regime geometry.

## 8. Failure boundaries are primary results

Three negative results should remain visible in the main paper.

First, compact TARE explanations can fail even when the support theorem remains correct. Second, a theorem-generated support bound can be far from intrinsic tightness. Third, a compact cross-family separator can fail because the representation itself merges opposite regimes.

These are not merely failed development attempts. They answer different reviewer-level alternatives: whether the normal form implies a simple basis, whether proof coordinates equal intrinsic complexity, and whether more fitting can fix a representation that does not identify the target.

## 9. Relation to quantum compilation research

Exact synthesis, compiler optimization, resource estimation and family-specific structural theorems are established areas. The present work does not claim exact search, dynamic programming, local rewrite analysis or support bounds in general as new concepts.

The residual contribution is to treat the **map of exactness regimes** as the object of study and to require its components to carry separate authority. A finite zero-error classifier is not an all-size theorem. A normal-form theorem is not a complete explanation. A prospective prediction is not a proof. A representation failure is not repaired by a larger model over the same information.

## 10. Limitations

The studied families do not establish a universal theory of quantum compilation phases. Each theorem depends on a fixed grammar and objective. Hardware-level resource implications are outside the current evidence, and exact compiler cost is not a quantum-speedup claim.

The stabilizer-preparation error floor is exact only for the frozen feature vocabulary and finite domain. A richer representation could separate the mixed cells. Conversely, a compact rule in one family should not be transferred to another without a new proof.

The previous size-transfer promotion attempt has therefore been stopped rather than retuned. The bounded paper treats that failure as part of the final scientific map.

## 11. Reproducibility and availability

The submission should archive the exact family definitions, theorem statements, counterexample witnesses, finite censuses and prospective prediction records needed to reconstruct each claim. The first pages should state the principal assumptions and distinguish theorem-backed all-size results from finite exact checks. Code and data required to judge the claims should be accessible under the journal's reproducibility expectations.

## 12. Conclusion

Compilation families can possess sharply different regime geometries. Some admit exact low-complexity boundaries; others admit strong normal forms but complicated internal trades; still others are not identifiable from a compact representation. By treating theorem, counterexample, classifier and prospective prediction as separate evidence objects, the regime-geometry programme turns both transfer and refutation into a coherent map. The result is not a universal phase law, but a disciplined way to discover when such a law exists and when the available representation makes it impossible.