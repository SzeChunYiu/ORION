# EA donor matrix V2 — belief-state saturation reopen

**Date:** 2026-08-23  
**Supersedes for current decision-making:** `EA_DONOR_MATRIX_V1.md` while preserving V1 as chronology.  
**Authority:** research-design input only; not a novelty certificate.

A fresh search after the V1 closure found materially closer work. V1 is therefore preserved as an intermediate saturation snapshot and the fixed-schema belief-learning claim is reopened here.

## 1. Newly load-bearing donors

| Donor | Main object/mechanism | Why it matters to EA | Disposition |
|---|---|---|---|
| **ABBEL — LLM Agents Acting through Belief Bottlenecks Expressed in Language** (arXiv:2512.20111; 2026 update) | `b_t, a_t, o_t -> b_{t+1}` natural-language belief bottleneck; policy acts only through current belief; RL belief grading trains belief quality/compression | Directly owns learned persistent belief update from prior state + action + observation | `CRITICAL PARENT`; strike “train LLMs to update explicit belief state” |
| **Agent-BRACE** (arXiv:2605.11436) | separate belief-state model + policy model, jointly RL-trained; belief is atomic natural-language claims with ordinal certainty/UNKNOWN | Owns structured atomic belief state, uncertainty, belief-policy decoupling and end-to-end task gains | `CRITICAL PARENT`; strike “atomic typed-ish belief state improves long-horizon action” broadly |
| **ReBel — Rewarding Beliefs, Not Actions** (arXiv:2605.20061) | structured belief states + belief-consistency supervision + belief-aware credit assignment | Owns process-level RL directly supervising belief evolution | `MANDATORY BASELINE`; strike belief-consistency training alone |
| **PABU** (arXiv:2602.09138) | progress-aware belief update, selective retention, actions conditioned on retained belief/history | Owns learned selective belief update/retention for efficient agents | `BASELINE`; strike selective retention/progress-aware update |
| **Learning Dynamic Belief Graphs for Theory-of-Mind Reasoning** (arXiv:2603.20170) | dynamic interdependent belief graph, learned time-varying dependencies, LLM semantic projection to graphical-model potentials, ELBO training | Directly owns learned dynamic belief dependencies/graphical updates from language evidence | `CRITICAL GRAPH PARENT`; strike dynamic learned belief graph as novelty |
| **Don't Make the LLM Read the Graph: Make the Graph Think** (arXiv:2604.23057) | explicit belief graph can gate/rank action selection; controlled evidence that integration architecture matters | Shows external structured graph can be causally load-bearing rather than decorative prompt context | `MANDATORY ARCHITECTURE CONTROL`; native-state benefit must beat graph-gated execution |
| **BeliefMem** (arXiv:2605.05583) | probabilistic alternative conclusions retained and updated rather than committing to one deterministic memory | Owns explicit competing hypotheses/probabilities under partial observability | `BASELINE`; strike “preserve multiple uncertain alternatives” |
| **T3 / AREW active-reasoning line** (ICLR/ICML 2026) | joint learning of information seeking and belief tracking; belief deviation/self-locking analyses | Owns coupled active information acquisition + belief-state learning problems | `BASELINE/PARENT`; EA inquiry claim must not repackage this |
| **Align While Search** (CVPR 2026) | external structured belief updated by action-conditioned observations; information-gain action selection | Owns belief-guided exploration with explicit state alignment reward | `BASELINE`; strike generic belief-directed inquiry |
| **ReSSERAct** (2026 preprint) | typed hybrid state with posterior belief plus uncertainty, temporal-validity, replay and control ledgers; shielded admissibility gate; formal non-recoverability results | Very close to EA's idea that belief alone is insufficient and typed extra ledgers can be load-bearing | `CRITICAL STRUCTURAL PARENT`; fixed-schema “belief + staleness/contradiction/admissibility” is not a safe novelty surface |
| **Evidence-Informed LLM Beliefs for Continual Scientific Discovery** (arXiv:2606.29182) | evidence-updated LLM beliefs used to recompute non-stationary scientific surprisal/search reward | Owns evolving evidence-conditioned beliefs in continual scientific discovery | `SCIENCE BASELINE`; strike belief updating for discovery broadly |
| **Belief Engine** (arXiv:2605.15343) | arguments extracted into structured memory; deterministic evidence-weighted stance update with audit trail | Another clear neural-extraction + formal belief-update division of labour | `BASELINE`; reinforces exact-update-first doctrine |
| **Epistemic state updates in LLM agents via public announcement and graded modal logic** (J. Logic & Computation 2026) | observations/tool results/inferences treated as announcements updating explicit knowledge state with consistency-preserving semantics | Directly occupies explicit epistemic-state update language for LLM agents | `FORMAL PARENT`; strike broad “epistemic state updates for LLM agents” |
| **Towards principled knowledge editing methods for LLM reasoning** (Nature Machine Intelligence 2026) | argues knowledge edits must respect interdependence/deductive closure, model beliefs and contextual updates | Makes reasoning-consistent interconnected knowledge editing an explicit current research direction | `CONCEPTUAL PARENT`; no novelty from stating interconnected edits matter |
| **Reason-KE++ / ChainEdit / RAKEL-class reasoning-consistent knowledge editing** | process-faithful or graph/rule-guided propagation of knowledge edits | Owns several neural/internal knowledge-edit ripple mechanisms | `MANDATORY RELATED WORK`; fixed dependency ripple is occupied |
| **Nayebi, What Capable Agents Must Know** (UAI 2026) | selection theorems: strong performance under partial observability can force predictive/belief-like memory | Weakens any broad argument that belief-like internal state itself is the distinctive EA insight | `THEORY PARENT`; EA must test *which extra structure*, not belief-state necessity generally |

All V1 donors remain active parents, especially State Commitment Learning, Grounded Continuation, Kumiho, DGRR, StateMem, Self-Revising Discovery Systems, Model Discovery Agent, Mechanistic World Models, ORION P9/P10/Jump/failure and ORION-Q obligation transport.

## 2. New contraction — fixed-schema belief learning is occupied

The combined current field now already contains:

```text
prior state + observation -> learned posterior belief
structured/atomic belief representation
explicit uncertainty / competing alternatives
belief-policy separation
belief-aware RL objectives
selective retention / progress tracking
dynamic learned belief dependencies
external graph-gated action
staleness / temporal-validity ledgers
explicit epistemic-logic updates
exact/symbolic retraction and rollback
reasoning-consistent knowledge-edit propagation
```

Therefore ORION-EA must not use **Epistemic Autoregression** as a novelty synonym for any fixed-schema recurrent belief updater.

## 3. Consequence of EA-1 exact closure

The repo's own EA-1 result sharpens the literature finding:

1. hiding representation-semantic/failure/obligation-scope coordinates creates exact non-identifiability on the frozen hostile pairs;
2. once the full V0 coordinates and explicit intervention are supplied, the deterministic kernel exactly computes the gold state delta;
3. therefore no learned fixed-schema propagator is justified on that task.

So fixed-schema EA divides into already-owned pieces:

```text
PERCEPTION / BELIEF EXTRACTION  -> strong current learning donors
STATE UPDATE SEMANTICS          -> formal/symbolic donors
DEPENDENCY PROPAGATION          -> exact graph/rollback donors
STALE/UNCERTAINTY LEDGERS       -> current memory/belief donors
```

A novel architecture cannot be manufactured by wiring them together.

## 4. Residual after V2

The only candidate frontier still commensurate with #957's original ambition is **schema/regime evolution**, not state update inside a fixed schema:

> Can a learned system detect that its current epistemic schema/type language is boundedly inadequate, propose a materially new internal primitive/relation/type/representation, compile it into executable semantics, transport/reopen old knowledge and obligations, and predict a protected consequence — beyond donor-complete M-open expansion, program/library learning and self-revising scientific-regime systems?

Even this is heavily parented by:

- ORION Jump/#512;
- Self-Revising Discovery Systems for Science;
- Model Discovery Agent;
- DreamCoder/Stitch/LILO/library and grammar learning;
- causal representation learning / mechanistic world models;
- program synthesis and DSL evolution.

Thus the next study is not permitted to assume novelty. It must begin from a **bounded old-language insufficiency certificate** and a donor-complete representation/program-search baseline.

## 5. What remains useful from fixed-schema EA

The fixed-schema work survives as infrastructure and a bounded scientific finding:

- exact `EpistemicState.v0` evaluator;
- exact information collisions for representation/failure/obligation coordinates;
- exact causal state-surgery kernel;
- quantum transfer cases for access/resource/error/failure obligation revision;
- negative result that exact revision is sufficient once semantics are explicit.

These can serve as a verifier/evaluator for later schema-evolution studies.

## 6. Current V2 disposition

### Fixed-schema architecture claim

`DONOR_SATURATED / NO DISTINCT CONCEPTUAL NOVELTY ESTABLISHED`.

An empirical native-vs-serialized performance study could still be run, but it is not currently justified as the revolutionary core and is not required before moving to schema-evolution research.

### Exact state-information claim

`SUPPORTED WITHIN V0 HOSTILE PAIRS` — representation semantic identity and obligation/failure scope can be load-bearing information.

### Exact update claim

`EA1_DONOR_EXACT_REVISION_SUFFICIENT`.

### Revolutionary candidate

`EAJ_SCHEMA_REGIME_EVOLUTION_OPEN` — requires a new prospective discriminator and separate saturation.
