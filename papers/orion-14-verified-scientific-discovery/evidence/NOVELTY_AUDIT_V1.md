# ORION-14 Novelty Audit V1

**Date:** 2026-08-16  
**Protocol:** ORION-14.protected-authority.v1  
**Status:** DESIGN_FROZEN

Each system receives a disposition: **ADOPT** (mechanism absorbed as baseline), **ADAPT** (mechanism modified and composed), **COMPOSE** (mechanism reused in a different role), **DEFER** (future integration), or **REJECT** (not applicable).

## 1. ProvenanceGuard (arXiv:2606.18037)

**Disposition: ADOPT**

- Source-aware factuality verification decomposing claims into atomic statements and checking each against a retrieved source context.
- Cross-source conflation is an explicit failure mode.
- **Absorbed as:** Strongest baseline (ProvenanceGuard-style source-aware verifier). The conflation detection dimension is a coordinate we evaluate separately.
- **Residual preserved:** ProvenanceGuard does not implement a non-escalating authority transition or protected evaluator/holdout gates. It returns a verdict score, not a fail-closed authority state.

## 2. Claim-Level Auditability / AAR (arXiv:2602.13855)

**Disposition: ADAPT**

- Persistent semantic provenance records for deep research agents; verification of claims against asserted evidence *after* generation.
- **Absorbed as:** Claim-level auditability baseline (where runnable). The semantic provenance coordinate motivates our behavioral-influence gate.
- **Residual preserved:** AAR records provenance retrospectively; ORION requires evidence identity and behavioral influence at *authority-transition time*, not post-hoc. The fail-closed CANNOT_CHECK default is absent.

## 3. ProvenAI (arXiv:2606.26449)

**Disposition: COMPOSE**

- Separates citation fidelity from behavioral influence — whether cited evidence actually influenced the answer path.
- **Absorbed as:** The `CITED_NON_INFLUENTIAL` attack family and the behavioral-influence coordinate in the authority pipeline.
- **Residual preserved:** ProvenAI measures influence; ORION gates authority on it. The coordinate is a gate input, not a standalone novelty claim.

## 4. Search-Time Contamination (arXiv:2606.05241 and prior)

**Disposition: ADOPT**

- Browsing agents may retrieve public benchmark answers during inference, inflating performance.
- **Absorbed as:** `SEARCH_TIME_CONTAMINATION` attack family, contamination gate in the pipeline, and search-logging access policy.
- **Residual preserved:** STC work identifies the problem; ORION makes it a first-class authority gate. The detection mechanism is a direct baseline.

## 5. RewardHackingAgents (arXiv:2603.11337)

**Disposition: ADAPT**

- Benchmarks evaluator tampering, metric manipulation, and held-out test-set leakage for ML-engineering agents.
- **Absorbed as:** `EVALUATOR_TAMPER` and `HOLDOUT_ACCESS` attack families, evaluator protection gate, access telemetry policy.
- **Residual preserved:** RHA benchmarks the attack surface; ORION makes evaluator integrity a prerequisite for authority promotion. The fail-closed CANNOT_CHECK on evaluator attack is not in RHA.

## 6. AttributionBench (ACL 2024 Findings)

**Disposition: ADOPT**

- Benchmark for evaluating whether generated text is properly attributed to supporting sources.
- **Absorbed as:** AttributionBench-style attribution evaluator baseline; source-attribution accuracy metric.
- **Residual preserved:** AttributionBench evaluates attribution quality; ORION gates authority on source ownership. A correct attribution score does not imply a correct authority transition.

## 7. CLAIM-BENCH / SciClaimHunt (arXiv:2506.08235)

**Disposition: ADOPT**

- Scientific claim-to-evidence reasoning benchmark for support/contradiction classification.
- **Absorbed as:** Pooled-evidence NLI/support verifier baseline; support/contradiction F1 metric.
- **Residual preserved:** CLAIM-BENCH evaluates support classification; ORION requires support + attribution + checker admissibility + evaluator integrity simultaneously.

## 8. FIRE — Iterative Retrieve-or-Verify (related work)

**Disposition: COMPOSE**

- Iterative retrieval and verification pipeline for factual claims.
- **Absorbed as:** Iterative retrieve-or-verify baseline.
- **Residual preserved:** FIRE-style pipelines produce a verified claim; ORION produces a non-escalating authority state. The fail-closed CANNOT_CHECK default, checker lineage gates, and protected evaluator custody are absent from FIRE.

## Residual Claim

The **non-escalating scientific authority transition** requiring:
1. Exact content/provenance binding (not just citation matching)
2. Admissible checker lineage with independence gates (not just non-empty checkers)
3. Protected evaluator/holdout identity with access telemetry (not just post-hoc audit)
4. CANNOT_CHECK/BLOCK as default when any prerequisite is unresolved (not a confidence-weighted promotion)

This fail-closed architecture — rather than a weighted confidence sum — and the protected custody model that enforces it, constitute the candidate delta. No universal evaluator security is asserted; the claim is bounded to the registered attack families under the frozen custody model.

## Future Work

- **Assurance cases / safety cases:** formal decomposition of authority into sub-goals with evidence. DEFER — the formal assurance structure is complementary to the empirical benchmark.
- **Provenance systems / blockchains:** cryptographic evidence provenance. DEFER — not required for V1 protocol scope.
- **Secure evaluation enclaves:** hardware-enforced evaluator custody. DEFER — outside V1 host model.
- **Independent verification / scientific fact-checking end-to-end:** broader than our scoped authority transition. DEFER — the ORION programme's longer-term horizon.