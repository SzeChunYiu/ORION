# A Bounded Law for Locating Test-Time Computation Across State Construction and Reasoning

## Abstract

Test-time computation can be spent before reasoning, by materializing task-relevant state, or afterward, by searching over a less processed representation. We study this resource-location problem under matched action sets, exact task verification, and explicit negative controls.

An initial benchmark is excluded from the main claim because the joint allocator could emit four allocations while each one-axis comparator could emit only two. A prospectively frozen equal-action successor repairs that asymmetry. Across 32 independent family blocks, a two-signal policy improves exact allocation accuracy over the stronger one-signal policy by 0.253906, with a family-block bootstrap interval of 0.251221 to 0.256653.

The stronger result applies one unchanged allocator to nine protected cases across SAT unit propagation, 15×15 path planning, and 0/1 knapsack. Every arm produces an independently verified exact task output. The allocator reads only pending multiplicity, declared materialization cost, and the common budget. It matches the per-case hindsight resource-location oracle in 9 of 9 cases, while both fixed-locus restrictions incur positive regret in every domain.

The law is sharply bounded. The original greedy allocator fails a preregistered price- and distribution-shift battery. A price-aware successor attains zero priced regret in all 195 registered cells when exact charge certificates are supplied, but prospective availability of those certificates remains unresolved. The paper therefore establishes exact conformance of one resource-location rule on a small cross-domain panel, not universal allocation optimality or deployed adaptation.

## 1. Introduction

Test-time scaling is usually described as deciding how much reasoning to perform. That framing treats the state presented to the reasoner as fixed. In many systems, however, computation can first retrieve, compile, materialize, or reorganize the state. The same budget can then be spent at two loci:
\[
\text{current state}
\longrightarrow
\text{state construction}
\longrightarrow
\text{reasoning}
\longrightarrow
\text{verified output}.
\]

The useful question is not whether either locus matters. Both are established. The question is whether one matched rule can decide where marginal computation should be paid across different exact problem classes.

A valid answer needs three safeguards. All comparators must have the same action capability. Task correctness must be separated from allocation cost. Price or distribution shifts must be tested rather than assumed away.

## 2. Resource-location contract

For item \(i\), let \(c_i\) be computation spent constructing state and \(r_i\) computation spent downstream. In the controlled setting,
\[
c_i+r_i\le B.
\]

Compared policies include fixed allocation, state-only adaptation, reasoning-only adaptation, and joint allocation. A joint policy can receive credit only against one-axis comparators that can emit the same allocations under the same budget.

The endpoint is resource-location regret subject to exact task correctness. A low-cost wrong answer is not a favorable allocation.

## 3. Historical comparator failure

The first protected benchmark appeared to give a large margin to joint allocation. The comparison was not capability matched. The joint arm could choose
\[
(0,0),\ (2,0),\ (0,2),\ (1,1),
\]
whereas each one-axis arm could choose only two actions. Their perfect-signal ceilings were below the joint score.

The historical execution remains part of the record, but it carries no superiority interpretation. The defect motivates the equal-action successor.

## 4. Equal-action signal complementarity

The repaired successor gives every adaptive policy the same four actions and two-unit budget. Policies differ only in which pre-outcome signals they receive.

Across 32 independent family blocks, the two-signal policy improves allocation accuracy over the stronger one-signal policy by
\[
0.253906,
\]
with family-block bootstrap interval
\[
[0.251221,0.256653].
\]
Every registered noise stratum has positive mean gain, and locked-environment replay reproduces the result.

This experiment establishes signal complementarity inside the generated family. It does not yet show that one allocation rule transfers across domains.

## 5. Domain-invariant allocator

The transfer allocator reads three quantities with the same meaning in every domain:

1. pending multiplicity, the amount of unresolved structure state construction can reduce;
2. the declared cost of that materialization;
3. the common budget.

No domain-specific threshold or case identity is supplied. The same parameters are used for SAT propagation, path planning, and knapsack.

A hindsight oracle identifies the lower-cost locus for evaluation only. It is not available to the allocator. Independent task checkers verify that all compared arms return the exact problem solution.

## 6. Nine-case cross-domain result

The protected panel contains nine cases, three from each domain:

- SAT unit propagation;
- 15×15 path planning;
- 0/1 knapsack.

The unchanged allocator matches the hindsight location oracle in all nine cases. Its observed resource-location regret is therefore zero on the complete registered panel.

Both fixed-locus restrictions incur positive regret in every domain. The failures point in complementary directions: some cases benefit from paying to expose structure first, while others are better served by spending the budget downstream.

The result is exact panel conformance. Nine engineered cases do not define a population, support a sampling interval, or prove universal optimality. The scientific content is the cross-domain invariance of the registered decision variables and the fact that the two fixed-locus donors fail on both sides of the boundary.

## 7. Robustness falsifies the first allocator

A preregistered battery varies prices and instance distribution. The original greedy allocator fails under both shifts. The rule is not retuned after the negative.

This failure separates two claims that could otherwise be conflated:

- a rule can transfer across several fixed exact domains;
- a rule can remain optimal when the charging environment or data distribution changes.

The first is supported on nine cases. The second is not.

## 8. Conditional price-aware successor

A separately frozen successor receives exact per-structure charge certificates and optimizes the registered priced objective. Two implementations agree, and the selector has zero priced regret in all 195 registered battery cells.

The result is conditional on information that may not be prospectively available. Exact charges supplied by the environment solve the registered decision problem; they do not demonstrate that a deployed allocator can know those charges before acting.

The boundary is therefore explicit:
\[
\text{exact charge certificate available}
\Longrightarrow
\text{zero registered priced regret}.
\]
Whether the antecedent holds in a real system remains unresolved.

## 9. Censoring and indistinguishability

A resource cap can censor a result. Reaching the cap may show only that required resource is at least the cap, not that the method cannot succeed.

Similarly, if two worlds are identical under the allocator's observations but require different allocations, no policy restricted to those observations can be correct on both. Positive regret then reflects missing decision information rather than a poor optimizer.

These distinctions prevent budget exhaustion and observation coarsening from being misreported as capability results.

## 10. Donor boundary

Metareasoning, adaptive inference, retrieval, routing, materialized state, and value-of-information planning own the underlying primitives. The residual contribution is a matched resource-location contract, correction of an invalid comparator, and a small exact cross-domain test of one unchanged allocation law.

## 11. Limitations

The main transfer panel has nine cases. The tasks are exact and engineered for independent verification. The allocator does not establish a universal scalar exchange rate across heterogeneous resources. The original rule fails price and distribution shifts. The price-aware rule requires certificates whose availability is open.

A public-data successor has not executed and contributes no evidence. No claim is made about open-ended research agents, language-model scaling, naturalistic workloads, or deployed savings.

## 12. Conclusion

State construction and reasoning are competing locations for test-time computation. After repairing an action-set mismatch, a two-signal study shows controlled complementarity, and one unchanged allocator matches the hindsight locus on nine exact cases across three domains. The first rule then fails price and distribution shifts, while a price-aware successor succeeds only when exact charge certificates are supplied. The bounded law is therefore conditional and useful: resource location can transfer across exact domains, but robustness depends on the information and charging contract available before action.
