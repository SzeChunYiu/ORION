# P12 top-tier promotion V1 — Resource-Location Metareasoning

**Programme:** #977  
**Existing controlled authority:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_MATCHED-BUDGET_SUPERIORITY_RESULT` remains valid.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Inference scaling has a resource-location problem, not only a resource-amount problem.** Under one end-to-end resource envelope, an adaptive policy should decide whether the next unit of resource is best spent on state construction/acquisition, downstream reasoning/search, verification/tool use, or recovery. P12 derives and validates the conditions under which these loci substitute for or complement one another.

Adaptive test-time compute, best-of-N/search, context selection, uncertainty allocation and value-of-computation metareasoning are donors.

## Generalized action space

Move beyond the current two-locus scalar controlled world. Freeze a resource-location action set including at least:

- improve/compile/retrieve state;
- reason/search more over current state;
- call verifier/tool / acquire discriminating evidence where allowed;
- cache/reuse prior work;
- recover/reopen raw state after an unsupported responsibility or regime change.

Not every domain must expose every action, but unavailable actions must be declared before protected outcomes.

## Resource vector

Use the programme-wide vector:

`R = (preprocessing/compiler work, state/memory, model compute, inference/search, tool/verifier calls, latency, cache/reuse, recovery/reconstruction)`.

A scalar utility may be reported only when weights are supplied prospectively by a real downstream decision contract. Otherwise compare Pareto fronts and constrained slices.

## Theory/decision programme

### T12.1 — Marginal resource-location rule

Formalize a decision rule based on expected marginal verified value per constrained resource, with uncertainty over accessibility/difficulty. State the assumptions under which one-locus policies are optimal and construct regimes requiring joint allocation.

### T12.2 — Substitution/complementarity map

Define measurable criteria for when better state substitutes for more reasoning, when the two are complementary, and when neither should receive more resource. Avoid inferring this relation from an arbitrary scalarized endpoint.

### T12.3 — Regret to oracle allocator

Define an oracle ceiling only for analysis. Bound or empirically estimate regret of the frozen allocator relative to the oracle under distribution shift and hidden task-family variation.

## Protected experiments

### E12.1 — open-weight/procedural system

Freeze pre-outcome signals and compare:

1. fixed state + fixed compute;
2. fixed state + adaptive reasoning;
3. adaptive state + fixed reasoning;
4. joint adaptive state/reasoning;
5. generalized multi-locus allocator;
6. uncertainty-only/difficulty-only/context-only donors;
7. oracle diagnostic ceiling.

### E12.2 — verifier-backed search

Repeat with verifier-call/search budgets and independently checkable task correctness. State construction may use native proof/dependency information only if every comparator receives matched semantic access.

### E12.3 — cross-domain transfer

Freeze one allocator or a small registered family before target-domain outcomes. Test whether its allocation policy transfers without target-specific endpoint tuning.

## Primary endpoints

- verified quality at constrained resource slices;
- Pareto hypervolume/frontier dominance with uncertainty;
- time-to-first-correct / anytime performance;
- allocation-regret to oracle;
- false compile / false think-more decisions;
- substitution/complementarity prediction accuracy;
- cross-domain policy transfer;
- robustness under resource-price and task-distribution shift.

## Strongest hostile attacks

- joint allocator silently receives more total resources;
- state construction cost is discounted or unmeasured;
- protected difficulty/answer signal leaks into allocation;
- policy is tuned per item after outcomes;
- one arm receives better stopping/verifier semantics;
- scalar weighting is chosen to make joint policy win;
- oracle information leaks into train-time allocator;
- cross-domain transfer vanishes without retuning.

## Top-tier promotion gate

`P12_TOP_TIER_SUBMISSION_READY` requires:

- [ ] T12.1 resource-location decision rule;
- [ ] T12.2 substitution/complementarity criteria;
- [ ] real vector-valued resource accounting;
- [ ] open-weight/procedural replication;
- [ ] verifier-backed search replication;
- [ ] frozen cross-domain transfer test;
- [ ] strict comparisons to adaptive-compute-only and adaptive-state-only donors;
- [ ] no hidden resource advantage;
- [ ] family/domain-block uncertainty and independent replay;
- [ ] donor refresh and exact submission binding.

If no transferable allocator wins, retain the domain-specific crossover laws and characterize the information required for a general allocator rather than weakening the matched-budget requirement.
