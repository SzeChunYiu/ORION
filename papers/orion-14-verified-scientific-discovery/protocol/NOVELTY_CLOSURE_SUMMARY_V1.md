# Novelty Closure Summary — ORION-14 (V1)

**Protocol:** ORION-14.protected-authority.v1  
**Date:** 2026-08-16

## Residual claim

> **Non-escalating scientific authority transition** — promotion to scientific authority is a *protected state transition* (not a confidence threshold) requiring registered prerequisites. When any prerequisite is unresolved or compromised, the default terminal is `CANNOT_CHECK`/`BLOCK`.

## Three strongest prior works absorbed

| Prior work | What is absorbed | How |
|---|---|---|
| **ProvenanceGuard** | Cross-source conflation detection, atomic-claim granularity | Evidence-binding layer separates source ownership from semantic support as distinct coordinates |
| **RewardHackingAgents** | Evaluator locking, patch/access logging, held-out leakage detection | Protected-evaluation substrate: frozen evaluator hash, access telemetry, tamper detection |
| **ProvenAI** | Behavioral-influence coordinate | Citation is not authority until behavioral influence is verified; chronology attacks on citations are a protected-evaluation concern |

## The delta

**Existing systems** return confidence scores, support verdicts, or attribution labels. Even when they "block" or "abstain," the decision is a threshold on a continuous score (e.g., NLI probability < 0.5 → block).

**ORION-14** defines authority as a **lattice of registered prerequisites**: content binding, source ownership, semantic support, checker lineage + hostile discrimination, behavioral influence, evaluator integrity, contamination status. Every prerequisite is a discrete gate. When unresolved, the terminal is `CANNOT_CHECK` or `BLOCK` — not a confidence value that can be averaged into a promotion.

**Analogy:** This is the difference between score-based authentication ("password similarity > 0.7 → access granted") and multi-factor authentication (password AND token AND biometric → access). The individual factors are not new; the *fail-closed composition* into a protected authority lattice is the residual claim.

## Audit reference

See `NOVELTY_AUDIT_V1.md` for full dispositions (ADOPT/ADAPT/COMPOSE/DEFER/REJECT) across 10+ prior works.

## Re-search obligations

- [ ] Re-run literature sweep for 2026 assurance-case + provenance + secure-evaluation systems before submission.
- [ ] If an interim publication publishes an authority lattice, ADAPT + disclose, update this summary.