# Paper 01 claim ledger

## Architectural claims

| Claim | Status | Evidence type |
|---|---|---|
| ORION state separates K, W and M | DEFINITION / IMPLEMENTED | `src/orion/core/`, registry, unit tests |
| Core operators are modular and provider-independent | IMPLEMENTED CONTRACT | `src/orion/engine/operators/`, `src/orion/providers/` |
| Search/generation cannot directly mint authority | IMPLEMENTED CONTRACT | transition validation + verification boundary |
| Final solve requires bounded stopping/flatness rather than an open-world recall claim | IMPLEMENTED CONTRACT | saturation/solver + stopping corrections |
| Parent-discipline, literature-bridge and omission routes are required by bootstrap saturation | IMPLEMENTED POLICY | saturation/search basis |
| High-impact ORION development requires a knowledge/formulation saturation packet | IMPLEMENTED GOVERNANCE CONTRACT | `src/orion/development/protocol.py` |
| Atomic ORION mechanics can be represented as partial typed mechanic cells whose unfilled dimensions generate deterministic research questions | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/model.py`, `questioning.py`, recursive tests |
| Nearest work is a first-class absorption object: useful mechanisms receive typed dispositions and a novelty comparison fails closed without nearest work, route closure and a falsifier | IMPLEMENTED RESEARCH CONTRACT / EXTERNAL NOVELTY NOT ESTABLISHED | `src/orion/knowledge/nearest_work.py`, nearest-work tests, `research/paper-programme-v1/` |
| A `CANDIDATE_DELTA` never by itself authorizes a publication novelty claim | IMPLEMENTED GOVERNANCE DEFINITION | `NearestWorkCase.v1`, `papers/SYNC_CONTRACT.md` |
| Local `REFRAME` is licensed only for formulation/search responsibilities; a singular `EVIDENCE` or `EXECUTION` diagnosis does not by itself authorize formulation rewrite | IMPLEMENTED / FOUND BY PAPER-I NEGATIVE FALSIFIER | `src/orion/engine/cycle.py`, `operators/reframe.py`, Paper-I hidden-shift suite |
| Scientific source interpretation has a proposal-level typed projection carrying predicate roles, referents, constructs, measurements, time, polarity, modality, discourse, attribution, assumptions and ambiguity before GLUE | IMPLEMENTED SHADOW CONTRACT / REAL NLP ADEQUACY OPEN | `src/orion/knowledge/semantics.py`, Paper-III semantic-atlas tests |
| Persistent Self-ORION issue state keeps issue identity, competing/supported causes, discriminator evidence, failure episodes, interventions and lifecycle transitions across repair attempts | IMPLEMENTED SHADOW CONTRACT / ADAPTED FROM NEAREST WORK | `src/orion/self_orion/issue_state.py`, Paper-V hostile tests |
| The five flagship paper hypotheses have separate local falsifier and external promotion gates; repository tests cannot make a paper publication-ready while the external gate is `CANNOT_CHECK` | IMPLEMENTED RESEARCH GOVERNANCE | `src/orion/benchmarks/`, `FlagshipEvidenceState` |
| Prior failure variations can be retained as immutable episodes and abstracted into candidate failure patterns without immediate promotion | IMPLEMENTED SHADOW CONTRACT | `src/orion/experience/`, unit tests |
| Replay and fresh-transfer evidence are distinct, run/task/split/evaluation/variation-bound gates; conditional reuse requires host-protected verification bound to exact candidate, complete episode contents, and mechanically compared evaluator/evidence/process lineages | IMPLEMENTED SHADOW CONTRACT / NOT YET LIVE-VALIDATED | `src/orion/experience/authority.py`, `learning.py`, hostile tests |
| Atomic mechanic trace events emit transition-consistent receipts and are recorded losslessly as parent-bound immutable experience episodes; caught operator/provider failures also enter this path | IMPLEMENTED SHADOW CONTRACT / NOT YET CRASH-DURABILITY-VALIDATED | `src/orion/engine/trace.py`, `solver.py`, `runtime.py` |
| Host-installed executable failure-pattern guards can be invoked and recorded end-to-end by the real runtime | IMPLEMENTED SHADOW CONTRACT / BENEFIT NOT YET LIVE-VALIDATED | `src/orion/engine/guards.py`, `solver.py`, runtime guard test |
| Universal mechanic envelopes remain provisional and cannot silently close step-specific audit questions | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/model.py`, `questioning.py`, provisional-dimension tests |
| Recursive audit blocks unknown dependencies and dependency cycles separately from containment defects | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/audit.py`, hostile dependency tests |
| Persistent `AnswerRecord` objects provide evidence-required, typed, conflict/supersession-aware mechanic-cell updates | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/answers.py`, answer-loop tests |
| All 24 registered RAKL method surfaces are reconstructed as scoped ORION transfer profiles; 49 leaf/cross-cutting mechanics receive direct/adjacent profiles and 10 top-level mechanics receive composition profiles | IMPLEMENTED SHADOW CONTRACT / PROVENANCE-BOUND | `src/orion/self_orion/rakl_transfer.py`, `provenance/rakl/TRANSFER_INVENTORY_V1.md` |
| A Shadow Self-ORION controller can select an empirical development question, run research, gate implementation on evidence, request a content-addressed coding proposal, run an isolated candidate, evaluate it under protected fresh assurance and only recommend host promotion | IMPLEMENTED SHADOW ARCHITECTURE / NOT LIVE-VALIDATED | `src/orion/self_orion/self_driving.py`, `change_control.py`, `factory.py` |
| LLM/Codex-style coding is a proposal-provider boundary, not the development controller or evaluator | IMPLEMENTED SHADOW ARCHITECTURE | `src/orion/providers/development/` |
| Multi-axis development saturation, structural novelty, experience-conditioned scheduling, append-only evolution history and an invention-readiness gate are reconstructed from RAKL as mechanical control semantics | IMPLEMENTED SHADOW CONTRACT | `src/orion/self_orion/{saturation_vector,novelty,experience_policy,evolution_archive,invention_gate}.py` |
| Self-ORION readiness is staged: architectural composition can establish Shadow capability, while governed Self-ORION still requires fresh empirical development and assurance evidence | IMPLEMENTED GOVERNANCE DEFINITION | `src/orion/self_orion/readiness.py`, readiness-stage tests |

## Flagship falsifier V1 evidence boundary

The deterministic five-paper suite passed at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`. This establishes only the registered local known-world/hostile semantics. `current_flagship_evidence_state()` deliberately reports every stronger external paper gate as `CANNOT_CHECK`, so the suite cannot transform software-test success into publication authority.

## Paper I nearest-work boundary

The working claim does **not** treat autonomous iterative science, multi-agent hypothesis evolution, tree search, structured world models or recursive systems engineering as novel. The scoped candidate is the typed co-evolution of `K/W/M`, responsibility-targeted formulation revision, dependency-directed reopening and recursive mechanic-cell self-audit.

The historical hidden-representation/search-universe-shift falsifier is executed and passed, including negative missing-evidence/execution controls. It remains underpowered for its original broad H1 and is retained as negative history.

The separate v2.2.4 mutation-necessity successor is powered and complete. On a prospectively frozen 2,882-world primary and disjoint replication, full ORION achieves protected hidden-shift success 1.0000 versus 0.4938/0.4833 for each of three strong assimilated parents, with paired advantages 0.5063/0.5167 whose 95% intervals exceed the 0.10 registered margin. ORION has zero unnecessary high-level control reframes, protected-sibling regressions, and forbidden high-level mutations in both runs. Every frozen gate passes. Independent verification recomputes all 40,348 score rows per run with zero score or analysis mismatches. Evidence: `research/revival/p1/confirmatory/v2.2/PRIMARY_REPLICATION_CONCORDANCE.json`, the two result directories, and their SHA-256 manifests.

A separate prospectively frozen 32-case protected goal-evolution closure supplies a distinct bounded sufficiency result. `FIXED_MULTI_OBJECTIVE_PARETO_PROTECTED` and `ORION_PROTECTED_GOAL_EVOLUTION` both make 32/32 correct next-action decisions, with zero false objective revisions, zero missed revisions, zero protected-constraint violations, zero protected-intent regressions, and 4/4 in every family. The fixed original objective misses all 16 cases that genuinely require revision, while the unconstrained and performance-triggered rewrite controls each produce 12 false revisions and protected failures. This supports **Objective-Basis Sufficiency** at the registered scope: when the candidate objective portfolio is decision-complete, protected responsibility diagnosis plus old-versus-candidate admission is sufficient for correct objective revision, and dynamic generation of additional objective content adds no decision value on this panel. Evidence: `research/goal-evolution/PROTECTED_GOAL_EVOLUTION_CLOSURE_V1.md`. Status: `SUPPORTED_BOUNDED`; the original ORION-specific dynamic-generation incremental-value hypothesis remains `REFUTED` and is not relabeled.

This establishes only the credential-free mechanical composition of lower-level exclusion, same-task counterfactual effect, protected-invariant preservation, dependency-impact binding, and the separately frozen objective-basis sufficiency result at its registered scope. Attribution, minimal repair, diagnosis-to-recovery admission, dependency rollback, causal-context slicing, and certificate enforcement are credited as donor substrate. Model-general and open-ended scientific superiority remain untested.

## Empirical claims deliberately not made

- ORION is superior to generic LLM research.
- ORION is externally novel merely because a nearest-work comparison produced `CANDIDATE_DELTA`.
- The local five-paper falsifier suite by itself proves external novelty or publication readiness.
- The powered P1 mechanical successor proves model-general or open-ended scientific superiority.
- Dynamic objective generation is universally unnecessary; Objective-Basis Sufficiency is established only where the tested candidate portfolio is decision-complete.
- ORION reliably achieves high literature recall on the open web.
- The required route family or mechanic-question registry is sufficient for unknown-unknown discovery.
- Governed Self-ORION improves ORION on fresh development tasks.
- The Shadow self-driving controller beats a simpler LLM/coding-agent development baseline.
- Failure-pattern matching or candidate guards improve fresh tasks in live research.
- The current global portrait implementation captures scientific semantics adequately on real multi-disciplinary literature.
- Transferred RAKL contracts are empirically valid in ORION merely because structural specification checks pass.

Those remain evaluation fibers.
