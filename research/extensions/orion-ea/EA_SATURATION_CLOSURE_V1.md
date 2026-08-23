# EA-0A donor saturation closure V1

**Date:** 2026-08-23  
**Issue:** #957  
**Scientific scope:** nearest-work / research-design closure only.  
**Terminal:** `EA0A_DONOR_SATURATION_BOUNDED_RESIDUAL_SURVIVES`.

This document closes the first ORION-EA study: determine whether the broad idea “learn a persistent epistemic state rather than only next-token continuation” still contains a research residual after current 2026 donor pressure.

It does. The residual is substantially narrower than the opening issue.

## 1. Question frozen before literature outcome

EA-0A asked seven questions:

1. What already exists for native persistent/recurrent reasoning state?
2. What already exists for causal belief revision / dependency retraction?
3. What already exists for scoped stale/failure memory?
4. Which systems already combine neural proposals with exact state-transition kernels?
5. Is state commitment itself already a training objective?
6. Which systems already change the reasoning/scientific representation while preserving provenance?
7. After composing all of them, what discriminator is left for ORION-EA?

The intended broad claim was not protected. Any donor could contract or eliminate it.

## 2. Round A — neural-state / latent-reasoning vocabulary

Search vocabulary centered on:

- latent reasoning;
- recurrent reasoning state;
- hidden state persistence;
- thinking states;
- state stream;
- temporal recurrence;
- intrinsic memory state;
- computation vs memory.

### Material findings

This round found multiple direct parents:

- `Coconut` — continuous latent reasoning;
- `Latent Reasoning with Supervised Thinking States` — supervised recurrent reasoning state with strong state tracking;
- `State Stream Transformer V2` — persistent nonlinear state stream across decoder positions;
- `T²MLR` — temporal middle-layer recurrence;
- `LiveMem` — intrinsic memory-state continuity independent of active context;
- `State Commitment Learning` — direct training objective for deciding what hidden computation may be discarded and what must be committed as future-reliable state.

### Claim contractions

The following candidate novelty phrases were removed:

- “LLMs need a persistent internal reasoning state”;
- “reasoning should not be forced entirely through token space”;
- “a model should separate temporary computation from persistent state”;
- “a long-running LLM should carry intrinsic state beyond active context”.

### Residual after Round A

A possible residual remained around **typed arbitrary state deltas and explicit revision semantics**, because the strongest direct state-commitment paper explicitly bounds itself to an answer/hidden-thought interface rather than arbitrary memory/state management. This was only a search lead, not a novelty conclusion.

## 3. Round B — belief-revision / memory-repair vocabulary

Changed vocabulary centered on:

- belief revision;
- truth maintenance;
- dependency retraction;
- supersession;
- stale memory;
- revocation;
- rollback repair;
- evolving world state;
- relational memory dependencies.

### Material findings

This round changed the research object again:

- `Kumiho / Graph-Native Cognitive Memory` provides versioned graph memory with formal AGM/Hansson belief-revision semantics.
- `Grounded Continuation` already uses an LLM as an update interpreter and an exact symbolic dependency engine for selective retraction.
- `Supersede` directly diagnoses and trains the memory-update gap.
- `TEPA` supplies explicit stale-memory revocation.
- `StateMem / StateMemBench` treats evolving state, supersession and relational dependencies as the central memory problem.
- `Dependency-Guided Rollback Repair` traces typed provenance/dependencies, deactivates unsupported descendants, preserves independently supported benign state and selectively replays affected computation.

### Claim contractions

The following were removed:

- “first LLM/agent with dependency-aware belief retraction”;
- “first selective belief surgery preserving unaffected memory”;
- “first state-first memory for superseding facts”;
- “first stale-memory revocation lifecycle”;
- “first LLM proposal + exact symbolic revision engine”.

### Residual after Round B

The candidate residual changed from “belief surgery” in the broad sense to:

> **learn the typed delta proposal itself under counterfactual state interventions, while keeping exact revision consequences outside the neural claim.**

The exact engine is now a mandatory donor, not an ORION contribution.

## 4. Round C — event-sourcing / versioned-state / software-state vocabulary

A second changed-discipline round searched:

- event sourcing;
- versioned memory;
- transactional state;
- state continuity;
- deterministic mutation;
- replayable agent state;
- agent intentions vs materialized state.

### Material findings

- `ESAA` explicitly separates probabilistic cognitive intention from deterministic state mutation using append-only event sourcing and materialized views.
- `LiveMem` again appears as a native state-continuity parent.
- `Kumiho` again appears through versioned graph state.
- `Dependency-Guided Rollback Repair` again appears through rollback/repair language.

### Effect on residual

**No material new EA coordinate was added.** This round reinforces that intention/proposal vs deterministic mutation, versioning and replay are donor-owned. It does not eliminate the narrower typed-delta-learning discriminator.

Round C terminal: `NO_MATERIAL_RESIDUAL_CHANGE`.

## 5. Round D — discovery/regime-change vocabulary

A final orthogonal sweep asked whether the long-horizon “self-expanding language” idea was already occupied under scientific-discovery language:

- self-revising discovery;
- representational regime transition;
- M-open model discovery;
- mechanism-centric world models;
- provenance transport;
- schema transition;
- proof-carrying action/effect systems.

### Material findings

- `Self-Revising Discovery Systems for Science` explicitly defines discovery as a verified transition between typed representational regimes and transports old artifacts/provenance into the new schema.
- `Model Discovery Agent` already combines LLM structural proposal, Bayesian identification, value-of-information experiment design and M-open model-class expansion.
- `Mechanistic World Models` occupies broad mechanism-centric autonomous-discovery language.
- effect-typed/proof-carrying agent systems occupy typed action/effect/certificate language.

### Claim contractions

EA-5 cannot claim:

- representation revision itself;
- provenance-preserving regime transition itself;
- M-open hypothesis-space expansion itself;
- mechanism-centric discovery itself;
- typed/proof-carrying agent action itself.

EA-5 survives only as a **future learned-model incremental-value experiment** over those donor-complete parents.

Round D terminal: `NO_NEW_EA_PRIMITIVE__LONG_HORIZON_CLAIM_CONTRACTED`.

## 6. Saturation criterion

Two consecutive changed-vocabulary rounds after the last major residual contraction — event-sourced/versioned-state and discovery/regime-transition — added strong baseline/ownership pressure but did not change the minimal EA-1 experimental object:

```text
CURRENT EPISTEMIC STATE
        + NEW OBSERVATION / INTERVENTION
        -> LEARNED TYPED DELTA PROPOSAL
        -> EXACT ADMISSION / REVISION KERNEL
        -> NEW EPISTEMIC STATE
```

with state-level causal scoring and same-information architecture controls.

This satisfies the programme's bounded saturation rule for **freezing the next discriminator**. It does not establish novelty or positive value.

## 7. Final EA-0A residual

The residual is the conjunction below:

### R1 — arbitrary typed delta as a learned object

Train/evaluate a model on state changes such as:

- retract evidence;
- preserve an independently supported claim;
- reopen a stale failure;
- mark a dependent conclusion unknown;
- transport or reopen an obligation;
- change a representation identity/semantics;
- propose only the minimal change set.

This is broader than answer-state commitment and narrower than arbitrary self-modification.

### R2 — exact kernel is an adopted referee

A symbolic/typed kernel computes deterministic consequences. EA receives no scientific credit for exact graph propagation that Grounded Continuation, DGRR, truth-maintenance systems or ORION already know how to perform.

The learnable question is proposal/extraction/generalization under protected interventions.

### R3 — counterfactual causal state evaluation

The evaluator changes exactly one registered epistemic coordinate and scores:

- which nodes must change;
- which nodes must remain unchanged;
- which failures become stale/reopen;
- which obligations become unresolved/transported;
- whether the final action follows the repaired state.

Final-answer accuracy is insufficient.

### R4 — same-information architecture discriminator

A native-state architecture is allowed to claim value only if it adds something beyond:

- equivalent typed state serialized into tokens;
- recurrent/continuous latent state;
- intrinsic memory state;
- external versioned/graph memory;
- exact donor-composed revision systems;

under matched information and explicit resource accounting.

If serialization/external state matches, the architecture claim terminates negatively while the dataset/protocol may remain useful.

### R5 — ORION-specific interaction that still needs testing

The first benchmark includes **scoped negative knowledge + representation semantics + obligations** because those interactions are central ORION research objects and are not discharged merely by ordinary fact supersession or descendant deletion.

A stale failure should reopen on a material semantic regime change but **not** on an identity/notation remint. A representation edit that changes what an old certificate means should reopen the dependent obligation instead of silently transporting it.

This exact interaction is the first place EA may earn a bounded residual beyond current memory-revision parents.

## 8. Scientific terminal

`EA0A_DONOR_SATURATION_BOUNDED_RESIDUAL_SURVIVES`

What is finished:

- nearest-work decomposition;
- strong-parent absorption;
- broad-claim contraction;
- two changed-vocabulary no-material-change rounds;
- donor-composed incumbent definition;
- next exact discriminator selection.

What is **not** finished by literature analysis:

- EA-1 empirical/model result;
- native-state vs serialization result;
- cross-domain architecture result;
- self-expanding-language result;
- any LLM or quantum performance claim.

Those require execution. The next study is frozen in `EA1_CAUSAL_BELIEF_SURGERY_PROTOCOL_V1.md`.
