# ORION Learning Machine — local research framework V1

This package is the executable local core for candidate P9 and the evaluation-binding substrate for candidate P10. It is intentionally outside the canonical ORION `src/orion` package until P6–P8 stabilize their mechanic/navigation/authority interfaces.

## Current closure authority

**LOCAL_CORE_COMPLETE** means the local implementation, hostile tests, deterministic synthetic experiments, small real-source studies, manuscripts, ledgers and reproducibility packet are complete in this environment. It does **not** mean publication readiness, Lean-kernel verification, broad external superiority, or frontier-mathematics capability.

## Components

- `MechanicLibrary` — provenance-preserving, fail-closed mechanic canonicalization. Same-ID donor entries cannot silently erase family, semantic compatibility, cost or prerequisite differences; protected donor traits are unioned.
- `CompetenceMap` — three-valued empirical competence model. `UNKNOWN` is not trained as failure; it is inferred from insufficient admitted evidence or distance from admitted evidence.
- `TransitionContractInducer` — empirical mechanic → effect summaries from real state-transition observations. A modal effect is evidence, not a universal semantic theorem.
- `mine_macros` — contiguous abstraction mining with trajectory, source and donor lineage. Cross-source/cross-donor admission can be required. Phase 2A showed that recurrence alone is insufficient evidence of structural meaning.
- `ExplicitPlanner` — inspectable beam planner over named mechanics with exact depth bounds and optional stable-state cycle pruning.
- `ExperienceLedger` — append-only SHA-256 hash chain retaining success, failure and `UNKNOWN` episodes.
- `residual_clusters` — invention readiness gate requiring recurring cross-source residuals; this does not invent or promote a mechanic by itself.
- `LearningMachine` — integrates library, competence, empirical contracts and ledger. Execution requires an external authority callback for every step.
- `math_eval` — P10 content-binding harness for frozen mathematical tasks, attempts and verifier receipts. It prevents statement/attempt receipt replay but does not decide verifier trust; that belongs to P4/P8.

## Security/scientific boundaries

1. Capability never self-authorizes execution.
2. Missing evidence is `UNKNOWN`/`CANNOT_CHECK`, not failure and not permission.
3. Donor identity is preserved through absorption.
4. Learned abstractions cannot erase donor-specific protected traits.
5. Source-text parsing is low authority; goal-state/effect traces are preferred for mechanic induction.
6. A result is not a verified mathematical success without an exact content-bound verifier receipt.
7. P9 invention is optional and gated; P5/P8 own self-improvement/promotion authority.

## Reproduce

From this directory:

```bash
python -m pytest -q
```

From the lane root, run `bash REPRODUCE_LOCAL_CLOSURE.sh` to execute the full local closure packet. The Phase-1 synthetic experiment is CPU-heavy.
