# P12 — Adaptive State–Reasoning Co-Design

**Stable ID:** ORION-P12  
**Paper issue:** #665  
**Shared accounting:** #664  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript. Its historical P12A/P12B sections remain part of the evidence story, but the current top-tier claim is defined by the later verifier-backed resource-location and unchanged-allocator receipts.

## Current scientific state

P12 now has three evidence layers that must be read in order.

### 1. Historical comparison correction

P12A remains a valid execution record but not a valid signal-count superiority result: the joint arm could emit allocations unavailable to the one-axis arms. `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` permanently withholds that causal superiority interpretation.

P12B repairs the comparator by giving all signal policies the same four-action set and two-unit budget. Across 32 independent family RNG blocks, the two-signal policy gains `0.253906` over the stronger one-signal policy with stratified family-block 95% interval `[0.251221, 0.256653]`. This remains controlled equal-action evidence, not the final top-tier object.

### 2. Verifier-backed resource-location evidence

The top-tier programme moves the object upward from "two signals help" to **where computation should be spent**. Verifier-backed SAT and procedural path-planning studies establish that adaptive state/reason allocation can outperform fixed-locus restrictions while preserving exact task outputs. These results motivate a domain-invariant allocation rule rather than a benchmark-specific policy.

### 3. Unchanged-allocator cross-domain transfer — authoritative

`top_tier/P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md` binds GitHub Actions run `32661332687` with a primary and structurally independent checker.

One frozen allocator is applied **without any domain-specific parameter** to three exact domains:

- SAT unit propagation;
- 15×15 path planning;
- 0/1 knapsack.

Across all `9` frozen transfer cases:

- allocator regret versus the per-case hindsight location oracle: **0/9**;
- every arm produces the independently verified exact output;
- `REASON_ONLY` incurs positive regret in every domain;
- `STATE_ALWAYS` incurs positive regret in every domain;
- the allocator parameters are byte-identical across domains;
- the independent checker re-derives truth, selections and regret with different algorithms;
- every arm×case cell emits the full shared resource vector `R = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)`.

The result therefore supports a bounded **resource-location** claim rather than merely a signal-complementarity claim.

## Strongest paper-level claim

> Under the registered exact domains and common resource contract, a single frozen allocation rule using only pending multiplicity, declared materialization cost and the shared budget transfers unchanged across SAT propagation, path planning and knapsack, matches the hindsight resource-location oracle in all nine protected cases, and avoids the complementary failures of always-reason and always-materialize restrictions.

This is a cross-domain transfer result for the registered allocator and case family. It is **not** a proof of universal allocation optimality.

## Current top-tier blocker

The remaining scientific blocker is robustness, not another basic benchmark. Open gap-wave PR #1006 freezes an additive stress study over the already-bound allocator; until its receipt is bound, none of those stress results are scientific authority for this paper.

The frozen study tests:

- altered state-build / serve prices;
- nominal-budget versus priced-budget semantics;
- case-level and shared-budget task-distribution mixtures;
- an expanded 9→27 stress set;
- a static + dynamic hidden-domain-parameterization audit with mutant self-validation;
- a second independent implementation.

No threshold or allocator parameter may be changed after that run. Whatever the frozen robustness verdict is—robust, regime-conditional or broken—must be bound and written into the paper.

## Manuscript integration rule

The final manuscript should use P12A/P12B as the **comparison-design history**, then make the verifier-backed location law and unchanged three-domain allocator the primary empirical contribution. It should not lead with the old `0.858154` P12A score or imply that signal count alone caused that historical margin.

Manuscript-facing integration notes are in `top_tier/P12_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`.

## Core artifacts currently on main

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`
- `P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json`
- `P12_ACTIVE_CLAIM_AUTHORITY_V3.json`
- `top_tier/P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md`
- `top_tier/P12_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`

The robustness protocol/runner/checker remain in open PR #1006 until that lane is reconciled and landed.

## Explicit nonclaims

No universal resource-allocation optimality, no cross-domain scalar exchange rate between heterogeneous charged units, no open-weight LLM generality unless separately executed, and no claim that the historical P12A margin isolates signal count. Robustness to price and distribution shift remains pending until the frozen robustness receipt is bound.
