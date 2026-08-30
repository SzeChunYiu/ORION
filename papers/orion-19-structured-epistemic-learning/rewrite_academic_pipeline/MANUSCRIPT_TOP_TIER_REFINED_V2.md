# Diagnosing Whether Learning Fails from Missing Information, Inaccessible Information, or Missing Computation

## Abstract

When a learning system fails, adding model capacity or test-time computation is useful only if computation is the binding constraint. We develop a controlled diagnostic that separates three failure classes: information is absent from the model-visible view, information is present but inaccessible to the selected learner, or the remaining operation is computational and can be closed by an explicit procedure.

For a finite protected sample, exact collisions under a declared view give a deterministic accuracy ceiling. Generic classical learners receive first right of refusal. Explicit interventions then add information, reorganize the same information, or supply a frozen computation. On a five-family intervention panel, the registered diagnostic classifies 4 of 5 families under its original rule, compared with 1 of 5 for a generic uncertainty-triggered compute policy, and avoids four false compute escalations. On the false-escalation endpoint, all four paired disagreements favor the diagnostic; the exact five-family value is \(p=0.125\), and the generic comparator escalates by construction. An uncertainty-aware successor conforms on all five registered cases while retaining one accessibility case as `CANNOT_CHECK`.

In structured hostile pairs, typed relation, transport, and admitted-history coordinates are load-bearing exactly where weaker views collide. Once local affine maps are visible, generic learners remain near chance on global gluing, while exact affine composition closes the task. On a whole held-out procedural domain, typed relational comparisons score 1.0 versus 0.90625 for the strongest non-degenerate untyped comparator, with 12 cases favoring typed and none reversing. Case-level inference is post hoc and mutation-family identifiers needed for cluster-valid uncertainty are absent.

The contribution is a bounded failure-diagnosis methodology. A monotone language-model scaling hypothesis is negative, one real-data accessibility cell is null, two large transfer margins are withdrawn after hostile controls, and an unexecuted frontier contributes no evidence. The study does not establish neural architectural superiority or broad policy performance.

## 1. Introduction

A poor score does not identify its own cause. The model may be missing decisive information. The information may be present but organized in a way the selected learner cannot exploit. Or the representation may be sufficient while the target requires an explicit composition or search operation.

These cases imply different interventions.

- Missing information requires measurement, retrieval, or a richer observable state.
- Accessibility failure may be repaired by representation or learner change.
- Computational failure requires an operation that transforms available information into the target.

A policy that treats every uncertain case as a reason to spend more compute can be predictably wasteful. More search cannot recover a distinction erased by the input view.

We study a prospective diagnostic built around exact finite-sample information ceilings, simple-model first right of refusal, and intervention tests that change one failure axis at a time. The goal is not a new architecture. It is a way to decide whether architectural escalation is even relevant.

## 2. Exact information ceilings

Let \(\mathcal D\) be a finite protected sample and \(f_V(x)\) the exact fingerprint visible under view \(V\). Partition \(\mathcal D\) into groups of identical fingerprints. Any deterministic predictor using only \(V\) must return one label per group.

The maximum possible accuracy is
\[
C_V
=
\frac{1}{|\mathcal D|}
\sum_g
\max_y
|\{x\in g:y(x)=y\}|.
\]

This ceiling is elementary accounting over the frozen sample. It is not a theorem about asymptotic Bayes error or all future data. Its value is diagnostic:

- performance above \(C_V\) indicates leakage or evaluator error;
- performance at a low ceiling shows that the view is non-identifying;
- performance below a ceiling of one leaves either learning/accessibility or computation as the residual.

The distinction depends on the declared view. Surface, topology, typed relation, current transport, and semantic history are progressively richer observable states.

## 3. Diagnostic protocol

The protocol applies interventions in a fixed order.

First, compute the view-collision ceiling. If the target is not identifiable, additional compute is not the remedy.

Second, give generic classical learners first right of refusal. Logistic regression, trees, forests, and nearest neighbors test whether ordinary access is enough before a specialized architecture is introduced.

Third, reorganize or expose the same information. A successful same-information intervention indicates accessibility rather than missing content.

Fourth, when the required operation is transparent, run a separately frozen explicit procedure. If that procedure closes the residual from the same visible coordinates, the gap is computational.

The protocol permits abstention. A family whose response does not cross its registered decision boundary remains `CANNOT_CHECK`.

## 4. Five-family intervention result

The protected diagnostic panel contains five task families across two domains. The registered decision rule chooses among information, accessibility, and computation from development and probe interventions, then compares its choice with independently recomputed protected causal gold.

Under the original rule, the diagnostic is correct on 4 of 5 families. A generic policy that escalates compute under uncertainty is correct on 1 of 5 and falsely escalates compute in four families whose binding constraint is not computation.

On the false-compute-escalation endpoint, there are four paired disagreements, all favoring the diagnostic and none favoring the generic policy. With only five family-level units, the exact McNemar value is \(p=0.125\). The result is therefore mechanism evidence on a frozen panel, not a population performance estimate. The generic policy's errors are also partly definition-driven because its rule explicitly routes uncertainty to compute.

A second rule replaces point-threshold decisions with an ensemble-mean threshold. It reaches 5 of 5 diagnoses but fails its half-draw stability gate on one digits accessibility case. The decision margin is smaller than the rule's own sampling noise, so that failure is retained.

A third rule uses a 95% lower confidence bound for target satisfaction without changing any target. It conforms on all five registered families and has stable half-draw decisions. Crucially, the difficult digits accessibility cell remains `CANNOT_CHECK`: both probe and protected lower bounds stay below the unchanged target. The successor stabilizes the abstention rather than converting it into a pass.

## 5. Structured hostile pairs identify missing coordinates

Three paired constructions hold weaker views fixed while changing one decisive coordinate.

In the relation family, identical weak structure receives different targets depending on whether an evidence relation supports or defeats a candidate. Topology alone cannot identify the answer; typed relation semantics can.

In the transport family, typed endpoints are held fixed while local affine map values change. The target depends on whether the composed cycle is identity. Without map values, the worlds collide. With the current view, the information is present.

In the history family, current typed state is held fixed while admitted scoped negative history changes. Only the semantic view contains the decisive coordinate.

The simple-learning results respect every computed ceiling. Surface and topology reach 0.5 at ceilings of 0.5. Typed features reach 0.666667 at the same ceiling. The current view reaches 0.670139 against an overall ceiling of 0.833333, and the semantic view reaches 0.836806 against a ceiling of one.

The decomposition explains the remaining gap. Semantic mechanic selection reaches one, whereas affine gluing remains 0.510417 despite a task ceiling of one.

## 6. Explicit computation closes the gluing residual

A frozen payload-only procedure reconstructs the visible affine cycle and composes the local maps exactly. With typed endpoints but no map values, it remains unresolved. Once the maps are visible, it reaches accuracy one.

The result identifies the missing operation in this finite family. The information-sufficient view does not automatically make global composition accessible to the selected generic learners. An explicit algorithm closes the residual without a neural architecture.

Parallel controls produce the same structure. Typed relation semantics and admitted negative history close their exact hostile pairs through simple explicit selectors. These controls show that the coordinates are load-bearing; they do not show that neural relation or memory modules are necessary.

## 7. Whole-domain procedural transfer

A second study trains on numerical methods and graph algorithms, then holds out the entire domain of transactional workflows. Surface action identities are reminted and domain-disjoint.

The strongest retained comparison is typed relational structure versus untyped pair structure. Typed relational features score
\[
1.0000,
\]
while the untyped comparator scores
\[
0.90625.
\]
On the same 128 protected cases, 12 are correct only for the typed arm and none are correct only for the untyped arm.

A post hoc case-level exact test gives \(p\approx0.000488\), and a case bootstrap interval for the accuracy difference excludes zero. These calculations treat 128 mutated cases as independent. The family identifiers needed for cluster-valid inference are absent, so the paper does not use the case-level interval as a population claim. The exact protected contrast and zero reversals remain descriptive evidence that typed relation labels matter on this panel.

## 8. Withdrawn comparators and negative results

Two larger transfer margins do not survive hostile review.

A reminted transcript arm predicts the majority class on all protected cases. Its apparent 0.75 gap is therefore not a comparison between two functioning transferable representations.

A same-information serialization contains the typed payload, but a bijection of its symbol alphabet changes 32 of 128 predictions and moves accuracy from 0.75 to 0.50 while preserving semantics. Its margin depends on the chosen feature keys. The claim that explicit relational organization caused that difference is withdrawn.

Other adverse evidence remains visible. A registered monotone scaling hypothesis for a language-model family is negative: only the smallest scale is non-degenerate, its primary-budget contrast is \(-0.141\), and the two larger scales collapse to a constant label in both arms. In a real same-information accessibility intervention, breast-cancer and digits cells are positive while wine is a retained null.

An invariant-orbit analysis finds no indication for a representation successor. Training and protected data share no orbit cell, so the apparent invariant ceiling gap is a coverage transition rather than evidence that refining the representation would solve the problem. A separate frontier grid executes zero cells and carries no scientific result.

## 9. What is established

The evidence supports four bounded conclusions.

1. Exact view collisions can identify when a failure is informational on a frozen sample.
2. Simple learners and same-information interventions can separate accessibility from missing content.
3. Explicit computation can close a residual when the necessary coordinates are visible.
4. Typed relational coordinates improve exact protected transfer over a strong untyped comparator on one whole-domain holdout.

The evidence does not establish general superiority of the diagnostic, neural necessity, universal structured transfer, monotone scaling, or cluster-valid population effects.

## 10. Limitations

The experiments are small, exact, and deliberately constructed. Several comparisons use generated mutations rather than independent task families. The strongest family-level diagnostic panel has only five units. External naturalistic validation is limited, and one real-data cell is null.

The explicit procedures exploit transparent task structure. Their success does not imply that every computational residual admits a known symbolic closure. The collision ceiling is sample-specific and depends on a correctly declared model-visible view.

## 11. Conclusion

Learning failure should be diagnosed before compute is escalated. Exact view collisions reveal missing information; simple-model and same-information interventions expose accessibility; and explicit procedures can identify computational residuals. The controlled evidence shows all three cases and preserves the outcomes that narrow the claim: a five-family comparison too small for population inference, a null accessibility cell, a failed scaling hypothesis, withdrawn degenerate comparators, and an unexecuted frontier. The resulting methodology is useful because it chooses the intervention class that the evidence supports and permits `CANNOT_CHECK` when it does not.
