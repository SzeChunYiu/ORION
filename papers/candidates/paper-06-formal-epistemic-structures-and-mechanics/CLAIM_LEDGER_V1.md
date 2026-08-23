# P6 claim ledger V1

**Candidate:** Formal Epistemic Structures and Mechanics  
**Date:** 2026-08-17  
**Rule:** no abstract/conclusion claim may exceed this ledger.

| ID | Claim | Status | Current authority | Scope / reopen trigger |
|---|---|---|---|---|
| P6.C1 | The candidate defines typed epistemic states, mechanic contracts, authority-scoped writes, dependencies and reopening. | `FORMAL` | `manuscript/FORMAL_CORE_V1.md` Definitions 1–11 | Definition only; revise after exact ORION registry mapping. |
| P6.C2 | Downstream reopening is sufficient under dependency-soundness. | `FORMAL` | Theorem 1 + finite checks | Relative to a sound/complete dependency abstraction. Reopen if assumptions change. |
| P6.C3 | Downstream reopening is inclusion-minimal among uniformly sound graph-only strategies. | `FORMAL` | Theorem 2 + countermodel construction | Does not claim the graph is complete in real systems. |
| P6.C4 | Strongly separated deterministic mechanics commute. | `FORMAL` | Theorem 3 + 1,536 bounded cases | Only under stated read/write/authority/provenance separation. |
| P6.C5 | Sequential composition of non-escalating mechanics remains non-escalating. | `FORMAL` | Theorem 4 + 8,192 bounded compositions | Trusted-root correctness is assumed, not proved. |
| P6.C6 | Rank-decreasing recursive audit terminates. | `FORMAL` | Theorem 5; self-loop countermodel | Standard well-founded result; not novelty. |
| P6.C7 | Candidate-controlled admission cannot establish external promotion soundness. | `FORMAL_COUNTERMODEL` | Proposition 6 + deterministic fixture | Requires candidate control over both policy and evidence; protected constraints escape the result. |
| P6.C8 | The formal signature corresponds faithfully to current ORION mechanic/state objects. | `CANNOT_CHECK` | No full registry correspondence yet | Requires #333/#335 exact mapping and coverage report. |
| P6.C9 | The coupled mechanic-contract residual is not already solved by DEL, belief revision, TMS, process/separation or authorization formalisms. | `CANNOT_CHECK` | Initial pressure ledger only | Requires #334/#318 saturation and #287 certificate. |
| P6.C10 | The calculus catches important errors or preserves valid state better than a strong alternative formalization. | `CANNOT_CHECK` | No discriminating evaluation | Requires frozen comparison and #283 verification for any positive. |
| P6.C11 | P6 is a distinct paper rather than a formal section/appendix of P1. | `CANNOT_CHECK` | Ownership risk explicitly recorded | Requires #343 terminal with a non-duplicative theorem/evaluation residual. |
| P6.C12 | P6 is peer-review ready. | `STRUCK_PENDING_EVIDENCE` | None | Needs novelty closure, independent proof review, clean checks, complete manuscript and venue audit. |

## Prohibited current headline language

Do not claim `novel calculus`, `first formalization`, `complete semantics`, `verified autonomous science`, `general improvement`, or `peer-review ready` while P6.C8–C12 remain unresolved.
