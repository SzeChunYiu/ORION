# Implementation bindings — Shadow mechanics V1

The paper's implementation claims bind to these modular surfaces on `shadow/mechanics-completion-v1`:

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
- `src/orion/mechanics/dependencies.py` — dependency identity/failure/fallback contracts;
- `src/orion/mechanics/parent_domains.py` — parent-discipline search hypotheses;
- `src/orion/mechanics/search_coverage.py` — OWMD-derived route obligations;
- `src/orion/mechanics/saturation_plan.py` — bounded saturation contract;
- `src/orion/mechanics/actions.py` — candidate mechanic action/effectors;
- `src/orion/mechanics/objectives.py` — root-aware objectives;
- `src/orion/mechanics/optimization.py` — constrained/Pareto control policy;
- `src/orion/mechanics/resources.py` — resource accounting/exhaustion semantics;
- `src/orion/mechanics/diagnosis.py` — evidence-discriminated attribution;
- `src/orion/mechanics/storage.py` — raw/canonical/working/episode/receipt/artifact/cache layers;
- `src/orion/mechanics/provenance.py` — evidential/transformation/computational/experience/governance/dependency lineage;
- `src/orion/mechanics/engineering.py` — determinism, idempotency, concurrency, recovery, SLO, schema/security/fault-injection contracts;
- `src/orion/self_orion/completion_program.py` — composed Shadow specification controller.

Bindings are path-level until the branch is reviewed/frozen to a merge commit. Paper promotion must replace mutable branch references with the exact merge/source commit and CI/test receipts.
