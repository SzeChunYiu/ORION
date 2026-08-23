# P12 top-tier promotion V1 — Resource-Location Metareasoning

**Programme:** #977  
**Existing controlled authority:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_MATCHED-BUDGET_SUPERIORITY_RESULT` remains valid.  
**Top-tier state:** `TWO_EXECUTABLE_DOMAINS_EARNED__FINAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Inference scaling has a resource-location problem, not only a resource-amount problem.** Under one end-to-end resource envelope, an adaptive policy should decide whether the next unit of resource is best spent on state construction/acquisition, downstream reasoning/search, verification/tool use, or recovery. P12 derives and validates the conditions under which these loci substitute for or complement one another.

Adaptive test-time compute, best-of-N/search, context selection, uncertainty allocation and value-of-computation metareasoning are donors.

## Post-outcome status — 2026-08-23

The independent bounded theory checker closes the current marginal resource-location construction, a weight-free substitution/complementarity criterion, and a `2ε` oracle-regret bound under the frozen finite assumptions.

### Verifier-backed SAT domain

The prospectively frozen SAT study returns `P12_VERIFIER_RESOURCE_LOCATION_V1_SUPPORTED` with byte-identical replay. Every arm receives the same 2,000-literal-evaluation work budget and every returned SAT/UNSAT disposition is independently verified.

Protected outcomes over 16 cases:

- `ADAPTIVE_LOCATION`: `16/16` solved, mean solved work `50.25`, maximum work `272`;
- `PROPAGATE_FIRST`: `16/16` solved, mean solved work `52.375`, maximum work `272`;
- `REASON_ONLY`: `4/16` solved with `12` budget exhaustions;
- adaptive regret relative to the per-case oracle: maximum `0`, mean `0.0`.

The low-unit easy family is an anti-preprocessing control: adaptive mean work is `11.75`, exactly matching reason-only and improving on always-propagate `20.25`. Unit-heavy and contradiction families require state construction to avoid budget exhaustion.

### Procedural repeated-path domain

A second prospectively frozen executable domain now returns `P12_PROCEDURAL_PATH_ALLOCATION_V1_SUPPORTED` with deterministic byte replay. It contains eight repeated shortest-path task families with exact shortest-path verification and a pre-outcome query-count allocation signal.

All three arms return the same `46` verified paths, but their charged expansion work differs:

- `ADAPTIVE_LOCATION`: `858` total expansions, `0` budget exhaustions;
- `REASON_ONLY`: `7,024` total expansions, `4` budget exhaustions;
- `STATE_FIRST`: `1,688` total expansions, `0` budget exhaustions.

The frozen allocator agrees with the post-outcome oracle in all `8/8` cases with zero observed regret. It selects `REASON_ONLY` in every low-query case, where direct search costs only `2–5` expansions while reusable state costs roughly `197–225`, and selects `STATE_FIRST` in every high-query case, where repeated search costs `1,190–2,273` expansions while reusable state costs roughly `197–225`.

**Earned claim:** resource *location* is causally consequential in two qualitatively distinct executable settings, and non-beneficial regimes are part of the result rather than removed. A pre-outcome structural signal can select the lower-work locus while preserving exact task correctness. **Not earned:** a universal multi-locus allocator, open-weight LLM transfer, or complete vector-valued resource law across every programme coordinate.

Exact procedural authority is bound in `top_tier/P12_PROCEDURAL_PATH_ALLOCATION_RESULT_RECEIPT_V1.md`; SAT authority remains bound in the programme execution ledger.

## Generalized action space

Move beyond the current two-locus demonstrations. Freeze a resource-location action set including at least:

- improve/compile/retrieve state;
- reason/search more over current state;
- call verifier/tool / acquire discriminating evidence where allowed;
- cache/reuse prior work;
- recover/reopen raw state after an unsupported responsibility or regime change.

Not every domain must expose every action, but unavailable actions must be declared before protected outcomes.

Donor declarations for the action set and allocator framing (per `papers/SYNC_CONTRACT.md`): the recover/reopen-after-unsupported-responsibility action executes P13's reopen/recovery semantics and the regime-change action executes P7's regime-transport semantics — both are consumed as frozen upstream donor interfaces, not re-owned here; P9's ex-post causal diagnostic is cited as the offline upper-information comparator (what an allocator could do with causal gold it must not have), and P11's optionality law is cited as the offline design-time analysis layer that the runtime rule partially observes (P12's query-count signal is P11's horizon parameter observed online). P12's owned object is pre-outcome online marginal allocation under one envelope with oracle-regret semantics — neither the diagnostic nor the placement law.

## Resource vector

Use the programme-wide vector:

`R = (preprocessing/compiler work, state/memory, model compute, inference/search, tool/verifier calls, latency, cache/reuse, recovery/reconstruction)`.

The SAT and procedural studies now charge more than one resource coordinate explicitly (state-construction/search work and verifier/path-check work), but they do not yet instantiate the entire programme-wide vector. A scalar utility may be reported only when weights are supplied prospectively by a real downstream decision contract. Otherwise compare Pareto fronts and constrained slices.

## Theory/decision programme

### T12.1 — Marginal resource-location rule

Formalize a decision rule based on expected marginal verified value per constrained resource, with uncertainty over accessibility/difficulty. State the assumptions under which one-locus policies are optimal and construct regimes requiring joint allocation.

### T12.2 — Substitution/complementarity map

Define measurable criteria for when better state substitutes for more reasoning, when the two are complementary, and when neither should receive more resource. Avoid inferring this relation from an arbitrary scalarized endpoint.

### T12.3 — Regret to oracle allocator

Define an oracle ceiling only for analysis. Bound or empirically estimate regret of the frozen allocator relative to the oracle under distribution shift and hidden task-family variation. Both current executable studies have zero observed regret under their respective frozen signals, but that is not a universal bound.

## Protected experiments

### E12.1 — open-weight/procedural system

The procedural half of this requirement is now executed through the repeated shortest-path domain. A true open-weight model/agent replication remains strengthening for any headline that explicitly mentions LLM inference scaling.

### E12.2 — verifier-backed search

The SAT replication is executed with matched literal-evaluation budgets and independently checkable task correctness.

### E12.3 — cross-domain transfer

The current two studies establish the same resource-location phenomenon across domains, but they do not use one frozen allocator unchanged across SAT and path planning. A true policy-transfer claim therefore remains open.

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

- [x] T12.1 bounded resource-location decision rule;
- [x] T12.2 bounded substitution/complementarity criteria;
- [ ] full programme-vector accounting across preprocessing/state/model/inference/tool/latency/cache/recovery coordinates;
- [x] procedural replication with exact path verification and matched charged work;
- [x] verifier-backed SAT replication with matched literal-evaluation budget and independent correctness verification;
- [ ] one frozen allocator/policy transferred unchanged across domains if the final headline claims policy transfer;
- [x] strict comparison to both reason-only and state-first one-locus controls in the procedural domain;
- [x] no hidden total-work advantage in the protected SAT or path studies;
- [ ] family/domain-block uncertainty plus independent implementation/authority beyond same-workflow deterministic replay for the procedural study;
- [ ] donor refresh and exact submission binding.

If the final manuscript headline is the demonstrated **resource-location phenomenon and phase change**, the current SAT + procedural pair is substantially closer to peer-review readiness than a universal transfer claim. If the manuscript claims one transferable allocator across domains, the frozen cross-domain policy-transfer gate remains mandatory.

If no transferable allocator wins, retain the domain-specific crossover laws and characterize the information required for a general allocator rather than weakening the matched-budget requirement.
