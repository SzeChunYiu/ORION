# Exact Static Cost Forecasting with Fallible Structural Explanations

## Abstract

Static resource forecasting is attractive when an exact optimum can be inferred from input structure without rerunning an unrestricted search. The evidentiary difficulty is that several different claims are often collapsed into one accuracy statement: a theorem may certify the cost, a compact structural rule may explain which regime realizes it, and a finite benchmark may merely show that an implementation agrees with an exact referee. We show that these layers can disagree and should carry separate authority.

For a shared-Tag TARE compilation grammar under a fixed unit support-count objective, an all-size normal-form theorem proves that every unrestricted optimum has an optimum in the complete support-at-most-two family. Minimizing over that family therefore gives the exact unrestricted cost for every admitted system size under the theorem assumptions. The implementation agrees with unrestricted dynamic-programming truth on all 9,547 registered comparison instances, but this finite zero-error result is an implementation check rather than the source of exactness. A compact enlarged-borrow explanation repairs an earlier fresh-instance counterexample and fits its verification panels, yet a later hostile study finds 64 exact hybrid witnesses among 740 instances outside that explanation. The cost certificate survives because every witness remains in the theorem-certified support-two family. A refined explanation subsequently closes 10,481 verified instances, while one all-size explanation sector remains open.

The central result is a hierarchy of scientific authority: theorem-backed cost exactness can survive refutation of a human-readable regime explanation. Prospective prediction and finite benchmark agreement add forward-use and implementation evidence, but neither substitutes for the all-size proof. The result is restricted to the stated grammar and objective; it does not establish full-circuit performance, hardware advantage, arbitrary resource models, or quantum advantage.

## 1. Main results and assumptions

Quantum compilation papers often mix three questions that require different evidence:

1. **Cost exactness:** does the static predictor equal the unrestricted optimum?
2. **Explanation completeness:** does a compact regime description capture every optimal structural realization?
3. **Finite agreement:** does an implementation match an exact referee on tested instances?

For the problem studied here, these questions have different answers.

### Main result 1 — all-size cost exactness

Under the frozen shared-Tag TARE grammar and the unit support-count objective, an all-size normal-form theorem establishes that the unrestricted optimum always has a representative in the full support-at-most-two family. Therefore

> minimum cost over the complete support-two family = unrestricted exact optimum

for every admitted system size satisfying the theorem assumptions.

### Main result 2 — the compact explanation is not all-size complete

A compact enlarged-borrow description is exactly refuted by 64 hybrid witnesses in a 740-instance hostile study. Those witnesses remain inside support two, so they refute the explanation but not the cost theorem.

### Main result 3 — finite and prospective checks corroborate different layers

The theorem-backed evaluator has zero error on 9,547 registered unrestricted-referee comparisons. In a separate staged prospective sequence, 102 committed predictions agree with their frozen exact outcomes. These results test implementation and forward use; they are not the proof of all-size exactness.

The assumptions are load-bearing. The theorem is indexed by the stated compilation grammar and cost objective. Changing the resource weights can change the optimal support structure and requires a separate objective-specific argument.

## 2. Why static forecasts need an authority hierarchy

A static formula can be fast and still fail outside the instances from which it was inferred. A restricted exact search can be globally correct if a theorem proves the restriction complete. A compact explanation can be scientifically illuminating while remaining incomplete. A finite benchmark can expose implementation defects while saying nothing about untested sizes.

The paper therefore attaches evidence to the claim it actually supports. The theorem licenses all-size cost exactness. Exact finite comparisons validate the implementation on a registered panel. Prospective predictions show that structural rules can be committed before an exact referee is opened. Compact regime descriptions provide interpretation and are allowed to fail without borrowing authority from the theorem.

This separation is not bookkeeping. It determines what a counterexample means.

## 3. A compact closed form fails exactly

The initial predictor chooses the minimum cost among three intuitive construction families. It fits the original development cases but fails on a frozen fresh instance: the unrestricted optimum is 10 while the closed form predicts 11.

Because the objective is discrete and the unrestricted exact referee is available, this single witness is sufficient to reject the closed form as a complete certificate. Averaging the error away would answer the wrong question.

The witness reveals a broader support-two configuration missing from the hand-written menu. This motivates a new predictor that minimizes over the complete support-at-most-two family rather than over a short list of named regimes.

## 4. The support-two cost functional is exact for all sizes

The stronger predictor is not justified by the 9,547-instance benchmark. Its authority comes from the normal-form theorem.

The theorem shows that any unrestricted optimum can be transformed, without increasing the frozen objective, into an admissible optimum whose active support is at most two. Once that result is established, exhaustive optimization over the complete support-two family is not a heuristic restriction: it is an exact realization of the unrestricted optimum under the theorem assumptions.

The registered dynamic-programming comparison remains valuable. Zero error on all 9,547 cases checks that the implementation of the theorem-backed family, objective accounting, and reference interface agree across a broad exact panel. The manuscript keeps that evidence separate from the proof.

## 5. Explanation repair succeeds locally and fails globally

The fresh counterexample motivates an enlarged-borrow explanation intended to characterize the newly exposed support-two behavior. The rule repairs the refuting instance and agrees with its registered explanation panels.

A later hostile search asks a stronger question: is this compact explanation complete at arbitrary size? The answer is no. Among 740 hostile instances, 64 exact hybrid configurations attain the optimum while lying outside the enlarged-borrow description.

These witnesses do not leave the complete support-two family. The scientific consequences are therefore asymmetric:

- the compact explanation is refuted as an all-size classification;
- the theorem-backed cost functional remains exact.

This is the paper's key stress test. A weaker evidence architecture would let the explanation borrow the theorem's authority and would make the hostile witnesses appear to invalidate the forecaster itself.

## 6. Refined finite explanation and the remaining open sector

A refined explanation incorporates the hybrid mechanism and closes 10,481 verified instances. That is meaningful evidence for interpretability and structural classification, but it is still finite evidence. One registered all-size explanation sector remains open.

We therefore do not claim a final all-size regime formula. The cost problem is closed under the theorem assumptions; the compact explanatory problem is not.

## 7. Prospective predictions test forward use, not theorem truth

The broader programme contains 102 staged predictions in which regime and exact cost are committed before the unrestricted referee is opened. All 102 frozen predictions agree with their exact outcomes.

This chronology matters because it demonstrates that the structural predictor can be used prospectively rather than merely fitted to an already inspected panel. It still does not replace mathematical authority. A prospective row without a committed exact outcome remains unresolved, and a finite sequence of successful predictions does not prove the all-size theorem.

The evidence hierarchy is therefore:

> all-size theorem → exact cost authority; finite referee panel → implementation validation; prospective rows → forward-use evidence; compact explanation → interpretation subject to counterexample.

## 8. Objective dependence

The theorem is stated for a unit support-count objective. Separate robustness work identifies a coefficient region in which the support-two conclusion continues to hold and provides a support-three control outside that region.

The present manuscript does not generalize the exact certificate to arbitrary device or resource models. If a new objective changes the relative cost of support structures, the correct scientific response is a new objective-specific proof or counterexample analysis, not reuse of the unit-objective theorem by analogy.

## 9. Relation to prior compilation and resource-estimation work

Exact synthesis, restricted structural families, resource estimation, dynamic programming, and compiler-specific regime rules are established areas. The paper does not claim the generic idea of estimating cost from structure or searching a restricted family.

Its residual contribution is the **certificate hierarchy**: an exact theorem-certified cost functional is presented together with finite implementation checks, prospective use, and explicitly fallible structural explanations. The hostile explanation counterexamples are part of the main result because they demonstrate why these layers must not be conflated.

## 10. Limitations

The theorem is specific to the stated TARE grammar and objective. No full-circuit gate-count, device-level runtime, noise, hardware performance, or quantum-advantage claim follows. The refined structural explanation is not proved complete at arbitrary size, and its 10,481-instance closure remains a finite result.

Implementation timing is environment-dependent and should remain descriptive unless a submission environment and measurement protocol are frozen separately.

## 11. Reproducibility and availability

The publication archive should contain the theorem statement and proof, the support-two evaluator, the unrestricted exact referee used for finite checks, the fresh and hostile counterexample witnesses, the 102 prospective prediction records with their chronology, and the exact objective definition. The main result and assumptions should remain visible in the first pages, with detailed derivations and implementation instructions moved to the appropriate proof, Methods, or artifact surfaces.

Quantum submission additionally requires the manuscript to be posted to or cross-listed with `quant-ph`; the release package should preserve the exact claim hierarchy above rather than replacing it with a single accuracy headline.

## 12. Conclusion

An exact static forecast can remain correct after its most intuitive explanation fails. In the studied TARE grammar, an all-size support-two theorem certifies the cost functional, while exact hybrid witnesses refute a simpler structural regime description without escaping the theorem-certified family. Finite zero error and prospective prediction corroborate implementation and forward use but do not create proof. Separating theorem, benchmark, prospective prediction, and explanation yields a forecast whose authority remains clear even when the human-readable structural story changes.