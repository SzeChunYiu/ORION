# P6–P8 expert-review ledger V2

**Date:** 2026-08-17  
**Status:** internal adversarial review record  
**Independence boundary:** these are explicitly separated analytical roles used in one research session, not independent human referees.

## Review group

| Role | Background used | Assigned responsibility |
|---|---|---|
| Formal logician | dynamic/epistemic logic, proof theory, quantifier and model-class discipline | audit theorem statements, identify hidden existence/uniformity assumptions, construct countermodels |
| Formal-methods engineer | Hoare-style contracts, separation/local reasoning, executable finite-model checking | translate premises into checkable contracts; distinguish declared footprints from enforced footprints |
| Navigation theorist | graph search, partial observability, open-world stopping, representation/model change | separate fixed-chart search from atlas change; define stopping and transport discriminators |
| Authorization/security logician | authorization logic, delegation, revocation, information-flow and policy composition | attack cross-domain coercions, protected roots, deny-all loopholes and post-hoc authorization |
| Benchmark/statistics reviewer | prospective benchmark design, negative controls, matched baselines and error decomposition | freeze case families/terminals without fabricating effect sizes; enforce positive and negative controls |
| Novelty editor | internal P1–P5 ownership and nearest-work assimilation | strike relabeled contributions; assign keep/merge/technical-companion dispositions |

## Finding 1 — P6 reopening minimality

**Formal logician:** The V1 proof moves from “the graph is sound” to “choose a compatible semantics making every path necessary.” That is an existential closure property of the admissible model class, not a consequence of graph soundness.

**Formal-methods engineer:** The exhaustive V1 DAG checker verifies the implementation identity `retained = certified - descendants`; it cannot establish that every graph edge is semantically realizable. A finite graph enumeration therefore does not repair the proof gap.

**Novelty editor:** Even after correction, selective reopening is not a standalone novelty claim because truth-maintenance and dependency-guided repair are direct donors and P1 owns ORION's native reopening mechanism.

**Resolution:** preserve sufficiency under soundness; restate minimality under path realizability/robust graph-compatible semantics; add a spurious-edge negative control; keep the result as supporting P6 theory, not a headline novelty by itself.

## Finding 2 — P6 commutation

**Formal-methods engineer:** Declared disjointness is only trustworthy if transition outputs are extensional in declared reads and writes are mechanically confined. Hidden ambient reads can break commutation while declarations remain disjoint.

**Formal logician:** The proper equality is on the scientific projection. Ordered audit histories are intentionally unequal, with equivalence defined by swapping independent events.

**Resolution:** add footprint-fidelity wording, keep scientific-projection equality, and test distinct-but-trace-equivalent histories.

## Finding 3 — P7 benchmark identifiability

**Navigation theorist:** A benchmark containing only beneficial reframes would reward indiscriminate topology change. A retrieval-only benchmark would collapse back toward P2.

**Benchmark reviewer:** Each case needs a frozen terminal and gold obligations, but the reference oracle must not be described as an agent baseline. At least one harmful-reframe negative control and one non-retrieval transfer case are mandatory.

**Novelty editor:** Route independence, route/task stopping and censored coverage remain P2-owned. P7 survives only through chart/objective change plus support transport/reopening and a distinct transfer result.

**Resolution:** freeze eight executed contracts spanning hidden branches, unknown/censored coverage, deceptive diversity, revisit, beneficial/harmful topology change and non-retrieval experimental design.

## Finding 4 — P8 total-refusal loophole

**Authorization/security logician:** A calculus can score zero laundering by authorizing nothing. That is not a useful authority system.

**Benchmark reviewer:** Pair every blocked case with a clean authorized case and report unauthorized action jointly with unnecessary refusal/authorized coverage.

**Formal logician:** A typed anti-laundering theorem is only as good as the coercion registry. The suite therefore needs a valid explicit coercion case as well as missing-coercion attacks.

**Novelty editor:** Every within-domain gate belongs to P1–P5. P8 can own only cross-domain composition/coercion/revocation value beyond faithful embeddings of those gates.

**Resolution:** freeze five clean within-domain cases, five paired blocked cases, five laundering attacks, one `CANNOT_CHECK` case and one clean authorized cross-domain coercion case.

## Finding 5 — paper-level dispositions

| Candidate | Review disposition | Reason |
|---|---|---|
| P6 | `KEEP_CANDIDATE_UNDER_TECHNICAL_COMPANION_PRESSURE` | a history-aware effect/repair algebra may survive, but native mechanic/reopening/audit claims belong to P1 and donor pressure is severe |
| P7 | `KEEP_CANDIDATE_PROSPECTIVE` | the atlas/transport/closure object is the clearest non-duplicative residual and has a mandatory non-retrieval discriminator |
| P8 | `KEEP_CANDIDATE_WITH_MERGE_PRESSURE` | cross-domain laundering may justify a paper; failure to beat faithful independent P1–P5 gates collapses it into programme/P4 synthesis |

## Remaining disagreements not resolved by local work

1. Whether P6's coupled algebra is absent from the combined formal-methods literature remains `CANNOT_CHECK`.
2. Whether P7's atlas mechanism improves root success under matched resources remains `CANNOT_CHECK`.
3. Whether P8's shared calculus catches failures missed by correct independent gates without excess refusal remains `CANNOT_CHECK`.
4. No role in this ledger counts as independent external verification.
