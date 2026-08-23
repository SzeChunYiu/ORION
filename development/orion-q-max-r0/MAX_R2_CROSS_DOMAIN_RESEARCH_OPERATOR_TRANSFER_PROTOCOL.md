# ORION-Q MAX-R2 cross-domain research-operator transfer protocol

Date: 2026-08-20
Parent: #679
Prerequisite result: `MAX_R1_TYPED_RESEARCH_OPERATOR_ARBITRATION_SUPPORTED__EXACT_SYNTHETIC`
Status: protocol freeze only; no result yet.

## Maximal question

Can ORION transfer **research operators** across quantum domains and outperform a strong general self-evolving scientific-agent baseline when both receive the identical strongest V4 typed/scoped research state, the same specialist tools, the same execution budget and the same verifier access?

This is the first MAX experiment where ORION may not win by exposing additional information.

## Research-operator object

Freeze `QuantumResearchOperator.v1` as a reusable scientific skill, not a quantum gate:

- semantic operator class;
- preconditions over `QuantumResearchState.v1`;
- read coordinates;
- effect on research state;
- required specialist/tool capabilities;
- expected verifier/resource cost;
- applicability boundary;
- known failure receipts;
- `required_same` / `reopen_on_change` constraints;
- transfer provenance;
- authority requirements;
- version/lineage identity.

Candidate operator classes include:

- `VERIFY_CHEAP_THEN_DEEP`;
- `REOPEN_AFTER_REPRESENTATION_CHANGE`;
- `REOPEN_AFTER_ACCESS_CHANGE`;
- `SEARCH_MORE_BEFORE_INVENTION`;
- `SWITCH_SPECIALIST_ON_CERTIFIED_OBSTRUCTION`;
- `CHANGE_REPRESENTATION_WITH_CORRESPONDENCE_CHECK`;
- `CHANGE_INTERFACE_WITH_NO_STRONGER_ORACLE_CHECK`;
- `PROMOTE_REUSABLE_ABSTRACTION_AFTER_TRANSFER`;
- `QUERY_DISCRIMINATING_FACT`;
- `CANNOT_CHECK_AND_PRESERVE_OBLIGATION`.

No domain names or donor names appear in operator semantics.

## Domains

At least four held in one common arena:

D1 synthesis/program design;
D2 algorithm/interface/QSP-QSVT-style design;
D3 QEC code/circuit/decoder co-design;
D4 formal theorem/conjecture reasoning.

Optional D5 parametric algorithm-family design if its exact state mapping passes hostile review.

## Data generation / evidence policy

The first execution may use exact synthetic worlds, but every state transition and skill applicability must correspond to a real research pattern documented in the donor matrix.

A domain-specific carrier may remint names, costs and specialist identities, but the common typed state and operator semantics stay fixed.

## Split

Primary split is **leave-one-domain-out**.

For each fold:
- learn/distill reusable research operators from three domains only;
- freeze the operator library/policy;
- test zero-shot on the fourth domain;
- no target-domain labels, successful trajectories or outcome tuning before evaluation.

Additional holdout:
- remint all tool/specialist/task identities;
- perturb cost scales while preserving order where declared;
- include domain-specific nuisance features unavailable to the common controller.

## Strong baselines

### B0 oracle domain-policy ceiling
Knows the hidden domain/task family and chooses the best precomputed operator. Diagnostic only.

### B1 flat donor portfolio
Selects one specialist/tool based on current state, no learned reusable research skills.

### B2 donor-composed adaptive controller
Receives full V4 state and may sequence all registered donor capabilities using a strong hand-coded/rule/meta-policy.

### B3 general self-evolving scientific agent
Abstracts the strongest structures from S1-NexusAgent/Autogenesis/EvoMaster/AI-Scientist-style systems:
- same V4 state;
- same tool registry;
- reusable skill memory;
- trajectory critique/distillation;
- adaptive tool retrieval;
- slow/fast evaluation;
- versioned skill updates;
- target-domain adaptation forbidden before protected test.

### B4 ORION P9 research-operator controller
Same V4 state/tools/budget as B3, but skills are typed with explicit applicability, scoped negative history, obligation preservation and cross-domain semantic identity.

### B5 ORION P9 + P10
**Disabled in MAX-R2.** Activated only in MAX-R3 if B4 leaves a residual that requires changing the operator/method language.

## Primary hypothesis

`H-MAX-R2`:

> Under leave-one-domain-out evaluation, B4 achieves higher verified task/research success and lower harmful skill reuse than B3 at matched tool/verifier budget, without higher false escalation or authority violations.

This is a transfer/safety hypothesis, not a novelty claim.

## Primary endpoints

Non-compensatory vector:

- verified end-state success;
- zero-shot held-out-domain success;
- harmful transferred-skill rate;
- stale-failure reuse rate;
- unnecessary new-skill creation rate;
- verifier/tool cost;
- time/step count;
- false escalation;
- access/oracle violation;
- correct `CANNOT_CHECK`.

Success cannot be bought by violating a hard authority/access gate.

## Required hostile families

1. **same skill name, different applicability** — surface retrieval must fail;
2. **same failure signature, representation changed** — scoped reopen required;
3. **same representation label, stronger hidden oracle** — `NO_STRONGER_ORACLE` must block;
4. **successful source-domain skill harmful in target domain** — applicability gate must reject;
5. **unseen but valid operator composition** — tests transfer beyond memorized trajectories;
6. **new domain with no applicable skill** — correct action may be search/query/CANNOT_CHECK, not forced reuse;
7. **skill can be repaired by changing a parameter only** — do not invoke P10;
8. **domain-specific nuisance strongly correlated in training folds** — common state should resist shortcut.

## First-right-of-refusal rule

If B3 matches B4 after receiving the same typed applicability/obligation structure, absorb that structure into the general-agent incumbent and close MAX-R2 as `GENERAL_SELF_EVOLVING_AGENT_SUFFICIENT`; then MAX-R3 must target actual method-language expansion.

Do not weaken B3 to manufacture a win.

## Positive terminal

`MAX_R2_CROSS_DOMAIN_RESEARCH_OPERATOR_TRANSFER_SUPPORTED`

Requires:
- positive held-out-domain effect on >=3/4 folds;
- no hard-gate regression;
- effect survives identity remint and nuisance mutations;
- same exact V4 information/tools for B3/B4;
- independent replay.

Other terminals:
- `MAX_R2_GENERAL_SELF_EVOLVING_AGENT_SUFFICIENT`;
- `MAX_R2_DOMAIN_LOCAL_ONLY`;
- `MAX_R2_TRANSFER_HARMFUL`;
- `MAX_R2_INVALID_BASELINE_MATCH`;
- `CANNOT_CHECK`.

## Upward continuation

Regardless of terminal, the MAX programme continues:

- if B4 wins, its operator semantics are absorbed into the incumbent and MAX-R3 attacks method-language expansion;
- if B3 matches, B3 is absorbed and MAX-R3 begins from the stronger general-agent incumbent;
- if both fail, recursively diagnose representation/action-space/evaluator limits before redesign.