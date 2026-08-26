# Paper Q4 claim ledger V2 — typed epistemic state for scientific decisions

**Date:** 2026-08-22
**Manuscript:** `MANUSCRIPT_V2.md`

V1's receipt-backed numerical claims remain valid within their exact-synthetic scopes. V2 changes **interpretation and novelty boundaries** in light of 2026 related work.

| ID | Maximum permitted claim | Evidence / boundary | Status |
|---|---|---|---|
| Q4V2-1 | N4-A: with the same frozen world information, type-conditioned VoI obtains mean utility 3.291 versus 2.180 for the otherwise matched uniform-prior VoI arm; 71% of oracle utility. | `N4_A_UNKNOWN_VOI_RESULTS.json` | EXACT-SYNTHETIC MECHANISM EVIDENCE |
| Q4V2-2 | N4-B: scope-bound failure reopening outperforms never/always/unscoped reopening in the frozen two-regime world and avoids irrelevant-NOISE reopening traps. | `N4_B_STALE_RECEIPT_REOPENING_RESULTS.json` | EXACT-SYNTHETIC MECHANISM EVIDENCE |
| Q4V2-3 | N4-C: Pareto-ambiguity-targeted verification has mean scalarized regret 0.1096 vs random 0.2518 at matched budget, approximately 2.3x lower. | `N4_C_INTERVAL_PARETO_RESULTS.json` | EXACT-SYNTHETIC MECHANISM EVIDENCE |
| Q4V2-4 | N4-D: full-chain transport detects all 200 frozen laundering chains incl. all 68 deep splices with 0/200 false positives on the honest set; last-hop detection is much weaker in this constructed world. | `N4_D_LAUNDERING_DETECTION_RESULTS.json` | EXACT-SYNTHETIC ONLY; NOT SECURITY CLAIM |
| Q4V2-5 | N4-E: decision-coupled acquisition spends zero probes on frozen high-entropy decoys versus 36.6% for pure information gain and achieves higher mean utility in the registered world. | `N4_E_ACTIVE_EXPERIMENTS_RESULTS.json` | EXACT-SYNTHETIC MECHANISM EVIDENCE |
| Q4V2-6 | N4-F3: typed remint/transport beats matched-budget re-derivation in the mixed regime, commits zero failures, and ties all correct arms exactly in the remint-unnecessary regime. | `N4_F3_REMINT_TRANSPORT_RESULTS.json` | EXACT-SYNTHETIC MECHANISM EVIDENCE |
| Q4V2-7 | N1-C bounds policy novelty: typed scoped failure **state** improves over unscoped state, but the ideal VoI donor matches the allocation policy exactly. | `N1_C_COSTLY_VERIFICATION_RESULTS.json` | DONOR-BOUNDED POSITIVE |
| Q4V2-8 | N2-F5B bounds crossover novelty: the stronger model-selection donor absorbs the original well-specified-world residual; candidate advantage remains only on the frozen misspecified world. | `N2_F5B_DONOR_COMPARISON_RESULTS.json` | MIXED / DONOR-ABSORBED ORIGINAL CLAIM |
| Q4V2-9 | Current literature already contains typed/provenance-aware memory (e.g. MemIR), stale-memory benchmarks (STALE), and agentic VoI (ACL 2026). Q4 therefore makes no broad novelty claim for those primitives. | `NOVELTY_RESEARCH_2026-08-22.md` | RELATED-WORK BOUNDARY |
| Q4V2-10 | The residual synthesis is a hypothesis about **matched-information scientific decision state**: explicit applicability/provenance/uncertainty/transport/decision-role bindings can be load-bearing even when visible facts are held fixed. | synthesis of C1-C8 | MECHANISTIC INTERPRETATION, SYNTHETIC SCOPE |
| Q4V2-11 | A prospective real-domain validation protocol is frozen for >=100 research-decision items across >=3 programmes, aiming for >=30 genuinely unresolved items if feasible. No result exists under it yet. | `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` | REGISTERED RESEARCH ONLY |

## Forbidden promotions

- Do not claim first typed agent memory, provenance-aware memory, stale-memory revision, or value-of-information agent planning.
- Do not describe deterministic `LLM_PROXY` arms as measurements of actual LLMs.
- Do not extrapolate N4-D into cryptographic/security guarantees.
- Do not claim real scientific-agent effectiveness until the prospective real-domain protocol is executed.
- Do not pool the six families into one universal numerical effect size; they operationalize different decisions.

## Allowed current headline

> In six exact-synthetic matched-information studies, explicit epistemic bindings—type-conditioned priors, applicability scope, decision-relevant uncertainty, full-chain transport obligations, decision-coupled acquisition, and remint status—change research decisions relative to untyped/decision-agnostic controls, while strong donor and no-value regimes bound the claim. The result is a mechanism-isolation suite, not yet evidence of transfer to real scientific agents.
