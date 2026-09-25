# Where Should Test-Time Computation Be Spent? A Cross-Domain Resource-Location Law

## Abstract

Adaptive test-time computation is usually framed as deciding how much reasoning to perform. State construction creates a second place to spend the same resource: computation can be used to expose task-relevant structure before reasoning or to search over a less processed state afterward. We study this **resource-location** problem under matched budgets and explicit comparator repair.

An initial controlled benchmark appeared to show a large advantage for joint state–reasoning allocation, but a hostile audit found that the winning arm could emit four allocations while the one-axis comparators could emit only two. That superiority interpretation is permanently withheld. A prospectively frozen equal-action successor gives every arm the same four allocations and two-unit budget. Across 32 independent family blocks, the two-signal policy improves exact allocation accuracy by 0.253906 over the stronger one-signal policy, with a stratified family-block 95% interval of 0.251221 to 0.256653.

The main result moves beyond that signal-complementarity study. One frozen allocator using only pending multiplicity, declared materialization cost and the shared budget is applied unchanged to nine protected cases spanning SAT unit propagation, 15×15 path planning and 0/1 knapsack. All arms produce independently verified exact task outputs. The frozen allocator matches the per-case hindsight resource-location oracle in 9/9 cases, while `REASON_ONLY` and `STATE_ALWAYS` each incur positive regret in every domain. An independent implementation re-derives case truth, choices and regret, and allocator parameters are byte-identical across domains.

The boundary is equally important. A preregistered robustness battery shows that the original greedy allocator is not robust to price or distribution shift. A separately frozen price-aware successor attains zero priced regret in all 195 registered battery cells when exact per-structure charge certificates are available, but whether those certificates are available before action remains `CANNOT_CHECK`. The contribution is therefore a bounded cross-domain resource-location law and comparator discipline, not universal allocation optimality or deployed adaptation.

## 1. Introduction

Test-time scaling asks how much computation a system should devote to a difficult instance. More tokens, samples, search nodes or verifier calls can improve performance, but the value of additional reasoning depends on what structure is already exposed in the state. Some tasks are hard because relevant information is poorly organized; others remain hard after the right representation is available.

This creates two competing loci for computation:

\[
\text{current state}\rightarrow\text{state construction}\rightarrow\text{reasoning/search}\rightarrow\text{verified outcome}.
\]

A system with one budget must decide not only **how much** computation to spend but **where** to spend it.

Adaptive inference, routing, value-of-information methods, retrieval and dynamic context construction already own the underlying primitives. The residual question is stricter: under a matched resource boundary, can one rule choose the valuable locus of computation across different exact problem classes, and can the comparison survive strong one-axis controls?

We answer that question through a sequence of increasingly demanding tests. The sequence matters because the first apparent positive result fails its causal comparison; the repaired equal-action study isolates signal value; and the final cross-domain experiment tests a single unchanged allocation rule on three exact domains.

## 2. Matched resource-location problem

For an item \(i\), let \(c_i\) denote resource spent constructing or materializing state and \(r_i\) resource spent on downstream reasoning. In the cleanest controlled setting, the common budget is

\[
c_i+r_i\le B.
\]

A real system may require a vector budget covering tokens, memory, search, tool calls, compiler operations, latency and other resources. A scalar comparison is valid only when the scalarization is fixed before protected outcomes; otherwise the appropriate object is a Pareto frontier.

The comparison classes include fixed allocation, state-only adaptation, reasoning-only adaptation and joint allocation. A valid joint result requires superiority over the strongest one-axis policy under the same action set, information and budget. Merely beating a baseline that cannot emit the winning action does not isolate adaptive resource location.

## 3. Historical comparison correction

The first protected benchmark contained 16 held-out generated families under a two-unit budget. Its joint arm achieved mean success 0.858154, apparently far above the state-only and reasoning-only arms.

The comparison was not capability-matched. The joint policy could choose among four allocations—\((0,0),(2,0),(0,2),(1,1)\)—while each one-axis policy could emit only two. Their perfect-signal ceilings were below the observed joint score. The large historical margin therefore mixed information value with action-set advantage.

The execution record is retained, but superiority authority is withheld. This correction is not a minor methodological note; it determines which subsequent result can carry the paper's claim.

## 4. Equal-action signal complementarity

A prospectively frozen successor gives all adaptive arms the same four-action set and the same two-unit budget. The only intended difference is which pre-outcome signals are visible. The endpoint is exact allocation accuracy rather than downstream score, and the independent unit is the family RNG block.

Across 32 independent family blocks, the two-signal policy improves over the stronger one-signal arm by

\[
0.253906,
\]

with a stratified family-block 95% bootstrap interval of

\[
[0.251221,0.256653].
\]

The minimum family gain is 0.196289, and every fixed noise stratum shows a positive mean gain. Locked-environment revalidation reproduces the result.

This establishes a controlled complementarity fact: when action capability and total budget are held fixed, information about both resource loci improves allocation in the registered generated families. It does not establish cross-domain transfer or general adaptation.

## 5. From signal value to a resource-location rule

The stronger scientific target is not “two signals help” but **whether a common decision rule can locate where marginal computation should be paid across qualitatively different exact tasks**.

The frozen transfer rule reads only three quantities shared across domains:

1. pending multiplicity—the amount of unresolved structure that can be reduced by state materialization;
2. the declared cost of that materialization;
3. the common resource budget.

No domain-specific parameter, tuned threshold or case identity is supplied. The same rule is applied byte-for-byte across SAT propagation, grid path planning and 0/1 knapsack.

The task output itself is verified independently, so allocation quality is not allowed to trade away correctness.

## 6. Nine-case cross-domain transfer

The transfer study contains nine protected cases across three exact domains:

- SAT unit propagation;
- 15×15 path planning;
- 0/1 knapsack.

Every compared arm produces the independently verified exact task output on every case. Regret is therefore specifically **resource-location regret**, not a conflation of allocation and task correctness.

The unchanged allocator matches the per-case hindsight location oracle in all nine cases:

\[
\text{regret}=0/9.
\]

Both fixed-locus restrictions fail in every domain. `REASON_ONLY` incurs positive regret in all three domains, and `STATE_ALWAYS` also incurs positive regret in all three. The failures are complementary: some instances benefit from paying to expose structure, while others are better served by spending the resource downstream.

The allocator parameters are byte-identical across domains. A structurally independent checker re-derives case truth, choices and regret using different algorithms. Each arm×case cell emits the same declared resource-vector schema, preventing a hidden accounting advantage.

This is the paper's strongest empirical claim. It is a bounded cross-domain transfer result for one frozen rule and nine exact cases, not a proof of universal optimality.

## 7. Why the nine-case law is scientifically meaningful

A small exact study can be stronger than a larger opaque benchmark when the scientific object is sharply defined. Here, three properties make the transfer result informative.

First, task correctness is independently verified, so a low-cost allocation cannot “win” by producing a wrong answer. Second, the allocation rule is unchanged across domains and reads domain-agnostic resource coordinates. Third, the two fixed-locus donors fail in opposite directions, establishing that the problem is genuinely about where to spend resource rather than always favoring one side.

The result should nevertheless remain bounded. Nine cases do not characterize an open population, and the hindsight location oracle is an evaluation object, not a deployable policy.

## 8. Robustness falsifies the first allocator

A preregistered robustness battery tests the original greedy allocator under price and distribution shift. Both axes break. The negative is retained and the allocator is not retuned into a positive result.

This matters because a rule that transfers across three fixed exact domains can still be brittle to how resources are priced or how instance frequencies change. Cross-domain structural invariance and distributional robustness are different claims.

The paper therefore makes no claim that the first allocator is price-robust, shift-robust or suitable for deployment under unknown charging environments.

## 9. Price-aware successor and its information boundary

A separately preregistered successor widens the readable surface: it receives exact per-structure charge certificates from the environment and solves the registered budgeted objective using those certificates. Two independent implementations agree, and the successor attains zero priced regret across all 195 frozen battery cells.

The result is conditional. The selector is exact **given** the exact charge certificates. Whether those certificates are available before action in a real system is unresolved. The successor is therefore not evidence of forward-time adaptation under unknown prices.

This creates a clean information boundary. The original allocator is insufficient under price shift. The successor is sufficient when exact price certificates are supplied. A deployment claim would require evidence that the required certificates can be obtained prospectively at acceptable cost.

## 10. Censoring and non-identifiability

Resource ceilings create another evaluation hazard. If an arm hits an exact cap, the observation is censored: the experiment may establish only that the required resource is at least the cap, not that the method is incapable of succeeding with more resource.

Likewise, if two worlds are observation-equivalent to the allocator but require different actions, no policy restricted to those observations can be correct in both. The resulting positive worst-case regret is an information limitation, not an optimization failure.

These formal boundaries prevent absent substrate execution, budget exhaustion or coarsened signals from being silently converted into capability claims.

## 11. Relation to prior work

Metareasoning, adaptive inference, budgeted planning, routing and value-of-information methods already optimize test-time resource. Retrieval and state construction already alter what a reasoner sees. The paper does not claim either axis as new.

The residual contribution is their **matched co-design under one resource contract**, the explicit repair of an invalid comparator, and the unchanged cross-domain resource-location test. The nine-case result is especially useful because it moves from a benchmark-specific signal rule to a domain-invariant allocation law while preserving exact task verification.

## 12. External/public-data boundary

A public-data stop/go campaign has been prospectively frozen with symmetric action menus and explicit adverse priors from the robustness study. It has not been executed. No public-data runner, result, score or terminal exists, and no “P12C negative result” is present in the repository.

The unexecuted protocol contributes no empirical evidence. It records the next valid way to test naturalistic transfer without revising the current bounded claim after outcomes.

## 13. Limitations

The main transfer evidence contains nine exact cases. The domains are heterogeneous but finite and engineered for verifiable outputs. The allocator does not establish a common scalar exchange rate across arbitrary heterogeneous resources. The original greedy rule fails price and distribution-shift robustness. The price-aware successor depends on exact certificates whose prospective availability is unresolved.

No claim is made about open-weight LLMs, naturalistic research agents, universal metareasoning optimality or deployed resource savings.

## 14. Conclusion

State construction and reasoning are competing places to spend test-time computation. A valid comparison must hold both action capability and total resource fixed. After correcting an invalid historical contrast, an equal-action study isolates signal complementarity, and a stronger transfer study applies one unchanged allocator to SAT propagation, path planning and knapsack. The rule matches the hindsight resource-location oracle in all nine protected cases while fixed-locus restrictions fail in every domain. A robustness battery then breaks the first allocator under price and distribution shift, and a price-aware successor succeeds only when exact charge certificates are supplied. The resulting law is deliberately bounded: resource location can transfer across exact domains, but robustness depends on what the allocator is allowed to know.
