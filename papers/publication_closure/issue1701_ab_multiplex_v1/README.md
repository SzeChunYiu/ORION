# Issue 1701 canonical A/B research multiplex v1

**Reviewed main:** `e19a3b7cd0140d1f413e802a1188a2948726df6f`  
**Date:** 2026-08-29  
**Scientific authority delta:** `NONE`  
**Policy:** additive only; no frozen result, negative history, checksum ledger, or foreign branch is rewritten.

## Why this packet exists

Two uploaded audits were reconciled with current `main` and branch-only work. The recursive-closure audit is identity-aligned with the canonical ORION-01..25 series. The separate “top-tier science closure gate” is **not safe as a paper-local grade source**: it maps several ORION IDs to subjects that do not match `papers/PAPER_ALIASES.md` (for example ORION-06/07/08). Its general reviewer rubric is useful, but its per-paper A/B labels are rejected here.

This packet therefore uses **action grades**, not prestige grades:

- **A** — repository-local theory, exact analysis, or protocol repair can materially reduce a live science gap now.
- **B** — a decisive successor can be frozen now, but the outcome needs new compute/data/native systems and may still require external authority.
- **X** — the decisive authority is institution/expert-disjoint and cannot be self-created.

No grade means “top-tier ready.” No protocol file is an outcome.

## Expert review lenses

1. **Formal/theory:** theorem identity, estimands, counterexamples, symmetry, and impossibility routes.
2. **Design/statistics:** independent inference unit, exact small-N inference, multiplicity, power, and rival explanations.
3. **Reproducibility/governance:** chronology, frozen outcomes, content binding, checker independence, and external custody.
4. **Editorial/referee:** smallest defensible headline, no mechanism language from prediction alone, and explicit kill/stop rules.

A candidate remains live only if all four lenses can state what would falsify it.

## Highest-value changes captured here

### ORION-05 — repair before compute

The open V1 global-obstruction campaign expects 6/5 on three R6O controls, but its runner minimizes over all 15 matchings. Under that actual campaign estimand the controls are 4/4, 5/5, and 6/6. V2 therefore turns those into **domain-sensitivity negatives**, discovers positive controls prospectively in a disjoint repeated-target multiset domain using the *same* all-matchings optimizer, freezes the first three qualifying controls, and only then permits the 5,005 distinct-target confirmation. A second optimizer implementation is required for every row used in a universal claim.

Parallel theories are intentionally kept alive: (C1) finite obstruction basis; (C2) matching relaxation erases fixed-matching gaps; (C3) a symmetry-closed characterization of gaps that survive matching relaxation.

### ORION-17 — prediction survives; mechanism overclaim does not

The five held-out repositories are real prospective evidence, but density, module count, and edge count each perfectly separate the eight observed calibration+evaluation projects. The successor therefore selects **20 outcome-blind disagreement repositories**: 10 small/few-edge but dense and 10 large/many-edge but sparse. Density must win at least 15/20 and at least 7/10 in each stratum. Under a symmetric 0.5 null the joint gate probability is 0.0158081; power is about 0.732 if the independent density-win probability is 0.8. This tests density against the two prespecified absolute-size rivals without pretending it identifies every possible causal graph mechanism.

### ORION-19 and ORION-24 — small-N exactness before rhetoric

Both current paired comparisons have four favourable discordances and zero adverse discordances, so two-sided exact p=0.125. ORION-19 gets a minimum-20 identity-disjoint family replication with family-level paired inference and cost gatekeeping. ORION-24 gets a 20-family external construct replication split equally between negative-retention and ordinary/mixed strata; the same 15/20 + 7/10-per-stratum joint gate prevents the existing planted-control concentration from being laundered into broad superiority.

### Theory lanes

`AB_MULTIPLEX_PLAN_V1.json` keeps multiple falsifiable candidates alive for ORION-01, 04, 05, 09, 10, 14, 17, 19, 21, and 24. The point is not to maximize candidate count; it is to make rival explanations compete on **disagreement cases** or exact theorem premises rather than on more data from the same confounded regime.

## Branch reconciliation

- Current `main` already includes the ORION-11 arm-discrimination disclosure, ORION-13 null/baseline battery, ORION-16/17 alias-binding repairs, and PR #1754's ORION-11 R4 digest reconciliation. Do not duplicate them.
- `wk/top-tier-gap-audit-20260829` contains a strong V2 gap register, but is 3 commits ahead / 7 behind the reviewed main; its verified diagnoses are incorporated semantically here rather than bulk-cherry-picked.
- `science/o05-obstruction-basis-v1` is 5 ahead / 66 behind and is an implementation seed only because the control estimand is wrong.
- `wk/orion17-density-lane` is 1 ahead / 35 behind. Preserve the prospective 5/5 result, but reject its stronger “density, not size” terminal pending the rule-disagreement successor.
- `science/orion24-paired-evidence-interpretation-20260829` is 2 ahead / 3 behind and contains useful exact paired analysis; its numerical interpretation is carried here, without treating the open branch as mainline authority.
- Older ORION-23/25 theorem/protocol branches are far behind main and remain candidate/handoff material, not bulk-adoption targets.

## Files

- `AB_MULTIPLEX_PLAN_V1.json` — canonical 25-paper action register plus candidate registry.
- `ORION05_SAME_DOMAIN_PROTOCOL_V2.json`
- `ORION17_RULE_DISAGREEMENT_PROTOCOL_V1.json`
- `ORION19_FAMILY_REPLICATION_PROTOCOL_V1.json`
- `ORION24_STRATIFIED_REPLICATION_PROTOCOL_V1.json`
- `THEORY_CANDIDATES_V1.md` — human-readable competing hypotheses and stop logic.
- `RUN_QUEUE.md` — computation/external-handoff queue for another AI session.
- `check_ab_multiplex_v1.py` — stdlib validator and exact probability regression gate.

## Non-negotiable terminal

`PASS` from the checker means **the research plan is internally coherent**. It never means a paper is supported, externally replicated, top-tier ready, or submission ready.
