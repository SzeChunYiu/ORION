# P6 claim ledger V2

**Paper:** Formal Epistemic Structures and Mechanics  
**Theory status:** `CLOSED_V2`  
**Novelty status:** `CANNOT_CHECK` pending programme literature closure  
**Rule:** no sentence may upgrade a donor mechanism into a P6 novelty claim merely because it appears inside the ORION envelope.

| ID | Permitted claim | Authority | Evidence / proof | Forbidden upgrade |
|---|---|---|---|---|
| P6-C1 | P6 defines a typed mechanic contract including state effects, hard obligations, provenance, authority and retained history. | FORMAL_DEFINITION | `manuscript/FORMAL_CORE_V2.md` Defs. 1–4 | “P6 is the first typed formalism for agent actions.” |
| P6-C2 | Strict-descendant reopening is insufficient when the changed set may contain a certified claim. | PROVED_COUNTEREXAMPLE / REPAIR | V2 affected-set definition + theory checker changed-root cases | “All prior dependency repair is unsound.” |
| P6-C3 | Root-inclusive reopening is sound under the stated dependency-soundness abstraction. | THEOREM | `FORMAL_CORE_V2.md` Thm. 1 | Universal causal/relevance completeness. |
| P6-C4 | Root-inclusive reopening is inclusion-minimal for uniformly sound strategies restricted to graph-only information. | THEOREM_WITH_SCOPE | Thm. 2 | Minimal among strategies using richer semantic knowledge. |
| P6-C5 | A protected exact-change preservation certificate may safely retain a downstream affected certificate under the stated premises. | THEOREM_WITH_ASSUMED_CERT_SOUNDNESS | Thm. 3 + 64 checker cases | Automated certificates are always correct. |
| P6-C6 | Semantically separated mechanics commute on current scientific state while their ordered histories need only be independent-trace equivalent. | THEOREM | Thm. 4 + checker | Literal equality of ordered histories. |
| P6-C7 | Finite sequential composition of non-escalating mechanics remains non-escalating. | THEOREM | Thm. 5 | Claims about every delegation/authorization calculus. |
| P6-C8 | An emitted hard obligation persists until an authorized discharge or a typed non-success terminal. | THEOREM | Thm. 6 + checker | Claim that ETAS or other residual-obligation systems lack this property. |
| P6-C9 | Rank-decreasing or cycle-guarded recursive audit terminates. | ELEMENTARY_THEOREM | Thm. 7 + cycle fixtures | Novel recursion theorem. |
| P6-C10 | Candidate control of its own admission predicate and all predicate evidence cannot guarantee an externally defined promotion property. | COUNTERMODEL / BOUNDARY | Prop. 8 | Universal impossibility of safe self-modification. |
| P6-C11 | Bare transition/dependency erasure is not fully abstract for P6 admissibility: identical bare transitions can have different obligation/authority admissibility. | THEOREM / DISCRIMINATOR | Thm. 9 + typed-erasure checker | “Dependency maintenance is inadequate in general.” |
| P6-C12 | Ordinary transition systems, graph dependency maintenance, self-adjusting computation and typed effects can be represented as conservative special cases under inert P6-only dimensions. | REPRESENTATION_LEVEL_EMBEDDING | Props. 10–13 | P6 inherits every donor theorem, efficiency bound, implementation or empirical result. |
| P6-C13 | The V2 checker exercises 960 DAG/change combinations plus preservation, composition, obligation, authority and recursion fixtures. | DETERMINISTIC_ARTIFACT_FACT | `formal/check_theory_closure_v2.py` | Real-agent performance or frequency estimate. |
| P6-C14 | The donor-complete ORION envelope attempts to compose TMS/ATMS, incremental computation, effect, authorization and provenance structures rather than excluding them. | PROGRAMME_DESIGN | `../DONOR_COMPLETE_ORION_ENVELOPE_V1.md` | “ORION outperforms all donors.” |

## Donor ownership that must remain visible

P6 explicitly treats as donor/pre-existing: TMS/JTMS/ATMS, self-adjusting and incremental computation, dynamic epistemic/action logics, belief revision, separation/process trace theory, typed/algebraic effects, authorization/delegation/revocation, provenance/audit, CoALA, ETAS, FAVA, AgentTether, dependency-guided rollback repair, and ORION P1 mechanic/reopen ownership.

## Allowed headline

> A history-aware typed epistemic mechanic contract with root-inclusive certificate-aware repair, hard-obligation persistence and scoped commit authority separates scientific admissibility from bare computation/dependency semantics.

## Disallowed headlines

- “The first formal theory of epistemic mechanics.”
- “A new theory of dependency repair.”
- “ORION subsumes all effect systems/authorization logics.”
- “P6 outperforms TMS, self-adjusting computation, ETAS or FAVA.”

Any empirical superiority sentence requires a separate prospective comparison and result artifact.
