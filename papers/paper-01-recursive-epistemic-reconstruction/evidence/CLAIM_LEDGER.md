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

## Paper I nearest-work boundary

The working claim does **not** treat autonomous iterative science, multi-agent hypothesis evolution, tree search, structured world models or recursive systems engineering as novel. The current scoped candidate is the typed co-evolution of `K/W/M`, responsibility-targeted formulation revision, dependency-directed reopening and recursive mechanic-cell self-audit. Its hidden-representation/search-universe-shift falsifier remains unexecuted.

## Empirical claims deliberately not made

- ORION is superior to generic LLM research.
- ORION is externally novel merely because a nearest-work comparison produced `CANDIDATE_DELTA`.
- ORION reliably achieves high literature recall on the open web.
- The required route family or mechanic-question registry is sufficient for unknown-unknown discovery.
- Governed Self-ORION improves ORION on fresh development tasks.
- The Shadow self-driving controller beats a simpler LLM/coding-agent development baseline.
- Failure-pattern matching or candidate guards improve fresh tasks in live research.
- The current global portrait implementation captures scientific semantics adequately.
- Transferred RAKL contracts are empirically valid in ORION merely because structural specification checks pass.

Those remain evaluation fibers.
