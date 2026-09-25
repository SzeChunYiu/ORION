# Where Should Test-Time Computation Be Spent? A Bounded Cross-Domain Resource-Location Law

**ORION-22 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** equal-action signal complementarity, exact cross-domain transfer, and adverse robustness boundary  
**Primary route:** TMLR  
**Specialist fallback:** AIJ Research Note  
**Authority:** bounded internal exact domains; external/public-data transfer open

## Abstract

Adaptive test-time computation is usually framed as deciding how much reasoning to perform. State construction creates a second place to spend the same resource: computation can expose task-relevant structure before reasoning or support search over a less processed state afterward. We study this **resource-location** problem under matched budgets and explicit comparator repair.

An initial controlled benchmark appeared to show a large advantage for joint state–reasoning allocation, but a hostile audit found that the winning arm could emit four allocations while each one-axis comparator could emit only two. Their attainable ceilings lay below the winner's observed score, so the superiority interpretation is permanently withheld. A prospectively frozen equal-action successor gives every arm the same four allocations and two-unit budget. Across 32 independent family blocks, the two-signal policy improves exact allocation accuracy by 0.253906 over the stronger one-signal policy, with a stratified family-block 95% interval of 0.251221 to 0.256653.

The main transfer study applies one unchanged allocator to nine protected cases spanning SAT unit propagation, 15×15 path planning and 0/1 knapsack. The rule reads only pending multiplicity, declared materialization cost and the common budget; no domain-specific parameter or case identity is supplied. All arms produce independently verified exact task outputs. The frozen allocator matches the per-case hindsight resource-location oracle in 9/9 cases, while `REASON_ONLY` and `STATE_ALWAYS` each incur positive regret in every domain. A structurally separate implementation re-derives case truth, choices and regret, and the allocator parameters are byte-identical across domains.

The boundary is equally important. A preregistered robustness battery shows that the original q-greedy allocator is not robust to price or distribution shift. A separately frozen price-aware successor attains zero priced regret in all 195 registered battery cells when exact per-structure charge certificates are supplied. Whether those certificates are available before action remains `CANNOT_CHECK`. The contribution is therefore a bounded resource-location law and comparator discipline, not universal allocation optimality, price robustness or deployed-agent superiority.

## 1. Introduction

Test-time scaling asks how much computation a system should devote to a difficult instance. More tokens, samples, search nodes or verifier calls can improve performance, but the value of more reasoning depends on which structure is already exposed in the state. Some tasks are difficult because the relevant structure is hidden or expensive to materialize. Others remain difficult even after the right structure is available.

This creates two competing loci for the same resource:

`current state -> state construction -> reasoning/search -> verified outcome`.

A system must decide not only **how much** computation to spend but **where** to spend it.

Adaptive inference, metareasoning, routing, value-of-information methods, retrieval and dynamic context construction already own the underlying primitives. The residual question is stricter:

> Under a matched resource boundary, can one rule choose the valuable locus of computation across different exact task classes, and can the result survive capability-matched controls and adverse robustness tests?

The answer requires a sequence of corrections rather than one favorable benchmark. The first apparent superiority result fails because action capability is unmatched. The equal-action successor isolates the value of observing both resource demands. The transfer study then tests one domain-invariant allocation rule. A final robustness study identifies when that rule breaks and what additional information closes the registered battery.

## 2. Resource-location problem

For item `i`, let `c_i` be resource spent constructing or materializing state and `r_i` resource spent on downstream reasoning. In the controlled model,

`c_i + r_i <= B`.

A real system may require a vector resource receipt covering state bytes, model calls, search nodes, verifier calls, latency, compiler operations, memory, cache and recovery. A scalar comparison is valid only when the scalarization is fixed before protected outcomes. Otherwise the scientific result should be a Pareto frontier.

The comparison classes include:

- fixed allocation;
- state-only adaptation;
- reasoning-only adaptation;
- joint allocation;
- a hindsight joint oracle used only for evaluation.

A valid joint result must hold total budget, action set and information opportunity fixed. Equal budget without equal action capability is not a causal comparison.

## 3. Historical comparison correction

The first protected benchmark contains 16 held-out generated families under a two-unit budget. The joint arm obtains mean verified success 0.858154, apparently far above the named one-axis arms.

The arms are not capability-matched. The joint policy can choose among

`(0,0), (2,0), (0,2), (1,1)`,

whereas each one-axis comparator can emit only two allocations. Their perfect-signal ceilings are below the joint arm's achieved score. The large margin therefore entangles signal access with action-set advantage.

The execution record remains valid. The superiority inference does not. Its active disposition is withheld, and no later positive result relabels it.

This correction supplies a general benchmark rule: a baseline cannot establish the value of an additional signal when it is also denied actions needed to exploit that signal.

## 4. Equal-action signal complementarity

A prospectively frozen successor gives every adaptive arm the same four actions and the same two-unit budget. The only intended difference is which pre-outcome resource-need signals are visible. The endpoint is exact allocation accuracy, and the independent unit is the family random-generator block rather than the individual generated episode.

Across 32 independent family blocks, the two-signal policy improves over the stronger one-signal arm by

`0.253906`,

with a stratified family-block 95% bootstrap interval

`[0.251221, 0.256653]`.

The minimum family gain is 0.196289, and every fixed noise stratum has a positive mean gain. Locked-environment revalidation reproduces the result.

This establishes a controlled complementarity fact: after budget and actions are matched, observing both state-construction need and reasoning need improves exact allocation in the registered generated families. It does not establish naturalistic or cross-domain superiority.

## 5. From signal complementarity to a common rule

The stronger question is whether one rule can locate marginal computation across qualitatively different exact tasks.

The transfer allocator reads only:

1. pending multiplicity — the unresolved structure that state materialization can reduce;
2. the declared cost of that materialization;
3. the shared budget.

No domain-specific hyperparameter, task name or protected case identity is visible. The same bytes are used in SAT propagation, grid path planning and knapsack.

Every arm must produce the independently verified exact task answer. Allocation quality is scored only after correctness is established, so a cheaper but wrong arm cannot win.

## 6. Nine protected cross-domain cases

The transfer battery contains nine cases across three domains:

- SAT unit propagation;
- 15×15 path planning;
- 0/1 knapsack.

The unchanged allocator matches the per-case hindsight resource-location oracle in every case:

`zero location regret in 9/9`.

Both fixed-locus restrictions incur positive regret in every domain. `REASON_ONLY` wastes budget where a small materialization exposes decisive structure. `STATE_ALWAYS` pays construction cost in cases where downstream reasoning is already the cheaper locus.

A structurally separate checker re-derives each exact task output, the available actions, chosen allocation and regret. Every arm×case cell emits the same resource-vector schema, and the allocator parameters are byte-identical across domains.

The result is exact for the registered nine cases. It is not an estimated open-population success rate and does not prove universal optimality.

## 7. Why a small exact transfer study is informative

The case count is small, but the scientific object is sharply controlled.

First, task correctness is independently verified, separating resource location from answer quality. Second, the rule is unchanged across domains and reads only domain-agnostic resource coordinates. Third, the fixed-locus donors fail in opposite directions, demonstrating that neither state construction nor reasoning is uniformly preferred.

The evidence therefore supports existence and bounded transfer of a common resource-location law. It does not establish its frequency of success on naturally occurring tasks or its robustness under unknown prices and shifts.

## 8. Robustness battery: the first allocator breaks

A preregistered battery perturbs resource prices and instance distributions. The original q-greedy allocator fails both axes. The result remains negative; the allocator is not retuned after outcome into a positive robustness claim.

This distinguishes three scientific properties:

- transfer across task mechanics under one charging model;
- robustness to changed charging coefficients;
- robustness to changed task frequencies.

The nine-case transfer supports the first. It supplies no authority for the latter two.

## 9. Price-aware successor and certificate boundary

A separately frozen successor is allowed to read exact per-structure charge certificates. It selects the exact budget-feasible action under the declared prices. Two independent implementations agree, and the price-aware rule attains zero priced regret in all 195 frozen battery cells.

The result is conditional:

> Exact charge fields are sufficient for exact selection in the registered additive environment.

A matching necessity analysis supplies a witness for every registered coarsening of those fields: if the coarsened observation merges structures requiring different actions, no selector restricted to that observation is guaranteed correct everywhere.

The forward-time availability of exact charges is unresolved. A deployment claim would require evidence that the certificates exist before action, can be acquired at acceptable cost and remain correct under the relevant environment. The present result does not manufacture that premise.

## 10. Censoring and information limits

Resource ceilings create another common inference error. When an arm reaches an exact cap without success, the observation is censored: the required resource may exceed the cap. A cap hit is not proof of impossibility.

Likewise, if two worlds look identical to the allocator but require different resource locations, no deterministic policy restricted to that observation can be exact in both. Positive unavoidable regret is then an information boundary, not evidence that the optimization algorithm is weak.

The paper keeps `CANNOT_CHECK`, censored and exact-negative states distinct.

## 11. Resource accounting

A real comparison should bind at least:

- model and tool identities;
- state-construction calls, tokens and bytes;
- downstream reasoning/search operations;
- verifier calls;
- end-to-end latency;
- cache, invalidation and recovery cost;
- any model-capacity differences;
- reproducible energy only when it is actually measured.

A state-heavy arm cannot hide preprocessing upstream, and a reasoning-heavy arm cannot receive a larger model or search cap. When resource dimensions are not commensurable under a prospectively justified scalarization, the correct scientific display is a quality–resource frontier.

## 12. Relation to prior work

Metareasoning, adaptive inference, budgeted planning, routing and value-of-information methods already optimize test-time resources. Retrieval, compilation and state construction already alter what a reasoner sees. The paper does not claim either axis as new.

The residual is their **matched co-design** under one resource contract, the explicit correction of an invalid capability comparison, and a cross-domain exact test of one unchanged resource-location law. The price-aware successor additionally makes the information requirement for robust selection explicit rather than hiding it as an oracle assumption.

## 13. External/public-data boundary

A stop/go public-data campaign has been frozen with symmetric action and signal menus and with the adverse robustness results carried as binding priors. It has not executed. No runner output, metric or terminal exists.

The protocol contributes no empirical authority. It records the next valid route to naturalistic transfer without rewriting the present claim after outcomes.

## 14. Limitations

The cross-domain result contains nine exact cases. The domains are heterogeneous but engineered for verifiable outputs. The first allocator fails price and distribution robustness. The successor depends on exact charge certificates whose prospective availability is unknown. Scalar resource units are clean by construction and do not establish a universal exchange rate among real tokens, latency, memory and tool calls.

No claim is made about LLMs, deployed research agents, universal metareasoning optimality or real-world resource savings.

## 15. Reproducibility and availability

The release should bind the invalid historical comparison and its capability audit, equal-action protocol, 32 family-block result, nine transfer cases, exact task verifiers, common allocator bytes, independent checker, robustness negative, 195-cell price-aware result and charge-field necessity witnesses. The unexecuted public-data protocol should remain clearly labelled as prospective only.

## 16. Conclusion

State construction and reasoning are competing places to spend test-time computation. A valid comparison must match both actions and budget. After correcting an invalid historical contrast, an equal-action study establishes signal complementarity, and a stronger transfer study applies one unchanged allocator to SAT propagation, path planning and knapsack. The rule matches the hindsight location oracle in all nine protected cases while fixed-locus policies incur regret in every domain.

The robustness result prevents overgeneralization. The first allocator breaks under price and distribution shift; exact performance returns only when exact charge certificates are supplied. The supported law is therefore bounded and information-indexed: resource location can transfer across exact domains, but robust allocation depends on what the decision interface is allowed to know.

---

## Editorial production note — not manuscript prose

Adoption must reconcile this master with `CLAIM_EVIDENCE_LEDGER.md`, `P12_ACTIVE_CLAIM_AUTHORITY_V5.json`, the equal-action V1.1 revalidation, transfer receipt, robustness negative and price-aware/necessity receipts. Rebuild the TMLR or AIJ source, figures, bibliography, anonymous/named surfaces, archive and PDF. Do not cite the unexecuted public-data campaign as an empirical result or restore the invalid P12A superiority interpretation.
