# P9 top-tier promotion V1 — Representation Accessibility as a Scaling Coordinate

**Programme:** #977  
**Existing controlled authority:** `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR` remains valid for its bounded package.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Learning and reasoning scale along at least three separable coordinates: semantic information, representation accessibility and downstream computation.** Increasing model or inference resources is scientifically uninterpretable until these coordinates are disentangled. P9 provides a protected diagnostic methodology and demonstrates predictable crossovers among representation repair, explicit inference and model/compute escalation on real systems.

P9 does not reclaim graph inductive bias, serialization friction, generic representation-vs-reasoning distinction, domain generalization or a new neural architecture. Those remain donor-owned.

## Upward scientific object

Define a response surface over:

`Q = f(I, A, C, M)`

where:

- `I` = semantic task information available to the system;
- `A` = accessibility of that information under the frozen representation/interface;
- `C` = downstream computation/search/inference budget;
- `M` = model/access mechanism capacity.

The paper must empirically separate interventions on these coordinates rather than infer the cause of failure from final accuracy alone.

## Protected real-system programme

### E9.1 — Same-information accessibility scaling

Freeze tasks where two representations carry the same semantic information but differ in accessibility. Sweep at least:

- small/medium/large open-weight models or access mechanisms;
- multiple inference/search budgets;
- native/structured representation;
- same-information serialization;
- deliberately lossy/missing-information view;
- explicit deterministic inference control when the operation is known.

Primary question: does additional model/compute close an accessibility deficit, and at what resource cost relative to representation repair?

### E9.2 — Causal diagnostic intervention

For failures pre-classified prospectively as candidate information/accessibility/computation failures, intervene on exactly one coordinate at a time. Score diagnosis by whether the targeted intervention closes the protected failure without changing the other coordinates.

### E9.3 — Cross-domain transfer of the diagnostic

Execute the frozen diagnosis/intervention procedure in at least two qualitatively distinct domains, preferably:

1. open-weight procedural/agent tasks;
2. verifier-backed formal/search tasks.

Do not use sibling-paper labels as gold diagnoses.

## Strong comparators

- model-size escalation;
- best-of-N / test-time search escalation;
- representation/context-selection baseline;
- graph/relational or native-state baselines relevant to the domain;
- explicit symbolic/deterministic inference where available;
- same-information serialization controls;
- oracle information ceiling only as diagnostic, not a runnable superiority baseline.

All arms must receive matched semantic information and explicit total-resource accounting.

## Primary endpoints

- verified/task success at matched information and resource budget;
- resource needed to reach a frozen quality target;
- diagnosis accuracy for information vs accessibility vs computation failure;
- false escalation rate to larger models/compute;
- transfer of the diagnostic policy across domains;
- interaction/crossover surface among `A`, `C` and `M`.

## Strongest hostile attacks

- structured view secretly contains extra semantic information;
- serialization is merely longer and loses due to context truncation;
- stronger model closes every effect, making accessibility non-distinct;
- explicit inference control is an oracle unavailable to realistic systems;
- post-hoc failure labels make diagnosis appear causal;
- cross-domain success comes from domain-specific tuning;
- result merely restates known representation or scaling effects without a separable diagnostic law.

## Top-tier promotion gate

`P9_TOP_TIER_SUBMISSION_READY` requires:

- [ ] same-information real-system scaling surface;
- [ ] prospectively frozen one-coordinate causal interventions;
- [ ] diagnosis accuracy significantly above generic uncertainty/failure heuristics;
- [ ] at least two qualitatively distinct domains;
- [ ] matched model/inference/representation resource accounting;
- [ ] strong model-size and test-time-compute comparators;
- [ ] exact preservation of the bounded P9 negative/sufficiency history;
- [ ] no universal representation-superiority language;
- [ ] independent replay of protected results;
- [ ] immediate pre-submission nearest-work refresh and exact artifact binding.

If model/compute escalation consistently erases the accessibility residual at comparable cost, the higher result becomes a crossover/resource law rather than a claim that representation change is intrinsically superior.
