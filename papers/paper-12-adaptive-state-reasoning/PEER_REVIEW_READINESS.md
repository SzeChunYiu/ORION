# P12 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_MATCHED-BUDGET_SUPERIORITY_RESULT`

## Five-lens hostile review

### Theory / systems

**Pass.** The paper distinguishes state-construction resource from downstream reasoning resource and states the scalar controlled world separately from heterogeneous real resource vectors.

### Experimental design

**Pass.** Protected families are held out, both one-axis comparators adapt using the same pre-outcome signals, the total two-unit budget is identical, and oracle is diagnostic only.

### Statistics

**Pass.** Headline uncertainty is family-blocked rather than falsely treating all 8,192 items as independent domains. Mean gain, bootstrap interval and worst-family gain are all reported.

### Novelty

**Pass after subtraction.** Adaptive test-time compute, context selection, retrieval and dynamic generation are treated as donor-owned. Novelty is concentrated on the two-locus matched-budget decision and strict comparison to both one-axis adaptive controls.

### Referee / reporting

**Pass for a controlled paper.** No real-system result is implied. The manuscript gives a direct path for external validation with end-to-end compiler/reasoner accounting.

## Checklist

- [x] protected protocol committed before result
- [x] matched total budget
- [x] strong adaptive state-only baseline
- [x] strong adaptive reasoning-only baseline
- [x] fixed policy and oracle diagnostic
- [x] held-out family generalization
- [x] family-block uncertainty
- [x] worst-family result
- [x] deterministic two-run replay
- [x] claim/evidence ledger
- [x] current donor subtraction
- [x] explicit real-system promotion gate
- [ ] open-weight LLM/procedural replication
- [ ] verifier-backed search replication
- [ ] real vector resource Pareto surface

## Referee-facing headline

> **Inference scaling has a resource-location problem, not only a resource-amount problem.** When the source of difficulty varies between state accessibility and downstream reasoning, a frozen allocator that can spend the same budget on either locus strictly outperforms policies that may adapt only one.
