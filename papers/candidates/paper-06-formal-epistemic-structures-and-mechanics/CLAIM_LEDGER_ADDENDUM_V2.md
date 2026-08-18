# P6 claim ledger V2 — corrected theorem rows

**Date:** 2026-08-17  
**Rule:** this file supersedes V1 rows `P6.C2`–`P6.C4`; all other V1 rows retain their previous authority unless separately changed.

| ID | Corrected claim | Status | Current authority | Scope / reopen trigger |
|---|---|---|---|---|
| P6.C2 | Downstream reopening is sufficient to remove every potentially invalidated certification under support-soundness. | `FORMAL` | `manuscript/FORMAL_CORE_V2_CORRECTIONS.md`, Theorem V2.1; V1/V2 finite checks | Safety only. Does not assert every graph descendant is actually invalid. Reopen if dependency-soundness definition or mutation scope changes. |
| P6.C3 | Descendant reopening is inclusion-minimal among graph-only strategies that must be uniformly sound over a path-realizable graph-compatible semantics class. | `FORMAL_WITH_STRONG_PREMISE` | Theorem V2.2; stale/path-realizable and spurious-edge controls | V1 wording from soundness alone is `STRUCK`. No claim that real ORION graphs satisfy path realizability. |
| P6.C4 | Strongly operationally separated deterministic mechanics commute on the scientific projection when read/write footprints are faithful; ordered histories are distinct but equivalent modulo independent swaps. | `FORMAL_WITH_STRONG_PREMISE` | Theorem V2.3; bounded commutation and trace checks | No literal whole-state/history equality. Reopen on hidden reads, ambient state, shared authority/provenance/obligations or nondeterministic coupling. |

## Explicitly struck language

- “Dependency soundness alone proves minimal reopening.”
- “Disjoint declared footprints alone prove commutation.”
- “The complete mechanic states, including ordered histories, are equal under independent execution order.”

## Unchanged high-risk claims

The following remain `CANNOT_CHECK` exactly as in V1:

- faithful correspondence to the complete current ORION registry;
- novelty relative to the combined donor literature;
- empirical advantage over strong alternative formalisms;
- separate-paper status and peer-review readiness.
