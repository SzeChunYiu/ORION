# When Structure Is the Model: Separating Information, Learning, Computation, and Transfer

## Abstract

A learning system can fail for at least three different reasons: the representation may omit information required by the task; a learner may fail to exploit information that is present; or the residual operation may be computational rather than statistical. We develop a frozen diagnostic hierarchy for distinguishing these cases before escalating model complexity. The studies use exact synthetic and procedural method-structure tasks in which observational collisions provide deterministic ceilings on the frozen sample, generic classical learners receive first right of refusal, and an explicit-inference control is introduced when an information-sufficient view leaves a residual.

In the first study, surface and topology-only views remain at 0.500 accuracy and their exact deterministic ceilings are also 0.500. A typed view reaches 0.666667, while the current structured view reaches 0.670139 against a ceiling of 0.833333. A semantic view reaches 0.836806 and supports perfect mechanic selection, but affine gluing remains at 0.510417 despite a ceiling of 1.000000. Exact affine composition closes that residual, locating the remaining difficulty in computation rather than missing information. In a whole held-out domain of transactional workflows, typed relational comparisons reach 1.000 protected accuracy. Untyped pair structure reaches 0.906250, a same-information typed serialization reaches 0.500000, and reminted transcript features reach 0.250000—the majority-class base rate—because the transcript vocabulary creates new instance-specific symbols that cannot transfer.

The paper does not introduce a new graph, sheaf, neuro-symbolic, or latent architecture. Its contribution is a bounded evaluation method and evidence object: compute representation ceilings, test simple learners, apply explicit inference where justified, and reserve architecture escalation for residuals that survive those controls. The positive evidence is exact on the registered tasks; broad naturalistic transfer and universal claims about structured representations remain open.

## 1. Introduction

When a model underperforms, architecture is often the first variable changed. A larger network, more expressive kernel, or specialized relational model may improve the score, but the improvement can leave the scientific cause unresolved. The original representation may have merged task-distinct cases, making the target unlearnable from that view. Alternatively, the view may contain the necessary information while the learner lacks the computation needed to combine it. A third possibility is that a representation works inside one domain because its symbols recur there but fails on a new domain where those symbols are reminted.

These failure modes require different repairs. Missing information calls for a new observable or representation. Learnability failure calls for a better inductive bias or more data. A computational residual may be closed by an explicit algorithm instead of a larger statistical model. Transfer failure calls for a representation whose identities and relations survive domain change.

We propose a diagnostic order:

\[
	ext{information ceiling}
ightarrow	ext{simple learner}
ightarrow	ext{explicit inference}
ightarrow	ext{architecture escalation}.
\]

The sequence is designed to give strong donor mechanisms first right of refusal. If a deterministic ceiling is below the desired endpoint, no learner can repair the view. If the ceiling is high but a simple learner fails, an explicit operation may reveal that the residual is algorithmic. If a rich in-domain representation collapses on a held-out domain, the failure may lie in symbol transport rather than model capacity.

## 2. Four diagnostic questions

For a frozen task and representation \(Z=\phi(X)\), the paper asks four questions.

1. **Information:** do two examples with the same visible representation require different labels? If so, the view has a deterministic collision floor.
2. **Learning:** when the view is information-sufficient, can standard learners exploit it under the registered sample and model budget?
3. **Computation:** can a transparent task-specific operation close a residual left by the learner without adding information?
4. **Transfer:** are the representation's identities and relations stable on a held-out domain, or are features minted in a way that cannot recur?

These questions are evaluated separately. A view that has a high ceiling but poor learned accuracy is not called information-deficient. A view whose vocabulary cannot match across domains is not credited as “same information” merely because it contains detailed text.

## 3. Exact empirical ceilings

For a fixed sample, a representation partitions examples into observational cells. A deterministic classifier must assign one label within each cell. The empirical deterministic ceiling is therefore obtained by taking the majority label in every cell. This ceiling is exact for deterministic prediction from the frozen representation on the frozen sample.

The ceiling is not a population Bayes limit, and it does not prove that a future stochastic or enriched representation cannot perform better. Its role is diagnostic: when learner accuracy equals a low ceiling, architecture escalation cannot recover distinctions absent from the visible state. When accuracy is far below a ceiling of one, information is present and another explanation is required.

## 4. Study M1: progressively structured views

The first frozen study presents the same method-structure tasks through several views.

- The **surface** view exposes local tokens without the relations needed to identify the method.
- The **topology** view exposes coarse connectivity while omitting task-relevant types.
- The **typed** view adds relational type distinctions.
- The **current structured** view exposes a richer but still incomplete state.
- The **semantic** view exposes the relations needed to distinguish method mechanics and affine composition obligations.

The surface and topology views both achieve 0.500000 accuracy, exactly matching their deterministic ceilings of 0.500000. These are information failures: examples requiring different decisions are observationally identical.

The typed view reaches 0.666667, also matching its exact ceiling. The current structured view reaches 0.670139 against a ceiling of 0.833333, showing both remaining collisions and unused visible information. The semantic view reaches 0.836806 against a ceiling of 1.000000.

The aggregate semantic score hides an important decomposition. Mechanic selection reaches 1.000000. Affine gluing reaches only 0.510417, even though the semantic ceiling for gluing is 1.000000. The same low gluing score appears under the current structured view. The representation therefore contains enough information; the residual is not an observational collision.

## 5. Explicit inference closes the gluing residual

The gluing task requires composing affine relations rather than merely recognizing a method label. A separately frozen exact affine-composition procedure receives the same semantic inputs and performs the explicit operation. It closes the residual.

This result changes the interpretation of the failed learner. A more complex statistical architecture might also learn the operation, but the scientific object is already identified: the view is sufficient, and the missing step is exact composition. The explicit control therefore receives priority over a claim that a neural or relational architecture is necessary.

The study supports a computational diagnosis, not a universal argument for symbolic methods. On another task, the relevant operation may be noisy, unavailable, or too expensive to specify explicitly. Here the exact task structure makes the control appropriate.

## 6. Study D1: whole-domain transfer

The transfer study withholds an entire transactional-workflow domain. The training domains and held-out domain use the same underlying task semantics but can differ in surface vocabulary and instance identities.

Four representations are compared.

1. **Typed relational comparisons** preserve the scientific roles and pairwise relations needed by the decision.
2. **Untyped pair structure** preserves relational incidence but removes type distinctions.
3. **Typed serialization** contains the same typed information in a sequential encoding that changes the learner's access pattern.
4. **Reminted transcript features** encode detailed instance transcripts but create a fresh symbol vocabulary for each instance.

On the held-out domain, typed relational comparisons reach 1.000000 protected accuracy. Untyped pair structure reaches 0.906250. Typed serialization reaches 0.500000, and reminted transcript features reach 0.250000, the majority-class base rate.

The paired advantage of typed relations over untyped structure is 0.093750, with a paired interval from 0.046875 to 0.148438 and 12 discordant wins against no losses. Against typed serialization, the advantage is 0.500000, with interval 0.414062 to 0.585938 and 64 wins against no losses. Against reminted transcripts, the advantage is 0.750000, with interval 0.671875 to 0.820312 and 96 wins against no losses.

## 7. Why detailed transcripts fail to transfer

The transcript representation is not weak because it contains too little text. It fails because its symbols are minted per instance. The held-out domain contains no reusable vocabulary with which the learner can connect a new transcript to previously observed decisions. The resulting classifier is constant and returns the majority class.

This is a representation-identity failure. Adding more parameters to the same vocabulary interface cannot create cross-domain symbol recurrence. The repair is to expose transportable relations or a principled alignment, not merely to enlarge the downstream learner.

The typed serialization result supplies a different warning. It is described as same-information because the typed facts are retained, yet performance drops to 0.500000. Information equivalence does not imply equal learnability under a fixed learner and sample. The arrangement of information changes the inductive problem.

## 8. Donor absorption and novelty boundary

Graphs, typed relations, sufficient representations, neuro-symbolic learning, relational learning, invariant representations, program induction, and explicit inference are mature donor areas. The paper does not claim that structure matters, that typing can help, or that exact composition can outperform a generic learner as new general principles.

The residual contribution is the controlled diagnostic hierarchy and the frozen evidence chain. Representation collisions are measured before model comparison; simple learners are tested before specialized architectures; a direct operation is used to distinguish computation from learnability; and transfer is evaluated on a whole held-out domain with both information and identity controls.

The intended use is methodological. A future architecture claim should survive the strongest information, donor, and explicit-computation explanations available for its task.

## 9. What is established

The evidence establishes the following bounded claims.

- Surface and topology-only views are information-insufficient for the registered M1 tasks.
- Typed and current structured views remove some, but not all, observational collisions.
- The semantic view contains enough information for exact M1 prediction, and simple learning solves mechanic selection but not affine gluing.
- Explicit affine composition closes the gluing residual without adding information.
- Typed relational comparisons transfer perfectly to the registered held-out workflow domain.
- Untyped structure loses a smaller but exact set of distinctions.
- Same-information serialization can remain difficult for the frozen learner.
- Per-instance transcript vocabularies fail to transfer and collapse to the majority class.

The evidence does not establish that one representation is universally optimal, that neural escalation is never useful, or that the registered tasks represent an open population of scientific reasoning problems.

## 10. Statistical and inferential discipline

The exact ceilings are deterministic finite-sample objects. Transfer differences are paired because every representation is evaluated on the same held-out cases. Intervals summarize paired disagreement under the registered analysis; they are not independent replications.

The whole domain—not individual rows sampled from it—is the substantive transfer unit. Reporting many case-level decisions must not inflate the claim into many independent domain replications. Likewise, perfect held-out accuracy is an exact result for the registered domain, not an estimate of universal generalization.

## 11. Reproducibility

A complete release should include the task generators, frozen splits, representation constructors, collision partitions, deterministic ceiling calculations, learner configurations, exact affine-composition control, held-out domain identities, paired result tables, and negative controls. Generated macros and headline tables should remain machine-derived from immutable result records.

The anonymous review package should expose scientific task names rather than internal project identifiers. Repository paths, workflow names, and development history belong in artifact documentation, not manuscript prose.

## 12. Limitations

The strongest evidence comes from exact synthetic and procedural tasks. Their advantage is clean causal diagnosis; their limitation is uncertain transfer to naturalistic learning systems. The semantic and typed representations are designed with knowledge of the task ontology. Constructing similarly faithful structures in noisy open worlds may be difficult or expensive.

The learner family is strong enough to provide first-refusal controls for the registered studies but does not exhaust every modern architecture. The paper's logic does not require such exhaustion: once an explicit operation closes a residual, the present evidence no longer licenses a claim that a novel architecture is scientifically necessary.

The held-out domain result is one domain-level transfer. Additional families, especially those with noisy or partially wrong type systems, are needed for broader claims.

## 13. Conclusion

Poor prediction should not automatically trigger a larger model. In the registered studies, some views fail because they merge task-distinct cases, one semantic view leaves a computational residual that exact affine composition closes, and a detailed transcript representation fails because its symbols do not survive domain change. Typed relational structure transfers across the held-out workflow domain, but same-information serialization remains learner-dependent. The resulting contribution is a disciplined diagnostic sequence: identify missing information, test ordinary learning, isolate explicit computation, and only then decide whether architecture escalation addresses a remaining scientific problem.