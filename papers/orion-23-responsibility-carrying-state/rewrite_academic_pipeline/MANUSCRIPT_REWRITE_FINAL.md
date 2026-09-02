# Three-Valued Responsibility Transport under Incomplete Premise Status

## Abstract

A scientific conclusion may remain reusable after its context changes only if every load-bearing premise remains satisfied. In practice, a premise can be confirmed unchanged, contradicted, or unresolved because the required measurement or execution does not exist. Collapsing the unresolved state into either positive or negative evidence creates two different errors: optimistic reuse can preserve an unsound conclusion, whereas pessimistic revocation can discard support that was never refuted.

We formalize responsibility transport with three premise states—`UNCHANGED`, `CONTRADICTED`, and `UNKNOWN`—and evaluate every status assignment over three or four load-bearing premises. Each `UNKNOWN` premise carries a hidden actual value that the transport rule cannot observe, and every such premise is resolved both ways in the exact evaluation. Across 750 cases, the three-valued rule makes zero unsound transports and zero unnecessary revocations, while returning 296 abstentions. An optimistic two-valued collapse (`UNKNOWN`→`UNCHANGED`) is unsound 212 times. A pessimistic collapse (`UNKNOWN`→`CONTRADICTED`) is sound but over-revokes 84 times. Within the registered rule class, the three-valued transport law is the unique rule with zero of both error types.

A positive-control failure exposed a defect in the first ground-truth instrument: `UNKNOWN` had been defined as unsound by construction, making pessimistic revocation tautologically optimal. The instrument—not the claim—was repaired by adding hidden actual premise values while keeping the frozen claims, margins, and controls unchanged. A retrospective 31-repository corpus illustrates the same boundary but contributes no prospective evidence because its outcomes were already accessed.

The contribution is a formal transport law for bounded scientific state, not an empirical safety claim. `UNKNOWN` is a distinct epistemic terminal with a real operational cost: abstention is necessary when the available state does not determine whether support survives.

## 1. Introduction

Scientific workflows reuse results across time. A dataset is reprocessed, a software dependency changes, an evaluator is replaced, or a measurement protocol moves to a new environment. Some prior conclusions remain valid. Others must be revoked. A third group cannot yet be decided because a premise needed to transport the conclusion has not been measured in the new context.

Binary transport policies force that third group into one of two interpretations. An optimistic policy treats missing evidence as unchanged and carries the conclusion forward. A pessimistic policy treats missing evidence as failure and revokes the conclusion. Both choices can be operationally convenient, but neither is generally sound and non-wasteful.

We study the exact finite decision problem underneath this engineering choice. A scientific artifact is supported by several load-bearing premises. Each premise has an observed transport status and, when observed as `UNKNOWN`, an actual hidden status that determines whether reuse would be scientifically sound. The decision rule sees only the observed status. The evaluator sees the hidden status solely to score soundness and waste.

The main result is a no-free-collapse law: no two-valued treatment of `UNKNOWN` avoids both unsound reuse and unnecessary revocation. A three-valued rule avoids both by abstaining on the states that available evidence does not identify.

## 2. Responsibility-carrying scientific state

A reusable scientific object consists of a claim or certificate together with a support set of premises. Premises may concern data identity, measurement semantics, transformation validity, model assumptions, execution environment, evaluator custody, or another obligation required by the claim.

For transport from an old state to a new state, each premise receives one observed status:

- `UNCHANGED`: admissible evidence establishes that the premise still holds;
- `CONTRADICTED`: admissible evidence establishes that the premise no longer holds;
- `UNKNOWN`: available evidence establishes neither outcome.

A conclusion is sound to reuse exactly when every premise is actually satisfied in the new state. `UNKNOWN` therefore does not describe the truth of a premise. It describes the evidence available to the decider.

This separation is essential. If `UNKNOWN` is defined as false, pessimistic revocation becomes correct by construction and the scientific question disappears. If it is defined as true, optimistic reuse becomes correct by construction. A meaningful evaluation needs hidden actual values behind unresolved observations.

## 3. Three transport rules

The registered comparison contains three deterministic rules.

### 3.1 Three-valued transport

- Reuse when every premise is observed `UNCHANGED`.
- Revoke when at least one premise is observed `CONTRADICTED`.
- Abstain when no premise is contradicted and at least one is `UNKNOWN`.

### 3.2 Optimistic collapse

Map `UNKNOWN` to `UNCHANGED`, then reuse unless a premise is explicitly contradicted.

### 3.3 Pessimistic collapse

Map `UNKNOWN` to `CONTRADICTED`, then revoke whenever any premise is unresolved or contradicted.

The three-valued rule is not a compromise between the other two. It preserves a distinct decision state because the observable information does not determine the correct binary action.

## 4. Exact evaluation design

The finite campaign enumerates support sets with three or four load-bearing premises. Every observed status assignment is included. Each `UNKNOWN` premise is assigned both possible hidden actual values—satisfied and violated—while the decision rule remains blind to that assignment.

This construction yields 750 exact cases. The endpoints are:

- **unsound transport:** a rule reuses a conclusion while at least one hidden actual premise is violated;
- **unnecessary revocation:** a rule revokes a conclusion while every hidden actual premise is satisfied;
- **abstention:** a rule returns neither reuse nor revocation because the visible state is insufficient.

The evaluation is exhaustive for the registered premise counts and rule definitions. The 750 rows are not treated as an open-population sample.

## 5. Results

| Rule | Unsound transports | Unnecessary revocations | Abstentions |
|---|---:|---:|---:|
| Three-valued | 0 | 0 | 296 |
| Pessimistic collapse | 0 | 84 | 0 |
| Optimistic collapse | 212 | 0 | 0 |

The optimistic rule obtains complete coverage by assuming that unresolved premises remain valid. It is wrong in 212 cases where at least one hidden premise is violated. The pessimistic rule avoids unsound reuse by assuming unresolved premises fail. It revokes 84 cases in which every hidden premise remains satisfied.

The three-valued rule avoids both error types. Its cost is 296 abstentions: states in which no contradiction is visible but the conclusion is not established to remain valid.

## 6. No two-valued rule is both sound and non-wasteful

Consider any observable state containing one or more `UNKNOWN` premises and no `CONTRADICTED` premise. There exist two hidden worlds compatible with that same observation.

1. Every unknown premise is actually satisfied. Reuse is sound, and revocation is unnecessary.
2. At least one unknown premise is actually violated. Reuse is unsound, and revocation is necessary.

A deterministic binary rule must return the same action in both worlds because their observations are identical. If it reuses, it is unsound in the second world. If it revokes, it is wasteful in the first. Therefore no binary rule over the observed statuses can be both sound and non-wasteful on all admissible worlds.

The three-valued rule is exact because it returns `UNKNOWN` on precisely these observational fibres. Within the registered semantics, it is the unique rule with zero unsound transports and zero unnecessary revocations.

This is an information theorem, not a claim that every system must expose the same API. A product using an equivalent three-way distinction should tie extensionally.

## 7. The control that found a defect

The first execution returned `CANNOT_CHECK` because the registered positive control required pessimistic collapse to over-revoke at least once, but no such case appeared. Investigation showed that the ground truth had defined reuse as sound only when no premise was `CONTRADICTED` or `UNKNOWN`. Under that definition, unresolved premises were definitionally invalid, so pessimistic revocation could never be wasteful.

The control had detected a tautology. The frozen claim already referred to “unnecessary revocation,” which requires worlds where an unresolved premise may in fact remain satisfied. The repair therefore changed the evaluator, not the hypothesis: each `UNKNOWN` observation was given a hidden actual value, and every value assignment was enumerated. Claim wording, decision rules, thresholds, and control logic were not changed after outcome.

This episode is part of the scientific contribution. A benchmark that contains only negative controls can pass while measuring a definition chosen to favour the focal rule. A positive demonstration of the comparator's expected failure exposed the defect before release.

## 8. Retrospective external corpus

A separate corpus records 31 pinned repositories across 14 organizations, 123 decided facts, and 32 `CANNOT_CHECK` facts. In those unresolved cases, the exact per-repository runtime required by the contract does not exist; an exit status obtained through another environment is not the same premise.

The corpus illustrates the semantics of `UNKNOWN`: the required fact is absent, not contradicted. It does not validate the transport law prospectively because the outcomes were accessed before a frozen test was run. The manuscript therefore treats it as a labelled boundary observation only.

The broader deployment claim remains open. Exact formal transport on finite premise systems does not establish the frequency, cost, or downstream benefit of abstention in real organizations.

## 9. Relation to prior work

Three-valued logics, partial information, truth-maintenance, provenance, dependency-directed invalidation, selective revalidation, abstention, and robust decision-making are established donor areas. The paper does not claim the general existence of an unknown truth value or the idea that incomplete information should trigger abstention.

The residual contribution is the exact responsibility-transport object: soundness and waste are scored against hidden premise truth; the two binary collapses fail in opposite directions; the three-valued rule is characterized as the unique zero-error decision on the registered state space; and the evaluation history demonstrates how a positive control can detect tautological gold.

## 10. Claim ceiling

The current evidence supports:

- an exact three-valued transport law for support sets of three and four premises;
- zero unsound reuse and zero unnecessary revocation across all 750 registered cases;
- impossibility of a universally sound and non-wasteful binary collapse over the same observations;
- a necessary abstention set of 296 cases under the registered distribution of exact states;
- a benchmark-design lesson about hidden actual values behind unresolved observations.

It does not support:

- empirical safety or cost savings in deployed scientific systems;
- a claim that all premise ontologies are complete;
- forward-time validation on the 31-repository corpus;
- the separate self-scored P13A safety endpoint;
- universal minimality of this particular status vocabulary.

## 11. Reproducibility

The release should include the frozen claim and rule definitions, the complete 750-case generator, hidden-value construction, exact result table, original `CANNOT_CHECK` terminal, repaired evaluator, positive and negative controls, and the retrospective corpus with an explicit non-authority label. Every case should be reproducible without consulting repository-development history.

The manuscript-facing package should use scientific premise names rather than internal experiment identifiers. The full artifact can preserve hashes and chronology receipts.

## 12. Limitations and next valid study

The formal universe contains small support sets and binary hidden truth for each unresolved premise. Real scientific premises may interact, have graded validity, or require institutional judgment. Abstention can also be costly, and a deployed policy may rationally acquire evidence before returning a terminal.

A valid empirical successor would freeze organization-disjoint repositories and objective native verifiers before outcomes, then measure both false retention and avoidable recomputation. If the design cannot provide the required runtime or custody premise, the correct terminal remains `CANNOT_CHECK` rather than an improvised substitute.

## 13. Conclusion

An unresolved premise is neither confirmed nor refuted. Treating it as confirmed makes responsibility transport unsound; treating it as refuted wastes still-valid support. Across the complete registered state space, the optimistic collapse is unsound 212 times and the pessimistic collapse over-revokes 84 times. The three-valued rule avoids both errors by abstaining 296 times. This abstention is not indecision added for caution. It is the exact response to an observational state compatible with opposite scientific truths.