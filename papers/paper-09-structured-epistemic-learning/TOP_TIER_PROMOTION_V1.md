# P9 top-tier promotion V1 — Representation Accessibility as a Scaling Coordinate

**Programme:** #977  
**Existing controlled authority:** `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR` remains valid for its bounded package.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Learning and reasoning scale along at least three separable coordinates: semantic information, representation accessibility and downstream computation.** Increasing model or inference resources is scientifically uninterpretable until these coordinates are disentangled. P9 provides a protected diagnostic methodology and seeks reproducible crossover laws among representation repair, explicit inference and model/compute escalation on real systems.

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

## Post-outcome status — 2026-08-23

Two protected studies now constrain the higher claim in opposite but compatible directions.

### Real-data same-information intervention — supported, bounded

`P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED` executed a prospectively frozen, bijective representation intervention on breast-cancer, wine and handwritten-digit data. The cubic representation preserves semantic information exactly; deterministic inverse repair reconstructs native features to floating-point roundoff. Under the frozen linear access class, the native-to-cubic accuracy gap is `0.0351808725` on breast cancer and `0.0239275766` on digits, while wine is a null/negative cell (`-0.0001587302`). Inverse repair restores the native linear mean exactly on the two preregistered positive datasets. The 180-row study is byte-replay deterministic.

**Earned claim:** accessibility can change under an information-preserving representation intervention for a fixed access mechanism, and explicit representation repair can recover that accessibility. The wine cell forbids a universal-dataset statement.

### Protected Qwen2.5 model-size/inference sweep — negative

The immutable Qwen2.5 Q4_K_M 0.5B/1.5B/3B outputs originally generated on PR #618 were recovered without rerunning inference or changing any scientific threshold. The frozen analyzer deterministically returns `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`.

At primary budget 32, `R2_TYPED_STATE - R1_SAME_INFO` is `-0.140625` for 0.5B and `0.0` for both 1.5B and 3B. The positive-delta-every-size gate fails, the largest-model domain-block bootstrap lower bound is not above zero, no smaller-structured substitution is observed, and the aggregate hostile-control gate fails; ORDER is negative at both 0.5B and 3B.

**Required claim subtraction:** P9 must not state or imply a universal monotone law in which larger LLM capacity reveals a stable typed-state accessibility advantage. The higher result is access-class- and system-conditional unless stronger protected evidence later establishes a transferable crossover law.

The exact execution receipts and artifact identities are bound in `papers/candidates/TOP_TIER_EXECUTION_LEDGER_2026-08-23.md`.

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

- [x] bounded same-information real-system/access-mechanism scaling surfaces executed, including an authoritative negative Qwen surface;
- [x] prospectively frozen one-coordinate causal accessibility intervention with deterministic inverse repair;
- [ ] diagnosis accuracy significantly above generic uncertainty/failure heuristics;
- [ ] at least two qualitatively distinct protected diagnostic domains;
- [ ] matched full model/inference/representation resource accounting;
- [x] protected model-size and inference-budget comparators executed; their Qwen result is negative and retained;
- [x] exact preservation of the bounded P9 negative/sufficiency history;
- [x] no universal representation-superiority language;
- [ ] independent replay/authority beyond same-workflow deterministic byte replay;
- [ ] immediate pre-submission nearest-work refresh and exact artifact binding.

The unchecked items are genuine remaining promotion requirements. A positive result on the real-data intervention does not erase the Qwen null/negative surface, and the Qwen negative does not erase the real-data causal accessibility result.

If model/compute escalation consistently erases the accessibility residual at comparable cost in a later protected setting, the higher result becomes a crossover/resource law rather than a claim that representation change is intrinsically superior. If that transfer fails, the paper must retain the system-conditional law.
