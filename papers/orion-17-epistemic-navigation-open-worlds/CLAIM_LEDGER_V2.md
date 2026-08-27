# ORION-17 claim ledger V2

**Paper:** Epistemic Navigation in Open Worlds  
**Theory status:** `CLOSED_V2`  
**Novelty status:** broad navigation novelty rejected; scoped residual stable under the dated two-round literature closure
**Rule:** donor mechanisms are engulfed as special cases; novelty must come from preservation/closure interaction, not from claiming adaptive search or representation change.

| ID | Permitted claim | Authority | Evidence / proof | Forbidden upgrade |
|---|---|---|---|---|
| ORION-17-C1 | ORION-17 defines an epistemic atlas: charts plus partial representation/objective transforms and preservation contracts. | FORMAL_DEFINITION | `manuscript/FORMAL_CORE_V2.md` | “ORION-17 invents changing search spaces.” |
| ORION-17-C2 | Under extension ambiguity, no history-only rule can soundly certify task completion across all admissible completions. | THEOREM | Thm. 1 | Claim without the extension-ambiguity premise. |
| ORION-17-C3 | Absence of an explicit closure certificate alone does not imply extension ambiguity; a richness/completion premise is required for that inference. | LOGICAL_BOUNDARY / COUNTEREXAMPLE | V2 closed-world fixture | “No certificate always means search must continue.” |
| ORION-17-C4 | A representation refinement can strictly increase worst-case solvability with latent states, dynamics, goals, actions and retained raw sensing fixed. | EXISTENCE_THEOREM | Thm. 3 + finite refinement fixture | “Any richer representation improves performance.” |
| ORION-17-C5 | Coarsening can destroy the same solvability, so reframing is not monotonically beneficial. | COUNTEREXAMPLE / NEGATIVE_CONTROL | V2 coarsening fixture | “Reframe whenever progress stalls.” |
| ORION-17-C6 | Content-valid evidence can remain unchanged while a transformed objective/obligation is no longer discharged. | THEOREM / DISCRIMINATOR | Thm. 4; x=5, threshold 3→7 construction | Evidence is generally useless after goal change. |
| ORION-17-C7 | A complete support-transport witness licenses closure transport under its premises. | THEOREM_WITH_WITNESS_SOUNDNESS | Thm. 5 | Automatic correctness of arbitrary schema/abstraction mappings. |
| ORION-17-C8 | Incomplete and target-ambiguous transport requires reopen or `CANNOT_CHECK`; incomplete but non-ambiguous transport does not imply semantic failure. | THEOREM / BOUNDARY | Thm. 6 + 960 transport cases (64 coordinate combinations × 15 admissible target completion classes), target-ambiguity decided per case by `extension_ambiguous` over a finite completion pool, not proved over all admissible classes | “Missing transport proof proves the old result false.” / “The finite completion pool is a proof over Definition 14.” |
| ORION-17-C9 | `ROUTE_STOP`, `TASK_STOP`, `CONTINUE` and `CANNOT_CHECK` are semantically distinct terminals. | FORMAL_POLICY / EMBEDS_P2 | formal core + checker | Novelty over ORION-12 route/task stopping. |
| ORION-17-C10 | Fixed-graph navigation, POMDP belief-space planning, planning abstraction, schema/lens mappings, goal evolution and world-model revision can supply donor components/special cases in the atlas. | REPRESENTATION_LEVEL_DONOR_EMBEDDING | `FINAL.md` + donor envelope | ORION-17 inherits every theorem or benchmark result of those fields. |
| ORION-17-C11 | The V2 checker covers stopping ambiguity, certificate boundary, fixed-information refinement/coarsening, evidence-vs-closure, 960 transport cases (64 coordinate combinations × 15 completion classes) and stop terminals; `theory_closure_terminal` is `PASS`. | DETERMINISTIC_ARTIFACT_FACT | `formal/check_theory_closure_v2.py` | Real-agent performance claim. Reading the 960 as the earlier 64 grown: 64 was an enumeration downstream of an undecided premise and reported 1 decided case. |
| ORION-17-C12 | The strongest future comparison is an integrated donor product with correct adapters; ORION should not claim superiority merely by containing more modules. | PROGRAMME_DESIGN | donor-complete envelope | “ORION already beats Search-on-Graph/POMDP/SAGA/world-model systems.” |
| ORION-17-C13 | Route identity binds chart/objective, initial obligations and normalized trace; equivalence/refinement require protected structure- and obligation-preserving maps rather than content overlap. | FORMAL DEFINITION / CHECKER | Def. 8.1 + route-relation cases | Novel route-diversity algorithm claim. |
| ORION-17-C14 | Defer/revisit, witness-backed backtracking and forced reframe are distinct recovery transitions and never silently assert task completion. | FORMAL POLICY / REFERENCE CONTRACT | Def. 8.2 + frozen dead-end/revisit/reframe cases | Empirical optimality of the recovery policy. |

## Donor ownership that must remain visible

ORION-17 treats as donor/pre-existing: graph/knowledge-graph navigation, exploratory search, POMDP and belief-space information gathering, planning abstraction/homomorphism and representation languages, schema evolution/lenses/ontology mappings, objective/goal evolution including SAGA, self-evolving world models, orientation/initial exploration, scientific-search breadth, and ORION-12 route/task stopping.

## Allowed headline

> Scientific navigation across changing representations requires explicit evidence/obligation preservation semantics: representation refinement can change solvability without new sensing, while evidence can survive a reframe even when scientific closure does not.

## Disallowed headlines

- “A new theory of search/navigation.”
- “The first adaptive topology-changing agent.”
- “Changing representations always improves inquiry.”
- “ORION-17 outperforms graph search, POMDP, planning abstraction, SAGA or world-model agents.”

Empirical superiority requires frozen donor-product comparisons and protected result artifacts.
