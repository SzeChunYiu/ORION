# Diagnosing Information, Representation and Computation Failures by Intervention

## Abstract

When a learning or reasoning system fails, increasing model size or inference compute is a common default response. That response is scientifically ambiguous because the same poor outcome can result from missing semantic information, an inaccessible representation of available information, or insufficient downstream computation. We study failure diagnosis as an intervention problem rather than inferring cause from final accuracy alone.

The empirical programme combines positive, null and adverse results. In information-preserving representation tests, a fixed linear access mechanism loses 0.0352 accuracy on breast-cancer data and 0.0239 on handwritten digits after a bijective cubic transformation, while Wine is a null cell; deterministic inverse repair restores the native linear result on the preregistered positive datasets. A protected model-size and inference-budget sweep with 0.5B, 1.5B and 3B open-weight language models does not support the registered monotone scaling hypothesis and is retained as a negative result. The main causal diagnostic uses one-coordinate interventions on information, accessibility and computation. Across five protected task families in two qualitatively different domains, it identifies the registered failure class on four of five tasks, compared with one of five for a generic escalate-compute heuristic, and produces zero false compute escalations compared with four. One held-out accessibility diagnosis fails to transport its threshold and remains unresolved rather than being retuned after inspection.

A corrected eight-coordinate resource ledger charges semantic information, representation dimensionality and transformation, model state, fitting, inference, explicit computation and registered recovery cost separately. The diagnostic decisions and the adverse held-out cell remain unchanged under that accounting. A separate hostile representation study also shows that an earlier large serialized-representation margin is format-prior sensitive; that margin is retired from the paper's evidence rather than repaired post hoc.

The contribution is a bounded causal diagnostic methodology: intervention response can distinguish information, accessibility and computation failures more reliably than generic compute escalation on the registered tasks. The paper does not claim universal LLM scaling laws or universal superiority of structured representations.

## 1. Introduction

A poor model output does not identify why the system failed. More data may help when relevant information is missing. A different representation may help when the information is present but difficult for the current access mechanism to use. More inference or search may help when the representation is adequate but the available computation is insufficient.

These causes can produce similar final accuracies. Observing only the terminal score therefore creates a causal identification problem.

We ask whether failure location can instead be diagnosed by **controlled interventions**. The central idea is simple: change one resource coordinate while holding the others fixed as far as the task permits, then observe which intervention crosses a prespecified quality target.

The paper distinguishes three primary coordinates:

- semantic information available to the system;
- accessibility of that information under the current representation or interface;
- downstream computation applied after the representation is fixed.

Model capacity is recorded separately because it can alter the access mechanism and computation frontier without revealing which coordinate was responsible for the original failure.

## 2. Why terminal accuracy is not a diagnosis

Consider two tasks with the same observed error rate. In the first, a critical variable has been removed from the input. No amount of computation over the remaining representation can recover information that is not present. In the second, all semantic information is preserved by a bijective transformation, but a fixed linear mechanism cannot easily access the relevant relation. These tasks can look equally difficult from the final score while requiring different repairs.

A generic uncertainty-driven policy that simply escalates compute treats these cases as equivalent. The intervention approach instead asks what happens when information, representation accessibility and computation are changed separately.

A diagnosis is accepted only when the registered intervention reaches the frozen quality target on the protected evaluation. If a probe-time diagnosis fails to transport to protected data, the result remains unresolved.

## 3. Same-information representation interventions

The first empirical component uses public real datasets and a bijective cubic representation transform. Because the transform is invertible, the semantic information content is preserved. The access mechanism is held fixed.

On breast-cancer data, the native-to-cubic accuracy gap is 0.0352. On handwritten digits it is 0.0239. Deterministic inverse repair reconstructs the native features to floating-point roundoff and restores the native linear mean on both preregistered positive datasets.

Wine provides the important null: the native-to-cubic difference is approximately -0.00016. The representation intervention therefore does not support a universal claim that the cubic encoding harms linear accessibility across datasets.

The supported statement is narrower. An information-preserving transformation can change performance for a fixed access mechanism, and explicit inverse representation repair can recover that accessibility in the positive cells.

## 4. Larger language models do not reveal a monotone accessibility law

A separate protected experiment tests whether increasing language-model size and inference budget reveals a stable advantage for the structured state. The registered hypothesis is negative under the recovered immutable outputs.

At the primary inference budget, the structured-minus-same-information difference is -0.1406 for the 0.5B model and 0 for both the 1.5B and 3B models. The positive-at-every-size gate fails, the largest-model protected lower bound is not above zero, and hostile controls do not support the monotone hypothesis.

This result is retained because it constrains the interpretation of the representation studies. The paper cannot claim that larger model capacity monotonically exposes an underlying structured-state advantage.

The negative also motivates the causal diagnostic. Scaling the model is one intervention, not an explanation of why the task failed.

## 5. Intervention-based causal diagnosis

The main study freezes a small set of task families with interventions that separately alter information, representation accessibility and computation. On a probe split, the diagnostic selects the lowest-cost intervention that reaches a prespecified quality target. Protected data are then used to determine which intervention actually clears the target.

Across five task families spanning handwritten-digit tasks and exact executable tasks, the diagnostic is correct on four. A generic policy that escalates computation when uncertainty remains is correct on one.

The contrast is sharper in false compute escalation. The intervention diagnostic sends no protected task to unnecessary compute escalation, whereas the generic heuristic does so four times. The mean registered intervention-cost regret of the diagnostic is zero on the actionable protected tasks.

Three exact executable tasks are diagnosed correctly. Of two digit tasks, one is diagnosed correctly and one exposes a transfer failure discussed below.

These counts are deliberately reported with their small denominator. They are bounded cross-domain mechanism evidence, not a population estimate for arbitrary AI tasks.

## 6. The protected failure is part of the result

For one digit task, inverse representation repair clears the probe target but not the protected target. The probe-time rule therefore predicts an accessibility failure, while the protected outcome does not establish that diagnosis.

The threshold is not relaxed after observing the protected result. The case remains unresolved.

This adverse cell is scientifically useful because it demonstrates the exact failure mode the methodology is designed to preserve: an intervention that appears diagnostic during development may not transport to protected deployment data. A method that simply relabeled this case after inspection would no longer be testing prospective diagnosis.

## 7. Full resource accounting

Diagnoses can be distorted if representation or preprocessing work is treated as free. The final resource ledger therefore separates eight coordinates:

1. semantic information;
2. representation dimensionality;
3. representation transformation work;
4. fitted model state;
5. fitting cost;
6. inference cost;
7. explicit downstream computation;
8. registered recovery or intervention cost.

The corrected ledger fixes earlier under-counts by charging fitted scaler state, exact-domain readout operations and accessibility serialization. Decisions are re-derived from the resource records rather than copied from previous labels.

The headline diagnostic remains four of five versus one of five, the protected unresolved case remains unresolved, and the false-compute-escalation counts remain zero versus four. No scalar exchange rate is imposed across unlike resources.

The resource result therefore supports the causal interpretation without claiming one universal total-cost metric.

## 8. A hostile format attack retires an earlier representation headline

An earlier same-information serialization experiment appeared to show a large advantage for a typed relational representation. A prospectively frozen hostile study tests whether that margin is invariant to semantics-preserving symbol changes.

A global symbol remint changes the serialized comparator's protected accuracy from 0.75 to 0.50 and changes 32 of 128 answers. The large historical margin is therefore format-prior sensitive and is retired as headline evidence.

A later invariant profile representation recovers the 0.75 behavior under the registered orbit checks, but that successor does not retroactively rehabilitate the defeated margin. The correct lesson is about diagnosis: representation accessibility can matter, but a particular serialization advantage may depend on incidental numerical or format choices.

## 9. What the combined evidence supports

The strongest current conclusion is methodological.

Failure should not automatically be interpreted as insufficient compute. On the registered tasks, intervention response distinguishes missing information, inaccessible representation and insufficient computation substantially better than a generic compute-escalation heuristic. The positive real-data accessibility cells show that representation can be causal even when semantic information is preserved. The Wine null prevents universalization. The language-model sweep shows that scale does not monotonically reveal the effect. The protected digit failure shows that a diagnosis can fail to transport.

Together these results are stronger than a collection of positive representation examples because they identify both where the diagnostic works and where its assumptions fail.

## 10. Relation to representation learning and test-time compute

Representation learning, feature access, model scaling and test-time computation are mature research areas. The paper does not propose a new neural architecture or claim that representation structure is generically superior.

The residual contribution is the experimental decomposition of failure cause. Rather than compare two final systems and infer why one wins, the study intervenes separately on information, accessibility and computation and uses protected outcomes to score the diagnosis.

This distinction is especially relevant when compute escalation is expensive or when an information-preserving representation change can make a task easier for a fixed mechanism.

## 11. Limitations

The main diagnostic has only five protected task families. The exact-domain tasks and digit tasks are qualitatively different, but they do not establish broad agent or language-model generality. A wider LLM-agent claim would require a new procedural domain and additional model families.

The intervention taxonomy is also not proven complete. Real failures can involve interactions among information, representation, model capacity, computation and method availability. The study identifies the registered single-coordinate causes; it does not claim every failure has one unique coordinate.

Finally, the resource vector is intentionally not scalarized. Decision makers with a fixed price model can add a cost function, but the paper does not infer one from the observed outcomes.

## 12. Reproducibility and availability

The anonymous TMLR package should include the frozen task definitions, intervention rules, protected results, corrected resource ledger, hostile representation tests and independent scorer. The submission should preserve the negative language-model result, Wine null and unresolved deployment cell in the main evidence story rather than relegating them to an inaccessible audit archive.

## 13. Conclusion

Poor performance does not reveal its own cause. Across bounded real-data and exact tasks, controlled interventions on information, representation accessibility and computation provide a more informative diagnosis than generic compute escalation. The result survives corrected resource accounting while retaining a negative scaling study, a real-data null and a protected transfer failure. The contribution is therefore a causal diagnostic methodology with explicit boundaries, not a universal claim that structured representations or larger models determine performance.