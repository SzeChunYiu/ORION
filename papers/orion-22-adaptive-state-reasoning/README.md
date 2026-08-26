# ORION-22 — Adaptive State–Reasoning Co-Design

**Stable ID:** ORION-ORION-22  
**Paper issue:** #665  
**Shared accounting:** #664  
**Programme:** #670

## Canonical manuscript

`manuscript/sections/*.md` are the canonical publication source and `manuscript/main.pdf` is the rendered paper. `MANUSCRIPT.md` is a historical integrated review snapshot. Current claim authority is `P12_ACTIVE_CLAIM_AUTHORITY_V5.json`, which extends the lifecycle `P12_ACTIVE_CLAIM_AUTHORITY_V4.json` without altering any of its leaves.

## Current scientific state

ORION-22 now has three evidence layers that must be read in order.

### 1. Historical comparison correction

P12A remains a valid execution record but not a valid signal-count superiority result: the joint arm could emit allocations unavailable to the one-axis arms. `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` permanently sets `P12A_SUPERIORITY_AUTHORITY_WITHHELD`. V4 preserves P12B's bounded `P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED` terminal.

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

## Landed robustness boundary and successor

The preregistered stress study is complete. The original q-greedy allocator's FLAT result replicates, but its price and distribution-shift axes are both **BROKEN**. That negative remains binding and was not retuned.

A separately preregistered successor reads the charging environment's exact per-structure certificates and prices and solves the registered budgeted objective exactly. It reaches zero priced regret in all 195 frozen battery cells with two implementations agreeing. This is a conditional selection result, not a forward-time deployment result: whether exact certificates are available before action is `CANNOT_CHECK`.

Selection-sufficiency and certificate-necessity falsifiers support the exact-certificate boundary in the registered finite environment. They do not establish external transfer.

## Stop/go public-data campaign — frozen protocol (not executed)

Issue #1086 (ORION-22 boxes) freezes the protocol for a public-data stop/go campaign
**before any data collection**. The campaign itself has **not** been executed:
no runner, datum, score, gate verdict or terminal exists for it, and nothing in
these artifacts may be cited as evidence of any empirical outcome.

- Frozen menus: `top_tier/p12_stopgo_frozen_menus_v1.json` (machine-readable)
  and `top_tier/P12_STOPGO_FROZEN_MENUS_V1.md` (protocol doc). Identical
  four-action menu `((0,0),(2,0),(0,2),(1,1))` and identical closed four-signal
  menu across the adaptive arm and both one-signal arms; task-family/domain
  inference unit; clean-license ScienceAgentBench substrate with the six
  upstream-license instances excluded; preregistered pass gate and a binding
  fail action (stop and publish the boundary/null result; do not iterate until
  positive).
- Binding prior adverse evidence (SHA-bound in the menus JSON and in
  `P12_ACTIVE_CLAIM_AUTHORITY_V5.json`): `P12A_SUPERIORITY_AUTHORITY_WITHHELD`
  (actions must be held symmetric), `P12_ROBUSTNESS_STRESS_V1_EXECUTED` with
  `price_axis=BROKEN` and `distribution_shift_axis=BROKEN` (no robustness
  wording available to this campaign), and `P12_PRICE_AWARE_SUCCESSOR_SUPPORTED`
  (preregistered readable-surface widening is the only sanctioned revival
  pattern).
- Label honesty: issue #1086 asks to integrate "P12C's negative public-data
  result". **No repository artifact labelled P12C exists** (working tree, all
  refs, PRs and issues searched); none was invented. The integrated priors are
  the landed adverse chain above.
- Fail-closed audit: `check_p12_stopgo_integration_v1.py` (paper root)
  validates menu identity across arms, the inference unit, scope minimums, the
  prior bindings and authority V5-over-V4 preservation; it reports
  `scientific_authority_delta: NONE` and `external_validation: CANNOT_CHECK`.

## Manuscript integration rule

The final manuscript should use P12A/P12B as the **comparison-design history**, then make the verifier-backed location law and unchanged three-domain allocator the primary empirical contribution. It should not lead with the old `0.858154` P12A score or imply that signal count alone caused that historical margin.

Manuscript-facing integration notes are in `top_tier/P12_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`.

## Core artifacts currently on main

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`
- `P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json`
- `P12_ACTIVE_CLAIM_AUTHORITY_V4.json`
- `top_tier/P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md`
- `top_tier/P12_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`

The transfer, robustness, price-aware successor and theorem receipts are content-bound by V4.

Issue #1086 stop/go protocol artifacts (added by the ORION-21/ORION-22 lane):

- `P12_ACTIVE_CLAIM_AUTHORITY_V5.json` (V4 preserved; adds the frozen-campaign leaf)
- `check_p12_stopgo_integration_v1.py` (fail-closed audit)
- `top_tier/p12_stopgo_frozen_menus_v1.json`
- `top_tier/P12_STOPGO_FROZEN_MENUS_V1.md`

## Explicit nonclaims

No universal resource-allocation optimality, no cross-domain scalar exchange rate between heterogeneous charged units, no open-weight LLM generality, and no claim that the historical P12A margin isolates signal count. The V1 allocator is not price- or shift-robust. The successor is not a forward-time allocator because it consumes exact published charge certificates. No `P12C` artifact or bound public ScienceAgentBench result exists.
