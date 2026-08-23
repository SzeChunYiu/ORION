# P9 top-tier promotion V1 — Representation Accessibility as a Scaling Coordinate

**Programme:** #977  
**Existing controlled authority:** `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR` remains valid for its bounded package.  
**Top-tier state:** `CAUSAL_DIAGNOSTIC_EARNED__FINAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Learning and reasoning scale along at least three separable coordinates: semantic information, representation accessibility and downstream computation.** Increasing model or inference resources is scientifically uninterpretable until these coordinates are disentangled. P9 provides a protected diagnostic methodology and seeks reproducible crossover laws among representation repair, explicit inference and model/compute escalation on real systems.

P9 does not reclaim graph inductive bias, serialization friction, generic representation-vs-reasoning distinction, domain generalization or a new neural architecture. Those remain donor-owned.

## Upward scientific object

Define a response surface over:

`Q = f(I, A, C, M)`

where:

- `I` = semantic task information available to the system;
- `A` = accessibility of that information under the frozen representation/interface;
- `C` = downstream computation/search/inference budget;
- `M` = model/access mechanism capacity.

The paper empirically separates interventions on these coordinates rather than inferring the cause of failure from final accuracy alone.

## Post-outcome status — 2026-08-23

Three protected result families now constrain the higher claim.

### Real-data same-information intervention — supported, bounded

`P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED` executed a prospectively frozen, bijective representation intervention on breast-cancer, wine and handwritten-digit data. The cubic representation preserves semantic information exactly; deterministic inverse repair reconstructs native features to floating-point roundoff. Under the frozen linear access class, the native-to-cubic accuracy gap is `0.0351808725` on breast cancer and `0.0239275766` on digits, while wine is a null/negative cell (`-0.0001587302`). Inverse repair restores the native linear mean exactly on the two preregistered positive datasets. The 180-row study is byte-replay deterministic.

**Earned claim:** accessibility can change under an information-preserving representation intervention for a fixed access mechanism, and explicit representation repair can recover that accessibility. The wine cell forbids a universal-dataset statement.

Wine and digits are shared programme infrastructure (wine also carries P7's transport rows and P11's compiler positive cell; digits also carry P11's 64→32 compiler and P13's parity→exact-digit episodes). The frozen quantities owned here are P9's own accessibility measurements: the wine null cell above, and the digits cubic-representation gap plus `D-A` diagnostic — distinct objects from the other papers' endpoints on the same public datasets.

### Protected Qwen2.5 model-size/inference sweep — negative

The immutable Qwen2.5 Q4_K_M 0.5B/1.5B/3B outputs originally generated on PR #618 were recovered without rerunning inference or changing any scientific threshold. The frozen analyzer deterministically returns `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`.

At primary budget 32, `R2_STRUCTURED_STATE - R1_SAME_INFO` is `-0.140625` for 0.5B and `0.0` for both 1.5B and 3B. The positive-delta-every-size gate fails, the largest-model domain-block bootstrap lower bound is not above zero, no smaller-structured substitution is observed, and the aggregate hostile-control gate fails; ORDER is negative at both 0.5B and 3B.

**Required claim subtraction:** P9 must not state or imply a universal monotone law in which larger LLM capacity reveals a stable typed-state accessibility advantage.

### Causal intervention diagnostic — supported with a protected CANNOT_CHECK cell

The prospectively frozen diagnostic study now returns `P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED`; a second implementation returns `P9_CAUSAL_DIAGNOSTIC_SECOND_INDEPENDENT_CHECKER_GREEN`, with exact decision agreement and deterministic replay.

The procedure does not assign failure labels from task names. On a probe split it applies one-coordinate interventions—`INFORMATION`, `ACCESSIBILITY`, `COMPUTATION`—and predicts the lowest-cost intervention that reaches a frozen quality target. On protected data the causal gold is recomputed independently from held-out intervention outcomes.

Across five task families in two qualitatively distinct domains:

- P9 diagnostic accuracy: `0.8` (`4/5`);
- generic `UNCERTAINTY_ESCALATE_COMPUTE` heuristic: `0.2` (`1/5`);
- exact executable tasks: `3/3` correct;
- digits tasks: `1/2` correct;
- false compute escalations: `0` for P9 vs `4` for the generic heuristic;
- mean registered intervention-cost regret: `0.0`;
- all actionable predicted interventions reach their frozen protected target.

The four stable diagnoses cover genuine missing information, representation accessibility and downstream computation. The fifth cell is intentionally retained as an instability: on digits task `D-A`, inverse representation repair clears the probe target (`0.9721448 >= 0.965`) but misses the protected target (`0.9555556 < 0.965`), so protected causal gold is `CANNOT_CHECK` while the probe-time diagnostic predicted `ACCESSIBILITY`.

**Earned claim:** P9 now has a bounded cross-domain causal diagnostic showing that intervention response can distinguish information/accessibility/computation failure substantially better than generic compute escalation, while correctly preserving a deployment-instability `CANNOT_CHECK` instead of retuning it away. **Not earned:** a universal LLM diagnostic, a claim that accessibility repair is always preferred, or a universal cross-system scaling law.

Exact authority is bound in `top_tier/P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md`; the earlier real-data and Qwen receipts remain equally binding.

## Protected real-system programme

### E9.1 — Same-information accessibility scaling

Executed at bounded scope through the real-data intervention and protected Qwen model-size/inference surface. The positive and negative surfaces must both remain in the manuscript.

### E9.2 — Causal diagnostic intervention

Executed at bounded scope. Failures are diagnosed from prospectively frozen intervention response and protected causal gold rather than post-hoc labels.

Scoping: this diagnostic is an ex-post attribution instrument, not an online policy (P12 owns pre-outcome regret-bounded allocation) and not a placement/optionality law (P11 owns the design-time resource-placement crossover); P9 claims neither placement-optimality nor runtime-allocation semantics.

### E9.3 — Cross-domain transfer of the diagnostic

The same diagnostic rule is now exercised across a non-synthetic digits domain and an exact executable/formal domain. This closes a bounded two-domain transfer requirement. A stronger open-weight procedural/agent transfer remains strengthening if the final headline explicitly targets LLM agents.

## Strong comparators

- model-size escalation;
- best-of-N / test-time search escalation;
- representation/context-selection baseline;
- graph/relational or native-state baselines relevant to the domain;
- explicit symbolic/deterministic inference where available;
- same-information serialization controls;
- oracle information ceiling only as diagnostic, not a runnable superiority baseline.

The causal study additionally includes the generic compute-escalation heuristic. All arms use frozen intervention semantics and report explicit resource coordinates; however, one unified programme-wide model/inference/representation cost vector is not yet complete.

## Primary endpoints

- verified/task success at matched information and resource budget;
- resource needed to reach a frozen quality target;
- diagnosis accuracy for information vs accessibility vs computation failure;
- false escalation rate to larger models/compute;
- transfer of the diagnostic policy across domains;
- interaction/crossover surface among `A`, `C` and `M`.

## Strongest hostile attacks

- structured view secretly contains extra semantic information;
- serialization is merely longer and loses due to context truncation;
- stronger model closes every effect, making accessibility non-distinct;
- explicit inference control is an oracle unavailable to realistic systems;
- post-hoc failure labels make diagnosis appear causal;
- cross-domain success comes from domain-specific tuning;
- probe-time diagnosis does not survive protected deployment data—the `D-A` cell demonstrates this can happen and is retained;
- result merely restates known representation or scaling effects without a separable diagnostic law.

## Top-tier promotion gate

`P9_TOP_TIER_SUBMISSION_READY` requires:

- [x] bounded same-information real-system/access-mechanism scaling surfaces executed, including an authoritative negative Qwen surface;
- [x] prospectively frozen one-coordinate causal accessibility intervention with deterministic inverse repair;
- [x] diagnosis accuracy above the frozen generic uncertainty/compute-escalation heuristic (`0.8` vs `0.2`);
- [x] at least two qualitatively distinct protected diagnostic domains (digits + exact executable);
- [ ] unified matched full model/inference/representation resource accounting for the final headline;
- [x] protected model-size and inference-budget comparators executed; their Qwen result is negative and retained;
- [x] exact preservation of the bounded P9 negative/sufficiency history;
- [x] no universal representation-superiority language, extended to no placement-optimality or online-policy language;
- [x] second independently implemented diagnostic verifier plus deterministic replay for the causal study;
- [ ] immediate pre-submission nearest-work refresh and exact final artifact/manuscript binding.

If the final manuscript headline is the demonstrated **causal diagnostic and crossover methodology**, the primary remaining internal scientific gap is unified resource accounting rather than another representation benchmark. If the headline claims universal LLM-agent transfer, an additional open-weight procedural/agent diagnostic domain remains necessary.

The protected `D-A` instability and Qwen negative are part of the contribution: they define where the diagnostic or scaling hypothesis does not transport.
