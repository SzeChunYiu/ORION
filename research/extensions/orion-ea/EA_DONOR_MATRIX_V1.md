# EA donor matrix V1

**Frozen:** 2026-08-23  
**Purpose:** EA-0A nearest-work saturation before any ORION-EA architecture result.  
**Authority:** literature/research-design input only; not a novelty certificate.

## Decision rule

For each close parent, extract the state object, update mechanism, invalidation semantics, training signal and exact/non-neural component. ORION-EA adopts the strongest parent mechanism and strikes the corresponding novelty phrase. A residual survives only if it has a discriminator not already supplied by the donor-composed incumbent.

## Primary donor matrix

| Donor | State / computation object | Update / training mechanism | Revision / invalidation | What it already owns | EA disposition |
|---|---|---|---|---|---|
| **Coconut** — arXiv:2412.06769 | continuous hidden state recycled as next reasoning input | latent reasoning training rather than linguistic CoT at every step | no ORION-style typed revision contract | reasoning in continuous latent space; branching latent alternatives | `ADOPT/BASELINE`; strike “reasoning need not be tokens” |
| **Thinking States** — arXiv:2602.08332 | recurrent thinking-state embeddings injected during input processing | natural-language supervised thinking tokens mapped back to embedding space | not a general persistent belief-revision system | supervised recurrent latent state and strong state-tracking behavior | `MANDATORY BASELINE`; strike “recurrent internal reasoning state” |
| **SST V2** — arXiv:2605.00206 | nonlinear latent state streamed horizontally at each decoder layer | co-training + parallel recurrence; optional extra latent deliberation | no typed epistemic invalidation | intrinsic continuous state stream and latent deliberation | `MANDATORY BASELINE`; native state cannot mean merely a recurrent latent stream |
| **T²MLR** — arXiv:2607.15178 | cached middle-layer representation from previous token re-enters earlier current layer | localized temporal recurrence; can retrofit a pretrained model | no typed belief revision | persistent abstract latent computation across decoding steps | `MANDATORY BASELINE`; match recurrent depth and parameters |
| **LiveMem** — arXiv:2608.02515 | fixed-capacity intrinsic memory state independent of active context lifetime | memory-oriented post-training + state-aware serving | primarily continuity, not semantic dependency repair | persistent internal state across context turnover | `MANDATORY BASELINE`; strike “intrinsic state continuity” |
| **State Commitment Learning** — arXiv:2606.05201 | visible answer state is the persistent interface; hidden thought is temporary computation | Counterfactual Erasure RL / HSCO; persistent-state sufficiency objective | erases computation and tests future answer sufficiency | training a model to distinguish temporary computation from committed state | `ABSORB`; strike computation-vs-memory boundary as EA novelty. Authors explicitly bound it as not general arbitrary state management. |
| **Kumiho / Graph-Native Cognitive Memory** — arXiv:2603.17244 | versioned property-graph memory with immutable revisions, tag pointers and typed dependencies | external structured memory + retrieval/reranking | formal AGM/Hansson belief-revision semantics | graph-native versioning, formal belief revision, dependency structure | `MANDATORY EXTERNAL BASELINE`; strike formal graph belief revision |
| **Grounded Continuation** — arXiv:2605.14175 | explicit claim/evidence dependency graph plus epistemic/argumentation state | LLM classifies one of eight update operations; symbolic engine applies update | exact graph-walk retraction; formal conflict-free guarantee | neural proposal + exact structural state update/retraction | `CRITICAL PARENT`; strike LLM→symbolic exact revision architecture. Residual cannot be external orchestration alone. |
| **Supersede** — arXiv:2606.27472 | temporal fact/current-state update behavior | diagnosis + training for supersession | updates newer facts over stale ones | training and evaluation of memory supersession | `ADOPT/BASELINE`; strike generic learned supersession |
| **TEPA** — arXiv:2608.07429 | keyed precedents/memories with lifecycle state | revoke stale memory on fresh conflict | explicit revocation while retaining history for audit | memory revocation lifecycle | `ADOPT`; strike revocation as novelty |
| **StateMem / StateMemBench** — arXiv:2608.19652 | state-first memory explicitly tracking supersession and relational dependencies | structured state extraction/wrapper over memory systems | current-state/superseded-state tracking | state-first evolving-world memory and benchmark | `MANDATORY BASELINE`; strike state tracking by supersession/dependency alone |
| **Dependency-Guided Rollback Repair** — arXiv:2608.10502 | typed memory-to-action provenance/dependency graph | post-failure diagnosis, dependency tracing, selective replay | deactivates unsupported state while preserving independently supported benign state | selective descendant invalidation + rollback + benign-state preservation | `CRITICAL PARENT`; strike causal rollback/preservation as a standalone EA claim |
| **FORGE** — arXiv:2605.16233 | reusable textual failure lessons/heuristics from trajectories | failure-driven reflective memory, population selection | no full typed scope/obligation semantics | learning reusable lessons from failed trajectories | `BASELINE`; strike generic failure reflection |
| **Query-Conditioned Trajectory Reuse** — arXiv:2608.12847 | reusable procedure + bindings + applicability/verification conditions | retrieve/adapt prior trajectories under current query | checks reuse applicability under changed context | contextual skill/trajectory reuse | `BASELINE`; strike applicability-aware trajectory reuse |
| **ESAA** — arXiv:2602.23193 | append-only event log + deterministic projected materialized state | LLM emits structured intentions; orchestrator validates/applies effects | replayable deterministic state mutation | event-sourced separation of probabilistic intention from deterministic mutation | `SYSTEMS PARENT`; strike event-sourced proposal/execution split |
| **Self-Revising Discovery Systems for Science** — arXiv:2606.01444 | typed regime/schema; state as copresheaf; provenance category | fixed-regime update vs verified schema/regime transition | old artifacts transported through schema functor/Kan extension and preservation map | representational regime transition, provenance transport, typed accepted/rejected artifacts | `CRITICAL DISCOVERY PARENT`; strike “AI revises its representation while preserving provenance” broadly |
| **Mechanistic World Models** — arXiv:2607.12474 | modular explanatory mechanisms and variables | mechanism-centric modeling, invariance/composition pressure | mechanism shifts/local adaptation rather than ORION authority | reusable explanatory mechanisms for autonomous discovery | `ABSORB`; strike mechanism-centric world model as novelty |
| **Model Discovery Agent** — arXiv:2608.09696 | Bayesian scientific hypothesis/model state | LLM structure proposer + SMC/SBI + value-of-information experiment design | predictive checks trigger M-open model-class expansion | LLM proposer separated from exact/probabilistic scientific identification; M-open expansion | `CRITICAL PARENT`; strike “detect model inadequacy then expand hypothesis class” |
| **Effect-typed / proof-carrying agent systems (ETAS, proof-carrying actions)** — arXiv:2607.17780 / 2606.04104 | typed actions/effects, obligations and certificates | proposal/commit lifecycle plus runtime checking | rejects actions that fail declared proof/effect obligations | typed action contracts and proof-carrying execution | `PL/SAFETY PARENT`; strike typed effects/certificates alone |
| **ORION P9** | typed structural worlds, exact information views, failure history, transport | simple learning first right of refusal; exact inference closes residuals | exact history/filtering and transport computation | load-bearing typed information + exact-first doctrine | `INTERNAL INCUMBENT`; EA cannot relabel P9 structure as new |
| **ORION P10 A0** | fixed candidate responsibility state/controller | donor-composed structured control | exact finite equivalence to incumbent | observe/repair/reframe/unresolved control over fixed proposals | `CLOSED INTERNAL NEGATIVE`; do not rescue with LLM wrapper |
| **ORION Jump / J3** | epistemic regime and candidate new primitive/representation | bounded old-language insufficiency + representational proposal | preservation/correspondence and protected consequence | the research question of bounded scientific regime/concept invention | `UPSTREAM OWNER`; EA-5 is a neural instantiation/test, not ownership of Jump itself |
| **ORION failure epistemology** | scoped negative knowledge with compatibility and reopen conditions | failure-to-constraint/reopen semantics | stale negative knowledge can reopen on material regime change | structured negative knowledge | `UPSTREAM OWNER`; EA learns/proposes over this object, not redefines it |
| **ORION-Q obligation transport / protected skill admission** | joint semantic/access/error/resource/failure/authority bundles | verified transport and protected persistent-skill admission | reopen/quarantine/rollback under changed obligations | scientific-admissibility transport across representation/skill changes | `QUANTUM GOLD/STRESS TEST`; not EA novelty by itself |

## Material contractions

### C1 — native latent state is occupied

Thinking States, SST V2, T²MLR and LiveMem make it untenable to describe “persistent state inside/alongside a Transformer” as the EA novelty. Any EA native-state arm must be compared against these families under matched serial compute, state capacity and post-training data.

### C2 — computation/state commitment is occupied

State Commitment Learning directly trains a future-facing boundary between discardable hidden computation and persistent answer state. EA therefore may not claim that distinction or counterfactual erasure as its novelty. The paper's own stated limitation — a restricted state-management setting rather than arbitrary memory/state management — defines a legitimate pressure point, not a novelty certificate.

### C3 — exact dependency retraction and rollback are occupied

Grounded Continuation supplies the LLM-update-proposal + symbolic exact dependency engine pattern; DGRR supplies typed provenance, descendant tracing, benign-state preservation and selective replay. Kumiho supplies formal belief-revision semantics. EA's causal-surgery study must therefore ask whether **learning typed deltas** improves proposal/extraction and transfer; the exact kernel itself is an adopted baseline.

### C4 — state-first stale-memory handling is occupied

Supersede, TEPA and StateMem independently cover supersession, revocation and state-first relational tracking. EA cannot claim “agents should update stale memory”. Scoped failure semantics must be tested specifically where ordinary supersession is insufficient: compatibility, negative transfer, representation remint vs semantic change, and obligation reopening.

### C5 — regime revision/provenance transport is occupied

Self-Revising Discovery Systems already formalizes discovery as verified representational regime transition with preservation/transport of old artifacts. MDA covers M-open model-class expansion. EA-5 may only claim a new result if a **learned model** earns bounded generation/selection value over donor-complete regime-revision/search parents on a prospectively protected discriminator.

## Donor-composed incumbent for EA-1

The strongest first-study incumbent is not a single paper. It is functionally:

```text
recurrent / intrinsic state capacity
+ state-commitment training
+ state-first/versioned structured memory
+ exact dependency/truth-maintenance kernel
+ dependency-guided rollback and selective replay
+ explicit stale-state revocation
+ matched LLM proposal/extraction
```

The ORION-EA candidate may add only what is not already present in that composition.

## Residual that survives this matrix

The narrow candidate residual is:

1. **Training target:** predict arbitrary typed `EpistemicDelta` operations, rather than only answer-state commitment or textual memory writes.
2. **Semantic contract:** deltas are over claims/evidence/dependencies/failures/unknowns/representations/obligations with explicit admissibility semantics.
3. **Execution split:** exact revision kernel executes deterministic consequences; the learned model is scored on proposal fidelity, not credited for the kernel's correctness.
4. **Causal evaluation:** evaluator intervenes directly on epistemic coordinates and scores minimal changed state plus preservation of unaffected state.
5. **Failure/representation interaction:** scoped negative knowledge must reopen on material semantic changes but survive notation-only remints.
6. **Obligation interaction:** representation changes must preserve, transport or explicitly reopen load-bearing obligations rather than merely update facts.
7. **Architecture question remains empirical:** native typed state must beat or otherwise distinguish itself from same-information token serialization, recurrent latent state and external exact workspace under matched resources. If it does not, the native-architecture claim is struck.

## Claims explicitly forbidden after EA-0A

Without a new result, do **not** claim:

- first persistent-state LLM;
- first model that distinguishes computation from memory;
- first belief-revising agent memory;
- first dependency-aware retraction system;
- first stale-memory revocation method;
- first state-first long-horizon memory;
- first selective rollback repair;
- first neural+symbolic exact state controller;
- first self-revising scientific representation;
- first M-open scientific model expansion;
- first proof-carrying agent action system;
- first mechanism-centric scientific AI;
- better LLM reasoning from ORION-EA.

## EA-0A disposition

`EA0A_DONOR_SATURATION_BOUNDED_RESIDUAL_SURVIVES`

The residual is high-risk and must next survive the frozen EA-1A exact discriminator. Two changed-vocabulary saturation rounds are recorded in `EA_SATURATION_CLOSURE_V1.md`.
