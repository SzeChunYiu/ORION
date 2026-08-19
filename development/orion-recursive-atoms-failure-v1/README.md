# ORION recursive atoms + failure epistemology — implementation packet V1

**Base subject:** `d73e65c10f4f3b7ae773cea667f6dccd1507e8f0`  
**Issues:** #500, #506, #507, #508, #509, #510, #511, #512.  
**Authority:** formal/research substrate only. No object in this tranche can authorize a Jump, scientific claim, paper promotion, or Self-ORION adoption.

## 1. Research conclusion before code

The new programme should not implement a monolithic `JUMP()` operation. The literature already decomposes several pieces that ORION must **absorb rather than rename**:

- Aguilar & Aguirre, *How are Scientific Concepts Birthed?* (arXiv:2509.10740): concept formation in theoretical physics is formalized using type theory; distinction, property preservation, and concept change become compositional typing rules, with one historical path reconstructed as typed program synthesis. **Consequence:** typed concept-transformation witnesses and contexts are donor-owned substrate; ORION novelty cannot be “concept formation can be formalized.”
- Farmer, *Abduction Without a Body?* (arXiv:2608.02505): an Abduction Loop uses representation generation, motif extraction, convention-space canonicalization, cross-domain retrieval, identity-hypothesis generation, adversarial verification, and abstention. **Consequence:** cross-domain correspondence is a strong parent for analogy/identity-abduction studies and does not require physical embodiment in every case.
- Shen, Druckmann & Zou, *Unlocking LLM Creativity in Science through Analogical Reasoning* (arXiv:2605.11258): cross-domain relational analogy expands/diversifies solution generation and can produce useful biomedical proposals. **Consequence:** analogy is a mandatory baseline/donor for concept generation; it is not an ORION invention.
- Duraisamy, *Active Inference AI Systems for Scientific Discovery* (arXiv:2506.21329): explicitly separates exploratory thinking in counterfactual/imaginary spaces from deterministic validation and argues for manipulable abstractions, simulation, causal structure, memory, and empirical grounding. **Consequence:** assumption relaxation / imaginary-space exploration is a serious donor for thought-experiment mechanics, but the perspective does not itself establish a bounded Jump discriminator.
- Wang & Buehler, *Self-Revising Discovery Systems for Science* (arXiv:2606.01444): discovery is a verified representational-regime transition with provenance-preserving transport. **Consequence:** regime transition and preservation are direct prior art; #500 must earn a narrower generation/necessity result.
- Ota, Osa & Harada, *Self-Supervised Theorem Discovery in a Formal Axiomatic System* (arXiv:2606.28747): useful theorem discovery can emerge from proof search and lemma-library growth without regime change. **Consequence:** theorem discovery is an explicit `SEARCH_DISCOVERY / NO_JUMP` control; discovery is not synonymous with Jump.
- Sun et al., *Learning from Failure* (arXiv:2606.31270): failed trajectories can be diagnosed and converted into inference-time improvements. Trehan & Chopra (arXiv:2601.03315) document recurring autonomous-research failure modes. **Consequence:** failure-driven improvement is donor-owned; ORION's residual, if any, is scoped negative knowledge with applicability/reopen semantics rather than “learn from failures.”
- Existing ORION already owns/adopts model criticism, revision responsibility, selective negative history, evidence/authority separation, representation transport, and bounded higher-order revision mechanics. New code must compose with these rather than duplicate them.

## 2. Stable implementation residual

This tranche may safely implement five generic records before the atom studies execute:

1. **Bounded reachability witnesses** — represent `REACHABLE / UNREACHABLE / UNRESOLVED` under an explicit regime, contract, evaluator, and resource bound. They do not prove their own correctness.
2. **Bounded atom-study protocol** — a content-bound study record with positive cases, no-atom controls, matched parents, decomposition hypotheses, interaction hypotheses, recursion stop rules, and independent evaluator identity.
3. **Scoped failure knowledge** — a failure record states what conditions are excluded, which alternatives remain live, which context coordinates must match, and which coordinate changes reopen the failed route. A failure cannot globally ban a method/theory.
4. **Epistemic tension candidates/reports** — generic string-typed tensions with support/defeater/discriminator witnesses. Do not freeze a universal tension taxonomy.
5. **Thought-experiment and concept proposal records** — proposal-side typed artifacts only. Thought experiments must separate relaxed vs held-fixed assumptions and register expected outcomes; concept candidates must expose transformation trace, formal/typed semantics lineage, correspondence, unlocked-contract claims, and protected consequence requests.

The implementation deliberately does **not**:

- claim a complete operator basis;
- implement a scientific creativity model;
- hard-code Einstein/Maxwell/etc. discovery content;
- decide historical cognitive causation;
- compute universal `Reach_B` from arbitrary science;
- treat a concept proposal as valid/novel/useful;
- wire any proposal to P4/P8/P5 authority;
- change frozen P1/P3/P4/P6/P7/P8 paper claims;
- promote P5 H1-H4 or close #455/#500/#507/#508.

## 3. Bounded-reachability formal substrate

A resource bound is a canonical map of named non-negative resources. A reachability witness is claim/contract-relative:

```text
ReachabilityWitness.v1 = (
  regime_id,
  contract_id,
  resource_bound,
  status,
  witness_ids,
  evaluator_id,
  protected
)
```

The framework may mechanically compare *paired witness records* but cannot manufacture an impossibility proof. `UNREACHABLE` is therefore only as authoritative as its external evaluator/witness lineage.

For an atom study, the implementation can compute a non-authorizing delta classification such as:

```text
OLD_UNREACHABLE_NEW_REACHABLE
OLD_UNRESOLVED_NEW_REACHABLE
NO_REACHABILITY_EXPANSION
UNRESOLVED
```

It must retain both witness digests.

## 4. Recursive study contract

`BoundedEpistemicAtomStudy.v1` is a protocol object, not a result. It binds:

- atom identity and parent decomposition path;
- structure/regime version;
- target contract family;
- named resource bounds;
- positive case IDs;
- no-atom control IDs;
- parent/baseline IDs;
- ablation/replacement IDs;
- decomposition and interaction hypotheses;
- stop rules;
- evaluator/verifier identity;
- protected-data boundary;
- authority owner;
- `outcome_accessed=false` at construction.

The first implementation will also provide set-level interaction analysis on already externally evaluated reachable-contract sets. This is **not** claimed as a new factorial/interaction theory; it is bookkeeping for #507.

## 5. Failure knowledge semantics

`FailureKnowledge.v1` must preserve this distinction:

```text
FAILURE EVENT != SCOPED NEGATIVE KNOWLEDGE
```

A record binds:

- failed target/trace;
- regime/context at failure time;
- responsibility state identity;
- excluded conditions;
- still-live alternatives;
- preserved successes;
- exact context coordinates required for reuse;
- exact context coordinates whose change reopens the route;
- evidence and authority owner.

Applicability is fail-closed:

- missing required context -> `UNRESOLVED`;
- incompatible required-same coordinate -> `NOT_APPLICABLE`;
- a declared reopen coordinate changed -> `REOPENED` and no exclusions are applied;
- only compatible records return the scoped exclusions.

This prevents permanent negative transfer after a representation/objective/interface change.

## 6. Tension / thought experiment / concept boundaries

### Tension

A tension candidate is a hypothesis that a declared contract/opportunity is structurally load-bearing. Support and defeaters are explicit evidence IDs. Multiple surviving tensions remain plural; missing evidence remains unresolved. `empirical_residual_present=false` is allowed and retained as metadata rather than treated as a contradiction.

### Thought experiment

A thought experiment is a registered discrimination proposal:

```text
ThoughtExperiment.v1 = (
  tension,
  operation_kind,
  relaxed_assumptions,
  held_fixed_assumptions,
  setup,
  hypothesis -> expected outcomes,
  execution_mode,
  cost,
  safety_constraints
)
```

The framework may compute whether registered predictions separate hypothesis pairs. It does not claim those predictions are correct.

### Concept candidate

A concept candidate must be more than prose:

- typed/structural transformation steps;
- new primitive/relation declarations;
- semantic/type judgment IDs;
- correspondence/reconstruction map;
- executable artifact identity when available;
- claimed unlocked contract IDs;
- protected novel-consequence requests;
- lineage to donor/experience/tension records.

It remains `PROPOSAL_ONLY` until external proof/experiment/verification.

## 7. RED-first hostile requirements

Before implementation, tests must require at least:

1. negative resource bounds reject;
2. reachability witnesses are content-addressed and evaluator-bound;
3. atom-study protocol cannot be constructed after `outcome_accessed=true`;
4. positive and no-atom case sets cannot overlap;
5. duplicate/empty evaluator/authority identities reject;
6. reachability delta never converts old `UNRESOLVED` into an impossibility claim;
7. failure exclusions are returned only under compatible context;
8. changed reopen coordinate returns `REOPENED` and applies no exclusions;
9. missing context remains `UNRESOLVED` rather than silently applying a failure;
10. tension report can represent zero empirical residual + material structural tension;
11. multiple live tensions remain plural;
12. thought experiment cannot relax and hold fixed the same assumption;
13. non-discriminating thought experiment is detectable from registered predictions;
14. concept candidate requires structural/typed semantics and correspondence, not prose only;
15. concept proposal cannot self-authorize validity/novelty/adoption;
16. all records have deterministic digest verification under input reordering;
17. no object writes current P4/P8/P5 authority state.

## 8. Paper policy

Allowed after this tranche if CI is green:

- additive successor note under `research/extensions/`;
- P9/P10/JUMP programme handoff describing new protocol objects as **unvalidated research infrastructure**.

Forbidden:

- editing frozen P6/P7/P8 candidate manuscripts while saturation PRs #503-#505 are active;
- broadening P1's bounded mutation-necessity result;
- claiming P5 scientific self-improvement value;
- calling #500/#507/#508 scientifically supported.

## 9. Tranche terminal

Implementation-only terminal:

`RECURSIVE_ATOM_FAILURE_FORMAL_SUBSTRATE_IMPLEMENTED`

This terminal means the generic records and hostile tests exist and replay. It grants no scientific terminal for any child atom.