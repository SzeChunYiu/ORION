# P12 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_MATCHED-BUDGET_SUPERIORITY_RESULT`

## Five-lens hostile review

### Theory / systems

**Pass.** The paper distinguishes state-construction resource from downstream reasoning resource and states the scalar controlled world separately from heterogeneous real resource vectors.

### Experimental design

**Pass.** Protected families are held out, both one-axis comparators adapt using the same pre-outcome signals, the total two-unit budget is identical, and oracle is diagnostic only.

### Statistics

**Pass.** Headline uncertainty is family-blocked rather than falsely treating all 8,192 items as independent domains. Mean gain, bootstrap interval and worst-family gain are all reported.

### Reproducibility / protocol authority

**Pass after explicit correction.** Hostile PR review found that the V1 runner did not include the protocol's byte-replay requirement in its terminal decision even though the receipt reported a two-run replay. The V1 terminal is now explicitly non-authoritative alone. `verify_p12a_protocol_adjudication_v2.py` re-executes the exact frozen runner twice in fresh subprocess directories and makes the authoritative terminal contingent on all original scientific gates plus byte identity. Both canonical payloads have SHA-256 `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`.

### Novelty

**Pass after subtraction.** Adaptive test-time compute, current “when to think” allocation, context selection, retrieval and dynamic generation are treated as donor-owned. Novelty is concentrated on the two-locus matched-budget decision and strict comparison to both one-axis adaptive controls.

### Referee / reporting

**Pass for a controlled paper.** No real-system result is implied. The manuscript gives a direct path for external validation with end-to-end compiler/reasoner accounting, and the replay correction is visible rather than silently folded into the original receipt.

## Checklist

- [x] protected protocol committed before result
- [x] matched total budget
- [x] strong adaptive state-only baseline
- [x] strong adaptive reasoning-only baseline
- [x] fixed policy and oracle diagnostic
- [x] held-out family generalization
- [x] family-block uncertainty
- [x] worst-family result
- [x] V1 replay-gate omission disclosed
- [x] exact frozen runner independently executed twice
- [x] authoritative replay-gated V2 adjudication
- [x] claim/evidence ledger
- [x] current donor subtraction
- [x] explicit real-system promotion gate
- [ ] open-weight LLM/procedural replication
- [ ] verifier-backed search replication
- [ ] real vector resource Pareto surface

## Referee-facing headline

> **Inference scaling has a resource-location problem, not only a resource-amount problem.** When the source of difficulty varies between state accessibility and downstream reasoning, a frozen allocator that can spend the same budget on either locus strictly outperforms policies that may adapt only one; the exact result survives a replay adjudicator that enforces the originally registered reproducibility gate.
