# Shadow mechanics completion — research and CI evidence, 2026-08-15

**Scope:** evidence for the control/resource/persistence/engineering completion layer in PR #14. This receipt does **not** claim that the 59 registered mechanics are step-specifically validated or benchmark-ready.

## Concurrent-base identity

This round explicitly preserves concurrent work on `shadow/self-orion-v0`.

- protected failure-learning hardening is in the ancestry through commit `8fe55170318cb6db8ab63820680dbf9ebf120f26`;
- the current PR #14 base observed during finalization is `563072724b7dc1a564a47fa46c4555469499be08` (`fix(mechanics): separate containment from dependencies`);
- that base upgrades the substrate to `MechanicCell.v1` / `TaskEpisode.v1`, separates containment from execution dependencies, and deliberately keeps generic envelopes provisional until step-specific contracts or justified waivers exist.

The completion branch must adapt to these stronger contracts rather than overwrite or weaken them.

## Knowledge-saturation routes used before repair

The development atom was challenged through multiple parent disciplines and source families rather than only the incumbent ORION vocabulary.

1. **Systems engineering / verification / technical management** — NASA Systems Engineering Handbook and NASA systems-modeling guidance were used to separate requirements, verification approach, objective evidence, technical measures, resource allocation, risk margin, interfaces and life-cycle traceability.
2. **Autonomic/self-managing systems** — IBM autonomic-computing work was used as an independent control-loop parent for monitor/analyze/plan/execute over retained knowledge and explicit managed-resource interfaces.
3. **Rational metareasoning** — work on rational algorithm selection and resource allocation was used to make meta-level computation explicitly consume the same finite resource pool as object-level execution; ORION therefore reserves object-level/verification capacity and refuses unbounded introspection when calibrated value-of-computation is absent.
4. **Open-world information retrieval** — Chen & Choi (NAACL 2025) was used as a reminder that relevance/diversity coverage is a distinct empirical coordinate; a route list is not evidence that all relevant perspectives were retrieved.
5. **Evidence-synthesis stopping** — capture/recapture-style systematic-review stopping work was treated as a parent for bounded recall estimation, not a proof of open-world completeness.
6. **Autonomous scientific-research evaluation** — AutoResearchBench and ResearchClawBench were used as external evidence that wide literature discovery, evidence/protocol matching and recovery of the scientific core remain difficult empirical capabilities and must stay outside implementation-only closure claims.

### Primary/authoritative sources used

- NASA, *Systems Engineering Handbook* (including the Requirements Verification Matrix, technical measures, technical resource allocation, and definition of margin).
- NASA-HDBK-1009A, *NASA Systems Modeling Handbook for Systems Engineering*.
- IBM Research autonomic-computing / autonomic-manager architecture publications.
- Hay, Russell, Tolpin & Shimony, *Selecting Computations: Theory and Applications* / rational metareasoning line of work; and related rational algorithm-selection work.
- Chen & Choi, *Open-World Evaluation for Retrieving Diverse Perspectives*, NAACL 2025, DOI 10.18653/v1/2025.naacl-long.431.
- Kastner et al., capture-mark-recapture stopping for systematic-review search, *Journal of Clinical Epidemiology* 2009.
- 2026 autonomous-research benchmark papers retained in the paper bibliography/research notes (AutoResearchBench; ResearchClawBench).

## What the research changed in code

The research did not merely add references. It changed the contract:

- `resources.py` now uses typed resources, accounting semantics, explicit uncertainty/risk margins, protected verification/recovery headroom, and a bounded metareasoning/object-execution partition;
- resource exhaustion with material obligations open returns `CANNOT_CHECK_RESOURCE_BOUND`/`BLOCKED`; it cannot mint saturation, success or authority;
- the optimization contract stays vector/Pareto-first and may use expected utility only when probabilities/tradeoffs are justified;
- diagnosis keeps recurrence separate from causal attribution and explicitly requires a **discriminator** when competing causes imply different repairs;
- PR #14 exports its completion modules through the public `orion.mechanics` and `orion.self_orion` surfaces;
- legacy fixtures were adapted to the stronger `TaskEpisode.v1` run/evaluation/split/evidence-binding identity instead of weakening the new base contract.

## CI falsification sequence

The branch was not promoted from the first green-looking implementation.

1. Initial PR #14 CI failed because `resources.py` did not exist and the completion controller was not publicly exported.
2. Static contract audit found two additional latent defects before CI reached them: optimization wrote a nonexistent `optimization_semantics` field instead of `optimization_rules`; diagnosis wrote `diagnosis_semantics` instead of `diagnosis_rules`.
3. After those repairs, CI reached 84 tests with one semantic-contract failure: the diagnosis rule described a separating action but did not explicitly name it a `discriminator`.
4. The next combined-base run exposed two further facts from concurrent Codex/base hardening:
   - old `TaskEpisode` test fixtures no longer satisfied `TaskEpisode.v1` identity/evidence-binding requirements;
   - the assertion that every mechanic had zero open questions was false under `MechanicCell.v1` provisional semantics.
5. The closure assertion was **not** weakened by clearing provisional flags. Instead, the test now requires the exact remaining provisional frontier to stay visible.

Pre-paper-binding green head: `2b90128b8bb8d8ca2ca12410c1c3a473a1a17be8`.

GitHub Actions CI run: `31908922105` — **SUCCESS**.

## Current bounded result

For the combined PR #12 + PR #14 state used by the green run:

- reachable mechanic cells: **59**;
- unknown containment children: **0**;
- containment cycles: **0**;
- unknown execution-dependency references: **0**;
- dependency cycles: **0**;
- remaining step-specific open questions: **472 = 59 × 8**;
- the eight deliberately provisional dimensions are:
  - verification;
  - failure semantics;
  - observability;
  - handoff;
  - state;
  - transition model;
  - mathematics;
  - dependencies.

The PR #14 completion layer closes its own generic control/persistence/engineering coordinates (actions, objectives, optimization, resources, diagnosis, storage, provenance, engineering) but **does not** erase these eight step-specific questions.

## Promotion boundary

The justified terminal for this PR is therefore:

`SHADOW_COMPLETION_LAYER_INTEGRATED__STEP_SPECIFIC_FRONTIER_OPEN`

It is not:

- `ALL_MECHANICS_BENCHMARKABLE`;
- `OPEN_WORLD_SATURATED`;
- `AUTONOMOUS_SCIENTIST_VALIDATED`;
- `GOVERNED_SELF_ORION_READY`.

The 472-question frontier becomes the next recursive research programme. It must be reduced through step-specific research/evidence or explicit justified waivers, not by reclassifying universal scaffolding as a substantive answer.
