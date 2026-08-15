# Paper 01 claim ledger

## Architectural claims

| Claim | Status | Evidence type |
|---|---|---|
| ORION state separates K, W and M | DEFINITION / IMPLEMENTED | `src/orion/core/`, registry, unit tests |
| Core operators are modular and provider-independent | IMPLEMENTED CONTRACT | `src/orion/engine/operators/`, `src/orion/providers/` |
| Search/generation cannot directly mint authority | IMPLEMENTED CONTRACT | transition validation + verification boundary |
| Final solve requires bounded saturation | IMPLEMENTED CONTRACT | `SaturateOperator` + solver |
| Parent-discipline, literature-bridge and omission routes are required by bootstrap saturation | IMPLEMENTED POLICY | saturation basis v2/v3 |
| High-impact ORION development requires a knowledge/formulation saturation packet | IMPLEMENTED GOVERNANCE CONTRACT | `src/orion/development/protocol.py` |
| Atomic ORION mechanics can be represented as partial typed mechanic cells whose unfilled dimensions generate deterministic research questions | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/model.py`, `questioning.py`, recursive tests |
| Prior failure variations can be retained as immutable episodes and abstracted into candidate failure patterns without immediate promotion | IMPLEMENTED SHADOW CONTRACT | `src/orion/experience/`, unit tests |
| Replay and fresh-transfer evidence are distinct, run/task/split/evaluation/variation-bound gates; conditional reuse requires host-protected Ed25519 verification bound to exact candidate, complete episode contents, and mechanically compared evaluator/evidence/process lineages | IMPLEMENTED SHADOW CONTRACT / NOT YET LIVE-VALIDATED | `src/orion/experience/authority.py`, `learning.py`, hostile forgery/lineage/content-substitution tests |
| Atomic mechanic trace events emit transition-consistent receipts and are recorded losslessly as parent-bound immutable experience episodes; caught operator/provider failures also enter this path | IMPLEMENTED SHADOW CONTRACT / NOT YET CRASH-DURABILITY-VALIDATED | `src/orion/engine/trace.py`, `solver.py`, `runtime.py`, receipt round-trip and provider-exception tests |
| Host-installed executable failure-pattern guards can be invoked and recorded end-to-end by the real runtime | IMPLEMENTED SHADOW CONTRACT / BENEFIT NOT YET LIVE-VALIDATED | `src/orion/engine/guards.py`, `solver.py`, runtime guard test |
| Universal mechanic envelopes remain provisional and cannot silently close step-specific audit questions | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/model.py`, `questioning.py`, provisional-dimension tests |
| Recursive audit blocks unknown dependencies and dependency cycles separately from containment defects | IMPLEMENTED SHADOW CONTRACT | `src/orion/mechanics/audit.py`, hostile dependency tests |

## Empirical claims deliberately not made

- ORION is superior to generic LLM research.
- ORION reliably achieves high literature recall on the open web.
- The required route family or mechanic-question registry is sufficient for unknown-unknown discovery.
- Self-ORION improves ORION on fresh development tasks.
- Failure-pattern matching or candidate guards improve fresh tasks in live research.
- The current global portrait implementation captures scientific semantics adequately.

Those remain evaluation fibers.
