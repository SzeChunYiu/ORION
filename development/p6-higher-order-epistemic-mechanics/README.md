# P6 successor — higher-order epistemic mechanics, tranche 1

## Development question

Can ORION express the narrow principle **“a scientific anomaly does not itself license a broad epistemic rewrite”** as a small, non-authorizing mathematical mechanic, without prematurely freezing the provisional RLC/MDA-derived taxonomy of evidence/model/frame/objective/method failures?

The first implementation target is deliberately smaller than #463. It asks only whether claim-relative candidate revisions can be represented by typed read/write footprints, hard obligations, preservation obligations, authority requirements and cost, and whether the system can return the **minimal admissible revisions** or explicitly remain unresolved.

## Atomic development fibres

1. Represent a higher-order mechanic without hard-coding the provisional revision-class taxonomy.
2. Fail closed on violated, unknown or missing preconditions / hard evidence obligations.
3. Keep authority separate from confidence, utility and cost.
4. Define a claim-relative invasiveness preorder using material write scope, preservation obligations and authority scope.
5. Select minimal admissible mechanics without using cost as permission to make a broader rewrite.
6. Preserve **multiple incomparable minima** as `UNRESOLVED` rather than choosing by arbitrary tie-break.
7. Preserve a narrower unresolved candidate as a blocker on promotion of a broader admissible revision.
8. Bind every record by canonical content digest and make it explicitly non-self-authorizing.
9. Add countermodels before any Self-ORION integration.
10. Document the successor theory without altering the frozen P6 V2.1 peer-review package.

## Incumbent ORION mechanics and negative history

This tranche builds on, and must not duplicate:

- P6 V2.1 typed mechanic/state objects, read/write ownership, hard obligations, `CANNOT_CHECK`, non-escalation and dependency-scoped reopening (#333);
- claim-relative structural reduction, `MethodFibre.v1`, conditional composition and representation lift (#417/#419);
- P8/P4 non-compensatory authority semantics;
- P1's current bounded mutation-necessity result, which already demonstrates that lower-level exclusion / protected-invariant checks matter on its frozen mechanical family;
- #452/#454/#457/#458/#459/#462 research, which is **not yet saturated enough to freeze a universal revision taxonomy**.

Relevant negative lessons are retained:

- a broad failure label can be shortcut-predictable or instrumentally non-discriminating;
- a null on an axis with no headroom is not evidence of equivalence;
- confidence and utility are not permission;
- adding a richer representation/architecture can masquerade as an algorithmic mechanism effect;
- uncertainty can justify containment rather than revision;
- multiple reports/processes can be epistemically dependent despite distinct identities.

## Same-domain and parent-domain knowledge considered

The implementation hypothesis is pressure-tested against the structural families already routed through #452/#454/#457:

- belief revision / truth-maintenance / effect systems;
- POMDP and sufficient-state / abstraction theory;
- Bayesian model criticism and M-open model expansion;
- rational metareasoning / value of computation;
- constrained/safe control and uncertainty containment;
- dynamic epistemic / social-learning / mechanism-design formalisms;
- scientific-agent revision, objective evolution and world-model evolution.

This tranche claims none of those ingredients as novel. It implements only a generic ORION-facing contract needed to test whether a useful cross-coordinate residual exists.

## Bounded saturation assessment

For tranche 1, the following structure is stable across the incumbent P6/P8 contracts and the new research programme:

- mechanics inspect some state and may write only declared coordinates;
- material transitions have preconditions and hard obligations;
- some coordinates/invariants must be preserved;
- some transitions require external authority;
- several candidate transitions can remain live at once;
- missing evidence must remain unresolved rather than becoming broad permission;
- claim-relative locality matters.

The following is **not** saturated and therefore is intentionally excluded from the implementation:

- a universal list of epistemic coordinates;
- a universal ordering among evidence, measurement, model, representation, objective and method revision;
- a universal scalar value function for scientific computation;
- a universal social-belief representation;
- a claim that minimal epistemic change is always globally optimal.

## Challenge to the saturation basis

The apparent common structure could still be misleading because:

1. revision classes may only admit a local/claim-relative preorder, not one global order;
2. write-footprint inclusion alone may be semantically insufficient;
3. preserving more obligations can conflict with feasibility or authority;
4. two incomparable revisions may both be scientifically legitimate;
5. a narrower revision can be unresolved while a broader one is supported, making “always choose narrowest” unsafe unless unresolved alternatives are retained;
6. standard belief-revision or effect-system formalisms may already subsume the final abstraction.

The implementation therefore exposes a **bounded partial preorder and explicit unresolved selection**, not a total ordering or universal optimality theorem.

## Why prior searches could have been falsely flat

- papers use different vocabulary for minimal change, locality, admissibility and conservative update;
- metareasoning literature may frame the same structure as computation selection rather than epistemic revision;
- program/effect systems may encode the key property as write effects, not philosophy of science;
- decision theory can hide hard scientific obligations inside feasibility constraints;
- social epistemology can break naive independence assumptions that are invisible in single-agent mechanics.

These are reopen routes, not reasons to delay the generic contract.

## Competing implementation hypotheses

### H-I1 — useful small common calculus
A typed mechanic plus a claim-relative invasiveness preorder is enough to express the key countermodels without freezing the full taxonomy.

### H-I2 — write-footprint order is vacuous
If all meaningful comparisons require domain-specific semantics, the generic preorder adds no value and should be narrowed to explicit pairwise witnesses.

### H-I3 — existing P6 `CompositionContract` is already sufficient
If the new tests can be encoded cleanly as ordinary P6 composition/authority checks, this tranche should be deleted or reduced to documentation.

### H-I4 — minimality is unsafe under unresolved alternatives
If a broader admissible revision would be selected while a potentially narrower candidate is unresolved, the correct terminal must remain unresolved. The implementation must exhibit this case.

## Frozen implementation hypothesis

Implement **`HigherOrderEpistemicMechanic.v1`** as a content-bound, non-authorizing record with:

- claim id;
- mechanic id;
- read/write coordinate sets;
- preconditions;
- hard requirements;
- preservation obligations;
- required authority domains;
- non-negative declared cost;
- optional descriptive kind only (no authority semantics).

Implement:

1. an `ObligationState` (`SATISFIED / VIOLATED / UNRESOLVED`);
2. fail-closed mechanic assessment;
3. `less_or_equal_invasiveness(left, right)` for one claim using:
   - `Write(left) ⊆ Write(right)`;
   - `Pres(left) ⊇ Pres(right)`;
   - `Authority(left) ⊆ Authority(right)`;
4. strict comparison requiring at least one strict component;
5. minimal-admissible selection;
6. a selection guard: if an unresolved mechanic is strictly less invasive than an admissible minimum, return `UNRESOLVED` rather than promoting the broader mechanic;
7. no cost-based authority or self-authorization.

This is a **design axiom / experimental formal contract**, not a universal theorem of rational agency.

## RED / hostile tests to write before implementation

- narrower evidence-style write dominates broader model-style write when both are admissible;
- incomparable minimal revisions return multiple minima / unresolved selection;
- narrower unresolved candidate blocks promotion of broader admissible candidate;
- violated hard requirement blocks;
- unknown hard requirement remains unresolved;
- missing authority blocks despite low cost / otherwise satisfied obligations;
- protected/forbidden write blocks;
- cost cannot make a broader mechanic less invasive;
- cross-claim mechanics cannot be ordered;
- digest tampering is rejected;
- self-authorizing record construction is rejected;
- clean no-alarm case reaches unique minimum.

## Reopen triggers

Reopen the implementation hypothesis if:

- #452 saturation rejects minimal/local revision as a useful organizing principle;
- #454 finds a stronger formal donor that directly subsumes this contract;
- #463 shows the preorder requires semantic witnesses rather than set-based necessary conditions;
- a hostile countermodel shows the selector can authorize a broader transition from missing evidence;
- #455 empirical work shows the abstraction adds no discrimination value;
- P6/P8 authority semantics change incompatibly;
- an overlapping active PR introduces the same object under another owner.

## Nonclaims

This tranche does **not** establish:

- a final epistemic-state tuple;
- a final revision taxonomy;
- optimality of minimal revision;
- general scientific self-revision capability;
- MDA/POMDP/belief-revision novelty;
- peer-review readiness of a new paper;
- Self-ORION adoption authority.

The only intended terminal is a small executable formal substrate suitable for further falsification.