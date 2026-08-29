# Theorem-Backed Static Cost Forecasting with Fallible Regime Explanations

## Abstract

Static forecasting in exact quantum compilation is attractive when an input can be assigned a certified optimum without rerunning a large unrestricted search. A central difficulty is that a forecast can be correct for different reasons: an all-size theorem may certify the cost, a compact structural rule may explain which regime realizes it, or a finite benchmark may merely show agreement with an exact referee on tested instances. We show that these forms of evidence can diverge and should be reported separately.

For a shared-Tag TARE compilation grammar under a fixed unit support-count objective, an all-size normal-form theorem proves that the unrestricted optimum is attained within the full support-at-most-two family. The resulting static cost functional is therefore exact for every admitted system size under that objective. It also agrees with unrestricted dynamic-programming truth on all 9,547 registered comparison instances, which serves as an implementation check rather than the source of exactness. A compact enlarged-borrow explanation repairs an earlier fresh-instance counterexample and fits the verified explanation panels, but a later hostile study finds 64 exact hybrid witnesses among 740 instances that fall outside that explanation. The cost certificate remains correct because all of those witnesses still lie inside the theorem-certified support-two family. A further refined explanation closes 10,481 verified instances while one all-size explanation sector remains open.

The paper's main result is therefore a hierarchy of authority: theorem-backed cost exactness can survive the refutation of a human-readable regime explanation. This distinction prevents benchmark agreement from being mistaken for proof and prevents an explanatory counterexample from incorrectly invalidating a stronger cost theorem. The result is restricted to the stated grammar and objective and carries no full-circuit, hardware or quantum-advantage claim.

## 1. Main result

Consider an exact compilation problem with an unrestricted referee and a static predictor that reads only the input structure. Three questions should be separated:

1. Is the predicted **cost** equal to the unrestricted optimum?
2. Is the proposed **regime explanation** complete, meaning that it describes every optimal structural configuration?
3. Does a finite benchmark **agree** with the referee on the cases tested?

These questions can have different answers.

For the compilation family studied here, the first answer is yes under the fixed unit objective. The all-size theorem states that every unrestricted optimum has an optimum inside the complete support-at-most-two family. Evaluating that family therefore gives the exact unrestricted cost for every admitted size.

The second answer is not yet yes. Several compact regime descriptions are refuted by exact configurations that remain inside support two. The third answer is yes on the registered implementation panel, but that agreement corroborates the implementation; it does not prove the theorem.

This layered structure is the central contribution.

## 2. Why static cost forecasting needs certificates

A static forecaster is useful only if its authority is clear. A closed formula can be fast but wrong outside the cases from which it was inferred. A restricted exact search can be correct because a theorem proves the restriction complete. A heuristic can match all known examples while remaining vulnerable to one new configuration.

We therefore attach a distinct evidentiary status to each forecast component. The strongest form is a mathematical or machine-checked theorem that the searched structural family contains an optimum. Finite exact comparisons then test whether the implementation of that theorem-backed family agrees with the reference solver. Compact regime labels are treated as an explanatory layer whose failure need not invalidate the cost layer.

## 3. An early closed-form forecast is exactly refuted

The initial compact predictor combines three intuitive construction families and selects their minimum predicted cost. It performs well on the original development set but fails on a frozen fresh instance: the unrestricted optimum is 10 whereas the closed form predicts 11.

This single exact counterexample is sufficient to reject the proposed closed form as a complete static cost certificate. The failure is not repaired by averaging performance or by increasing tolerance because the objective is discrete and the exact referee is available.

The counterexample instead identifies a missing configuration involving a broader support-two construction. This motivates a new predictor defined over the complete support-at-most-two family rather than a small hand-written menu.

## 4. The full support-two cost functional is exact for all sizes

Let the static cost functional return the minimum cost over the full support-at-most-two family. Its exactness does not come from the observed benchmark. It follows from the all-size normal-form theorem: under the frozen grammar and unit support-count objective, the unrestricted optimum always has a representative in that family.

Consequently,

> minimum cost over the full support-two family = unrestricted exact optimum

for every admitted system size under the theorem assumptions.

As an implementation check, the static functional is compared with the unrestricted dynamic-programming referee on 9,547 registered instances and has zero error. The finite count is useful because it tests the evaluator and the code path on a broad exact panel. It should not be read as the proof of all-size exactness.

## 5. Explanation repair succeeds locally and then fails globally

A human-readable enlarged-borrow rule is introduced to explain the configuration that refuted the first closed form. It correctly repairs that fresh instance and matches the verified explanation panels.

A later hostile search tests whether the explanation is complete for arbitrary size. It finds 64 exact hybrid configurations among 740 hostile instances that achieve the optimum while lying outside the enlarged-borrow description.

This refutes the explanation theorem but not the cost theorem. Every hybrid witness remains inside the complete support-two family. The static cost functional therefore still returns the exact optimum.

The distinction matters in practice. If the compact explanation had been treated as the source of cost authority, the counterexamples would appear to destroy the forecaster. If the theorem-backed support-two family is recognized as the source of cost authority, the same counterexamples instead reveal that the explanation is incomplete.

## 6. A refined explanation closes a larger finite domain

A further explanation family incorporates the newly identified hybrid structure and closes 10,481 verified instances. This is meaningful progress in interpretability and structural classification, but it remains a finite closure result. One registered all-size explanation sector is still open.

The manuscript therefore does not claim an exact all-size regime formula. The cost is exact; the compact explanation is still under mathematical characterization.

This is precisely the distinction the paper is designed to make visible.

## 7. Prospective evidence and verification authority

The broader compilation programme also includes staged prospective predictions in which a regime and exact cost are committed before the unrestricted referee is opened. Across 102 registered staged predictions, the committed predictions agree with the exact outcomes on their frozen rows.

Prospective agreement provides evidence that a structural rule can be used before optimization, but it does not replace theorem authority. Conversely, a prediction row without a committed exact-referee result is not treated as verified merely because its prediction exists.

The evidence hierarchy is therefore:

- theorem for all-size cost exactness;
- exact referee for finite implementation validation;
- prospective prediction for forward-use evidence;
- compact explanation for interpretation, subject to independent counterexamples.

## 8. Objective dependence

The cost theorem is indexed by the unit support-count objective. Reweighted objectives can change which support configurations are optimal. Separate objective-robustness work identifies a coefficient region in which the support-two theorem remains valid and also supplies a support-three control outside that region.

The current paper therefore does not transfer the static cost certificate to arbitrary resource models. Any such transfer requires an objective-specific proof.

This restriction is not a technical footnote. A static forecaster that ignores the objective can be exactly correct for the wrong optimization problem.

## 9. What the result contributes

The paper contributes an evidence architecture for exact static forecasting.

First, it gives a theorem-backed static cost functional that is exact on the stated compilation family and objective. Second, it shows through exact counterexamples that a compact explanatory decomposition can be weaker than the cost certificate. Third, it demonstrates why finite zero error should be reported as implementation consistency rather than promoted to all-size proof. Fourth, it preserves prospective predictions and explanation failures as separate evidence rather than collapsing them into one accuracy number.

The result is especially relevant when exact optimization becomes expensive but a theorem can restrict the search to a provably complete structural family.

## 10. Relation to quantum compilation and resource estimation

Exact synthesis, restricted-family optimization, resource estimation and structural compiler rules are established research areas. The contribution here is not the generic idea of using a restricted exact family or predicting resource cost from input structure.

The residual is the layered certificate: the manuscript states exactly which part is theorem-backed, which part is benchmark-validated, which part is prospectively exercised and which explanatory statement has been refuted. This makes the forecast auditable even when the most intuitive structural story changes.

## 11. Limitations

The theorem is specific to one compilation grammar and objective. It does not establish full-circuit gate counts, device-level performance, runtime superiority or quantum advantage. The current compact regime explanation is not proved complete for all sizes, and the finite explanation closure should not be read as an unbounded result.

Implementation timing is also environment-dependent. Unless a final submission environment is fixed and measured, runtime should remain descriptive rather than part of the scientific headline.

## 12. Reproducibility and availability

The submission should archive the theorem statement and proof, the support-two evaluator, the unrestricted reference implementation used for finite checks, all counterexample witnesses, the prospective prediction records and the exact objective definition. Quantum requires the main results and assumptions to be easy to locate early in the paper; the final arXiv version should therefore preserve the hierarchy stated in Sections 1 and 7 and provide accessible code/data where needed to verify the claims.

## 13. Conclusion

An exact static forecast can remain correct even when its compact explanation is wrong. In the studied TARE grammar, an all-size support-two theorem certifies the cost functional, while exact hybrid counterexamples refute a simpler regime description without leaving the theorem-certified family. Separating theorem, finite benchmark, prospective prediction and explanation prevents one evidence layer from borrowing authority from another. The result is a bounded but exact cost certificate, not a universal compiler or hardware-performance claim.