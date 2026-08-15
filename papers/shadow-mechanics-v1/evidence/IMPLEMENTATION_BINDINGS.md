# Implementation bindings — Shadow mechanics V1

The paper's implementation/formal claims are frozen against the combined Shadow source state after PR #14 merged into `shadow/self-orion-v0`.

## Frozen source / evaluation identity

- PR #14 mechanics merge commit: `6aba2f3a601f506b6e59a4c562257fe6776b94c2`.
- Combined PR #12 GitHub Actions CI run on that exact source head: `31909086245` — **SUCCESS**.
- Concurrent protected failure-learning ancestry is preserved, including `8fe55170318cb6db8ab63820680dbf9ebf120f26` and subsequent `MechanicCell.v1` / `TaskEpisode.v1` hardening.
- The final PR #12 paper-binding commit necessarily follows the frozen implementation head above; it changes documentation identity only and must itself pass CI before merge to `main`.

## Bound modular surfaces

- `src/orion/mechanics/model.py` — mechanic cell / metric / handoff primitives;
- `src/orion/mechanics/questioning.py` — deterministic typed question generation;
- `src/orion/mechanics/decomposition.py` — recursive provisional workflow/RAKL migration mapping;
- `src/orion/mechanics/program.py` — bootstrap/saturation-stage mechanics controller;
- `src/orion/mechanics/verification.py` — verification planning;
- `src/orion/mechanics/failure.py` — failure-mode/effect/cause/detection/recovery separation;
- `src/orion/mechanics/observability.py` — telemetry vs scientific measurement boundary;
- `src/orion/mechanics/handoff.py` — typed receipt envelope;
- `src/orion/mechanics/state_plan.py` — replay-bound execution state;
- `src/orion/mechanics/transition.py` — guarded lifecycle relation;
- `src/orion/mechanics/mathematics.py` — candidate formalism families and fail-closed assumption policy;
- `src/orion/mechanics/metrics.py` — non-compensatory root-aware metric vector;
- `src/orion/mechanics/uncertainty.py` — typed non-probabilistic uncertainty options;
- `src/orion/mechanics/invariants.py` — inherited/core non-escalation invariants;
- `src/orion/mechanics/dependencies.py` — dependency identity/failure/fallback contracts with containment separated from execution prerequisites;
- `src/orion/mechanics/parent_domains.py` — parent-discipline search hypotheses;
- `src/orion/mechanics/search_coverage.py` — OWMD-derived route obligations;
- `src/orion/mechanics/saturation_plan.py` — bounded saturation contract;
- `src/orion/mechanics/actions.py` — candidate mechanic action/effectors;
- `src/orion/mechanics/objectives.py` — root-aware objectives;
- `src/orion/mechanics/optimization.py` — constrained/Pareto control policy;
- `src/orion/mechanics/resources.py` — typed resources, margins, metareasoning partition and fail-closed exhaustion;
- `src/orion/mechanics/diagnosis.py` — evidence-discriminated attribution and discriminator requirement;
- `src/orion/mechanics/storage.py` — raw/canonical/working/episode/receipt/artifact/cache layers;
- `src/orion/mechanics/provenance.py` — evidential/transformation/computational/experience/governance/dependency lineage;
- `src/orion/mechanics/engineering.py` — determinism, idempotency, concurrency, recovery, SLO, schema/security/fault-injection contracts;
- `src/orion/engine/capability_router.py`, `mechanical_questions.py`, `mechanical_planner.py` — mechanical-first / LLM-bounded control surfaces;
- `src/orion/runtime/mechanical_control.py` — model-free control runtime surface;
- `src/orion/experience/*` — immutable `TaskEpisode.v1`, protected failure-pattern/guard verification and experience retrieval;
- `src/orion/self_orion/completion_program.py` — composed Shadow completion controller.

## Bounded interpretation

This binding demonstrates exact source identity and successful software tests for the implementation/formal claims in the Shadow paper. It does not provide live scientific-performance evidence. In particular, the 59-cell programme still exposes 472 step-specific questions across the eight deliberately provisional dimensions documented in the research/CI receipt.
