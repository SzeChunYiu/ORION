# P7 claim-ledger addendum V3

**Date:** 2026-08-24
**Rule:** additive rows only; V1–V4 and ADDENDUM_V2 boundaries remain
unchanged. `CLAIM_LEDGER_V4.md` is not edited by this addendum (it is touched
by open PR #1065); nothing here modifies a row in it.

| ID | Claim | Status | Authority | Boundary / reopen trigger |
|---|---|---|---|---|
| P7.C-V3.1 | The intermediate-contract test `Match(a,b) := a = b OR Bridge(a,b)` is replaced by exact containment `Contains(a,b) := forall o. Demands(b,o) -> Demands(a,o)` in the coordinate transport axiom, everything else in the calculus unchanged. | `ARTIFACT_FACT` | `src/orion/study/p7/exact_containment.py`; contract `P7.CONTAIN.EXACT_BRIDGE_RULE.V1` | Reopen on calculus axiom change. |
| P7.C-V3.2 | The replacement rule is sound for the obligation semantics, and its side condition is not droppable (a two-total-leg, non-containing, non-total-composite model exists). | `LOCAL_DETERMINISTIC` | solver discharges; receipt `formal/mechanized/P7_EXACT_CONTAINMENT_MECHANIZED_2026-08-24.json` | z3 refutation + closed-world witness; no claim beyond the stated axiom set. |
| P7.C-V3.3 | The replacement subsumes the old rule (nothing previously licensed is lost) and strictly weakens it (an obligation-equivalent, distinct, unbridged hand-off is licensed). | `LOCAL_DETERMINISTIC` | same receipt | "Completeness" means exactly these two discharges plus P7.C-V3.2; it is not a claim about every conceivable rule. |
| P7.C-V3.4 | Containment is reflexive and transitive; the unit and associativity laws of the exact calculus hold observationally and, under extensionality, as equations. | `LOCAL_DETERMINISTIC` | same receipt | Extensionality is a declared modelling axiom, named in the receipt. |
| P7.C-V3.5 | The exact-calculus axiom set is satisfiable (vacuity guard) with a demanded obligation and containment both ways between distinct contracts. | `LOCAL_DETERMINISTIC` | same receipt | Guards vacuous PROVED lines only; not an empirical model. |
| P7.C-V3.6 | The data-heavy sub-box: >=2 non-retrieval domains, >=50 transitions/domain under the exact rule. | `CANNOT_CHECK` | no such corpus in the repository | Requires a domain/transition corpus that does not exist in-repo; not simulated. |

### Prohibited inference

`EXACT_BRIDGE_RULE` discharge does **not** retract the composition calculus's
incompleteness theorem about the old rule (that theorem is its reason for
existing), does not license any empirical or deployed-agent claim, and is not
independent formal review: every discharge was produced and checked in the
same lane with z3.
