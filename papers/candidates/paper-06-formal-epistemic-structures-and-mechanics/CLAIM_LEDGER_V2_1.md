# P6 claim ledger V2.1

**Normative manuscript:** `manuscript/FINAL_V2_1.md`  
**Normative formal core:** `manuscript/FORMAL_CORE_V2_1.md`  
**Theory:** `FINISHED_V2_1`

This ledger supersedes P6 V2 claims where theorem assumptions differ.

| ID | Permitted claim | Authority | Forbidden upgrade |
|---|---|---|---|
| P6.1 | Root-inclusive affected-set reopening is safe under a support-sound dependency abstraction. | THEOREM | Every reopened node is actually invalid. |
| P6.2 | Support soundness alone does not imply graph-descendant minimality when conservative/spurious edges are allowed. | COUNTEREXAMPLE | Conservative graphs are useless. |
| P6.3 | Root-inclusive affected-set invalidation/revalidation is minimax inclusion-minimal for graph-only strategies under an explicit affected-realizability compatible semantics class. | THEOREM_WITH_RICHNESS_PREMISE | Minimality for an arbitrary fixed semantics class or arbitrary real ORION graph. |
| P6.4 | Protected exact-change proofs may preserve an unchanged affected descendant; a directly changed certified root requires protected revalidation/new certification rather than continuity of its old certificate. | FORMAL_POLICY / THEOREM_BOUNDARY | Automatic correctness of preservation/revalidation proofs. |
| P6.5 | Full scientific current-state commutation requires faithful declared semantic footprints plus separation of authority/provenance/obligation/dependency/resource side conditions. | THEOREM | Declared read/write names alone prove commutation. |
| P6.6 | Hidden ambient reads provide a counterexample to commutation from declared separation without footprint fidelity. | COUNTEREXAMPLE | All real agent implementations contain hidden reads. |
| P6.7 | Sequential, authorized conditional, independent-parallel and rank/cycle-guarded recursive composition have explicit interface, obligation, provenance and authority well-formedness conditions. | FORMAL CONTRACT / THEOREM BOUNDARY | Novelty over donor process, authorization, effect or recursion fields. |
| P6.8 | Bare computation/dependency erasure is not fully abstract for P6 scientific admissibility. | THEOREM / MAIN DISCRIMINATOR | Dependency/incremental systems are incorrect for their native goals. |
| P6.9 | TMS/ATMS, self-adjusting computation, DEL/revision, typed effects, authorization/provenance and modern repair systems are engulfed donors/special cases. | DONOR EMBEDDING POLICY | P6 owns their mechanisms or inherits every donor theorem/efficiency bound. |
| P6.10 | V2.1 checker explicitly freezes spurious-edge, affected-realizability and hidden-read regressions. | DETERMINISTIC ARTIFACT FACT | Real-agent efficacy. |

## Allowed headline

> P6 adds a scientific-admissibility contract above engulfed dependency/effect/authorization mechanisms: support-sound graphs give safe repair, robust minimality needs an explicit realizability class, and computationally identical transitions can still differ in certification/commit admissibility.

## Prohibited headline

- “Sound dependency graphs imply minimal reopening.”
- “Every graph descendant must always reopen.”
- “Declared read/write separation alone proves commutation.”
- “P6 invents dependency repair, effect typing, authorization or incremental computation.”
- “P6 already outperforms the donor product.”
