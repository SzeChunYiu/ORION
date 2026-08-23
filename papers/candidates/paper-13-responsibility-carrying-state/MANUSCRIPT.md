# Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse

**ORION publication candidate P13**  
**Issue:** #666 · child track #668  
**Manuscript status:** complete current-evidence draft; permanent negative retained, efficacy gate open  
**Evidence date:** 2026-08-20

## Abstract

A compact state can be sufficient for one task and unsafe for another. Prediction, action selection, intervention, verification and repair may require different distinctions in the underlying world, so the phrase “sufficient state” is incomplete unless the downstream responsibility is named. We formalize **responsibility-relative sufficiency** and use *sufficiency debt* as an operational benchmark quantity: two representations may be matched for a lower responsibility while differing materially for a higher one. ORION’s first frozen controlled attempt produced the intended exact `+0.50` upward debts but failed its preregistered finite-sample sanity sentinel (`0.0556640625 > 0.05`); that terminal remains permanently negative. We therefore specify an independently frozen successor based on exact responsibility equivalence classes, prospective lower-rung noninferiority and confidence intervals for higher-rung verified performance differences rather than retuning the failed threshold. We also define a `ResponsibilityCarryingState` interface that binds state/evidence identity, supported responsibilities, independent witness identities, explicit omissions, recoverability, resource envelope, context coordinates and reopen conditions. A finite hostile substrate is already GREEN: supported use is allowed, unsupported or approximate use fails closed, relevant context change requires reopening when raw state is recoverable, semantic drift yields `CANNOT_CHECK`, resource mismatches fail closed, and evaluator/authority identity collapse is rejected. This is engineering evidence, not efficacy. The paper’s scientific gate requires a prospective demonstration that responsibility-carrying state reduces unsafe reuse relative to confidence-only and unqualified compression without degenerating to always-raw or always-reopen behavior, with at least one verifier-backed real-system validation.

## 1. Introduction

State compression is usually evaluated against a named task: prediction accuracy, policy value, reconstruction quality or another objective. Difficulties appear when a compact state is reused after the responsibility changes. A summary adequate for answering a question may omit provenance needed to authorize a scientific claim. A proof-state abstraction adequate for next-tactic prediction may omit a dependency needed to diagnose or repair a failed proof. A control state adequate for one policy may collapse distinctions needed for counterfactual intervention.

The logical fact that prediction, control and intervention can require different state distinctions is donor-owned by statistical sufficiency, predictive state representations, causal abstraction, state abstraction and related literatures. P13 does not claim to invent that distinction. Its narrower question is operational and systems-facing:

> Can a compact state carry an auditable contract that says what responsibilities it supports, what it intentionally omits, which witness certifies the scope, what raw/richer state can be recovered, and what changes force the system to stop reuse and reopen?

The problem has two parts. First, we need an evaluation that exposes **responsibility shift**: matched performance at a lower rung but divergent performance at a higher rung. Second, we need a reusable state interface that detects the boundary *before* a failure rather than relying on post-hoc confidence.

P13 is built around a five-rung ladder:

1. predict/classify;
2. choose or plan an action;
3. intervene/control/counterfactually reason;
4. verify or diagnose failure;
5. repair/recover after failure.

The ladder is not asserted to be universal or strictly ordered in every domain. It is a benchmark scaffold for asking whether a representation that merges world states under one responsibility remains safe under another.

## 2. Donor boundary

The following conceptual territory is prior-owned:

- statistical sufficiency and task-relative information preservation;
- predictive state representations;
- bisimulation and state abstraction for control;
- causal/interventional sufficiency and abstraction;
- rate-distortion state abstractions;
- confidence/uncertainty gating and selective prediction;
- proof-carrying code/actions/reasoning;
- certified abstractions and dynamic assurance;
- provenance/evidence contracts;
- capability and authorization systems;
- raw-history/always-reopen safety baselines.

P13’s proposed residual is the combination of:

1. a cross-responsibility benchmark with exact lower-rung equivalence and higher-rung divergence;
2. a responsibility-carrying state contract with explicit omissions, recoverability and reopen semantics;
3. a safety–cost evaluation of state reuse across responsibility shifts;
4. integration with ORION’s pre-existing transport/revocation and scientific-authority boundaries rather than a new self-authorizing calculus.

## 3. Responsibility-relative sufficiency

Let `X` be a latent/raw world and let responsibility `rho` induce a correct decision/output function `g_rho(X)`. Let a representation be `Z=T(X)`.

### Definition 1 — exact responsibility sufficiency

`Z` is sufficient for responsibility `rho` over world set `Omega` if there exists a function `h_rho` such that

`g_rho(x)=h_rho(T(x))`

for every `x in Omega`.

Equivalently, whenever `T(x)=T(x')`, the responsibility outputs must agree:

`g_rho(x)=g_rho(x')`.

This equivalence-class view is useful because it requires no learner and exposes exactly which world distinctions the representation collapses.

### Definition 2 — responsibility shift witness

A pair `(x,x')` is a shift witness from lower responsibility `rho_L` to higher/different responsibility `rho_H` for representation `T` if:

- `T(x)=T(x')`;
- `g_rho_L(x)=g_rho_L(x')`;
- `g_rho_H(x) != g_rho_H(x')`.

The representation is therefore adequate for the lower responsibility on this pair but cannot support the higher one exactly.

### Definition 3 — operational sufficiency debt

For a fixed representation and transition `rho_L -> rho_H`, define a benchmark debt as the higher-rung verified-performance gap between a richer/reference state and the compact state **conditional on a prospectively frozen lower-rung equivalence/noninferiority requirement**.

This is an operational quantity, not a new universal information measure. Each transition is reported separately rather than hidden in one averaged debt score.

## 4. Permanent negative history: the failed P14A terminal

The first frozen controlled sufficiency-debt experiment predates the grouped publication remap and is permanently retained.

Terminal:

`P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET`.

### 4.1 What the construction established

Full enumeration of eight latent states matched the registered ladder exactly:

- representations `Z1/Z2/Z3` were perfect for PREDICT and DECIDE;
- `Z1` achieved exactly `0.5` on INTERVENE and VERIFY while `Z2/Z3` achieved `1.0`;
- `Z2` achieved exactly `0.5` on REPAIR while `Z3` achieved `1.0`;
- registered upward debt differences were therefore exactly `+0.50`;
- no representation carried a responsibility-answer field.

### 4.2 What failed

The protocol also required the maximum deviation over 100 finite-sample sanity replicates of `n=1024` to be `<=0.05`. The observed maximum was

`0.0556640625`

at replicate 92. Therefore the combined frozen gate failed.

### 4.3 Disposition

The exact finite construction remains valid as mathematics/control structure, but the terminal is negative. The threshold is never edited, and the result is never retrospectively promoted. Any successor must use an independently justified estimand and protocol.

This negative is central to P13’s methods stance: a research programme cannot claim responsibility-aware reuse while silently deleting a preregistered miss.

## 5. Independently frozen successor protocol

The successor protocol is designed to answer the scientific question more directly rather than to make the old sentinel easier to pass.

### 5.1 Experiment 1 — exact responsibility lattice

Construct finite worlds with exact gold for the five responsibility classes. For every candidate representation:

1. enumerate equivalence classes induced by `T`;
2. compute whether each class is homogeneous under each `g_rho`;
3. record the responsibility × representation sufficiency matrix;
4. identify minimal witness coordinates where tractable;
5. generate matched pairs with identical lower-rung outputs but opposite higher-rung gold.

All state variants derive from the same raw world. Higher rungs do not receive hidden extra input.

### 5.2 Experiment 2 — statistical debt replication

Use a fresh generator and new seed family. Freeze:

- representation/rung transitions;
- lower-rung equivalence/noninferiority margin;
- higher-rung primary estimand;
- number of families/seeds;
- interval procedure;
- stopping rule.

Primary effect:

`Delta_H = verified_performance(richer_state, rho_H) - verified_performance(compact_state, rho_H)`

subject to the lower-rung equivalence/noninferiority condition being met prospectively.

Use paired exact/binomial or blocked bootstrap intervals as appropriate to the unit of generalization. Do not use the old maximum-deviation sentinel as a target to beat.

### 5.3 Why this is not retuning

The old P14A asked whether a specific fixed sanity sentinel passed. It did not. The successor asks a different, scientifically primary question: conditional higher-responsibility performance separation with explicit lower-responsibility matching and uncertainty. It receives a new protocol identity and can succeed or fail independently.

## 6. ResponsibilityCarryingState

A responsibility-carrying state (RCS) is a compact/compiled state plus a non-self-authorizing contract.

### 6.1 Required contract fields

An RCS binds:

- source/raw evidence identity;
- compiler/transform identity and version;
- exact supported responsibility set;
- independent witness/certificate identity per supported responsibility;
- intentionally omitted coordinates/information classes;
- required-same context coordinates;
- reopen-on-change coordinates;
- raw recovery/reconstruction availability;
- recovery/reopen cost;
- resource envelope under which the certificate holds;
- evaluator identity;
- authority owner identity distinct from evaluator where required;
- explicit statement that the object grants no scientific or novelty self-authority.

### 6.2 Decision semantics

At reuse time the interface returns a fail-closed action such as:

- `USE_COMPILED` — requested responsibility is supported and all bound context/resource conditions hold;
- `REOPEN_REQUIRED` — richer/raw state can be recovered and a registered change invalidates direct reuse;
- `CANNOT_CHECK` — responsibility is unsupported, witness is approximate/unacceptable, required-same semantic context changed, resource envelope mismatches, recovery is unavailable/stale, or another contract condition is unresolved.

`CANNOT_CHECK` is not failure to be hidden; it is the correct disposition when the state cannot establish safe reuse.

## 7. Existing hostile substrate result

Terminal:

`P17_RESPONSIBILITY_CARRYING_STATE_SUBSTRATE_GREEN`.

The finite hostile suite demonstrates:

- supported responsibility + exact bound/context -> `USE_COMPILED`;
- approximate witness -> `CANNOT_CHECK`;
- unregistered higher-rung responsibility -> `CANNOT_CHECK`;
- registered reopen-trigger change + recoverable raw -> `REOPEN_REQUIRED`;
- required-same semantic change -> `CANNOT_CHECK`;
- requested resource-bound mismatch -> `CANNOT_CHECK`;
- evaluator/authority identity collapse -> construction rejected.

This is **engineering/governance evidence only**. It shows the interface can encode fail-closed semantics; it does not show that RCS improves task outcomes or resource efficiency.

## 8. Responsibility-shift benchmark

### 8.1 Arms

1. unqualified compact state;
2. compact state + scalar confidence;
3. compact state + provenance only;
4. `ResponsibilityCarryingState`;
5. always-raw/full-state;
6. always-reopen safety ceiling.

### 8.2 Episode structure

A compact state is created under responsibility `rho_0`. Later, before action, the required responsibility may remain the same or shift. The system must choose among direct reuse, reopen/recover, or `CANNOT_CHECK` without seeing protected failure outcomes.

### 8.3 Primary endpoint

**Unsafe reuse rate**: proportion of episodes in which a system reuses compact state for a responsibility that the protected gold says the state cannot support.

The safety endpoint is constrained by a frozen task-success noninferiority/utility requirement so “always abstain” cannot win.

### 8.4 Secondary endpoints

- verified final task success;
- unnecessary reopen rate;
- raw bytes/tokens loaded;
- recovery latency;
- verifier calls/tool calls;
- state/certificate bytes;
- correct `CANNOT_CHECK`;
- stale-recovery failures.

Results are presented as a safety–cost frontier, not a single composite score.

## 9. Certificate transport and revocation

Prospectively mutate:

- source evidence identity/version;
- compiler version;
- representation mapping;
- objective/responsibility;
- evaluator/verifier version;
- other registered context coordinates.

Gold labels distinguish preserve, transport, reopen, revoke and unresolved outcomes. RCS transport/revocation must compose with ORION P6/P7/P8 semantics rather than creating a second authority system.

A certificate is invalid if the compiler or evaluator silently certifies its own scientific authority, if the represented evidence is stale, or if a semantic change is treated as a cosmetic version change.

## 10. Real-system programme

### 10.1 Lean/formal reasoning

Use a natural responsibility ladder:

- predict next tactic;
- choose/search an action;
- verify candidate proof;
- diagnose rejection;
- repair proof.

Construct matched tasks where a compact state adequate for prediction omits information required for diagnosis/repair. Exact verifier success is the final outcome. Report unsafe reuse and repair success at matched state/reopen/verifier cost.

### 10.2 Scientific/research workflow

Responsibilities include:

- summarize evidence;
- answer a question;
- decide whether more evidence is required;
- authorize/promote a claim;
- revise after counterevidence.

Use cases with matched answer surfaces but different provenance, dependency, custody or defeater structure. The P13 system may decide whether its state is sufficient to proceed, but it cannot self-authorize scientific novelty or truth; external evaluators retain that authority.

### 10.3 Optional non-formal procedural domain

A third domain should involve procedural/control responsibility shifts with exact or independently checkable outcomes. This guards against a P13 effect that is specific to Lean or research-governance vocabulary.

## 11. Statistics

The exact responsibility-lattice study is deterministic. The old P14A finite-sample result is reported exactly as frozen and is not reanalysed to create a new terminal.

For the successor:

- define the independent unit (task/world/family) before analysis;
- use paired comparisons because arms share the same episodes;
- require prospective lower-rung equivalence/noninferiority;
- estimate higher-rung effect sizes with confidence intervals;
- block headline uncertainty by task family/domain when generalization is claimed;
- report each responsibility transition separately;
- prespecify safety primary + task-success constraint for RCS;
- do not invent p values, margins, `n`, or interval methods before protocol freeze.

Interventions on certificate transport/revocation with exact gold may be reported as exact rates plus binomial/blocked intervals when a sampling population is defined.

## 12. Negative-result elimination programme

### N1 — old P14A sentinel failure

**Preserved terminal:** `P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET`.

**Elimination route:** replace the scientifically indirect maximum-deviation sentinel only in a new protocol with the direct conditional higher-rung effect and prospective lower-rung matching. The old result remains negative forever.

### N2 — responsibility debt disappears after stronger learner

If richer learner capacity removes the higher-rung gap, the result may indicate decoder limitation rather than state insufficiency. The exact equivalence-class study therefore provides learner-free witnesses; empirical studies include matched stronger decoders where appropriate. If no exact witness exists, do not claim state-level insufficiency.

### N3 — RCS is just confidence with extra words

Compare against a scalar-confidence baseline and a provenance-only baseline. Construct matched confidence episodes where responsibility support differs. If RCS adds no prospective safety value beyond confidence, narrow or reject the interface efficacy claim.

### N4 — always-reopen dominates

Require task-success noninferiority and report raw retrieval, latency, verifier calls and unnecessary reopen. A valid positive requires an interior safety–cost improvement, not only lower unsafe reuse.

### N5 — compiler/evaluator self-certifies

Construction rejects evaluator/authority collapse where those roles must be distinct. Every responsibility witness identity is external to the candidate state’s own scientific-authority claim.

### N6 — advertised recovery is stale or unavailable

Test raw deletion, version drift, invalidation and reconstruction failure. Recovery availability is an audited fact, not a metadata promise.

### N7 — certificate silently survives semantic change

Freeze required-same and reopen-on-change coordinates. Mutate them prospectively and require preserve/reopen/revoke/`CANNOT_CHECK` behavior against external gold.

## 13. Planned figures

1. Responsibility ladder and representation equivalence classes.
2. Exact responsibility × representation sufficiency matrix.
3. Matched lower-rung / divergent higher-rung performance with old negative history shown separately.
4. Unsafe reuse versus state/reopen/verifier cost for compact, confidence, provenance, RCS, raw and always-reopen arms.
5. Certificate lifecycle through context change, transport, reopen and revocation.
6. Verifier-backed real-system result or explicit negative.

## 14. Discussion

P13 treats reuse as a contract question rather than a confidence question. Confidence estimates how strongly a system believes an output under its current view; it does not, by itself, identify whether the current view omits information required for a different responsibility. Provenance identifies where state came from but does not necessarily state what the state can safely support. A responsibility-carrying contract makes those boundaries explicit and machine-checkable.

The approach is intentionally conservative about authority. A state can carry evidence that it is sufficient for a defined operational responsibility without carrying authority to declare a scientific claim true or novel. This distinction is necessary in research workflows, where a compact summary might support question answering but not claim promotion.

Negative history is equally important. The failed P14A sentinel demonstrates why an auditable research system must separate exact constructions from preregistered empirical gates. The construction can remain informative while the terminal remains negative. P13’s successor must earn a new result without rewriting that history.

## 15. Limitations

1. Responsibility ladders are domain-dependent and may be partially ordered rather than linear.
2. Exact sufficiency can be too strict for stochastic systems; approximate responsibility contracts require carefully specified tolerances/witnesses.
3. Current RCS evidence is only substrate correctness, not efficacy.
4. Certificate metadata can become expensive or stale; its own resource cost must be counted.
5. External witness quality is a separate problem and cannot be solved by the RCS container itself.
6. Always-reopen may remain rational in very high-risk domains; P13 does not require compact reuse to dominate universally.
7. Real-system Lean/research evaluations are not yet executed.

## 16. Reproducibility and evidence identity

Current evidence artifacts on the Frontier V2 branch/PR include:

- `P14A_CONTROLLED_SUFFICIENCY_DEBT_PROTOCOL_V1.md`;
- `P14A_OUTCOME_DISPOSITION_V1.md`;
- `results/P14A_CONTROLLED_SUFFICIENCY_DEBT_V1.json`;
- `P17_RESPONSIBILITY_CARRYING_STATE_PROTOCOL_V1.md`;
- `responsibility_carried_state_v1.py`;
- `check_p17_responsibility_carried_state_v1.py`;
- `P17_SUBSTRATE_CHECK_RECEIPT_V1.md`.

The old numbering is preserved as historical evidence; issue #666 defines the current grouped P13 publication identity.

## 17. Data and code availability

No protected successor efficacy dataset has been executed. The final P13 package must release or identify the exact world generator, frozen splits, responsibility gold, state/certificate schemas, hostile tests and machine-readable resource receipts.

## 18. Claim ledger

| Claim | Status | Evidence | Forbidden widening |
|---|---|---|---|
| sufficiency is responsibility-relative in exact constructed worlds | CONTROLLED/DEFINITIONAL FOUNDATION | exact P14A construction | claim of conceptual novelty over causal/RL donors |
| P14A combined controlled gate passed | NEGATIVE / FALSE | `0.0556640625 > 0.05` | never relabel positive |
| RCS fail-closed interface substrate works on hostile finite cases | ENGINEERING GREEN | P17 receipt | efficacy/safety superiority |
| new statistical debt protocol replicates higher-rung gap | OPEN | successor E2 | may not be assumed |
| RCS reduces unsafe reuse vs confidence/unqualified state | OPEN | responsibility-shift benchmark | may not be stated now |
| RCS avoids always-reopen degeneration | OPEN | safety–cost frontier | may not be inferred from substrate |
| transport/revocation works across semantic changes | OPEN beyond substrate | mutation benchmark | no silent preservation claim |
| verifier-backed real-system benefit | OPEN | Lean/procedural/research domain | no real-system claim yet |

## 19. Publication decision

**Current decision:** scientifically coherent current-evidence manuscript with one permanent negative and one GREEN engineering substrate; not yet externally promotable as the full P13 result.

Minimum promotion requires: independently frozen successor debt result, RCS safety–cost advantage without always-reopen degeneration, certificate transport/revocation evidence, and at least one verifier-backed real-system domain.

## References and donor notes

1. Classical statistical sufficiency and state-abstraction literatures — final paper requires task-specific canonical sources selected by the external literature pass.
2. ORION P6/P7/P8 canonical bibliography for dynamic change, authorization, provenance and non-amplification donors.
3. Doyle, J. **A Truth Maintenance System.** *Artificial Intelligence* 12(3):231–272 (1979). DOI `10.1016/0004-3702(79)90008-0`.
4. de Kleer, J. **An Assumption-Based TMS.** *Artificial Intelligence* 28(2):127–162 (1986). DOI `10.1016/0004-3702(86)90080-9`.
5. Park, J. & Sandhu, R. **The UCONABC Usage Control Model.** *ACM TISSEC* 7(1):128–174 (2004). DOI `10.1145/984334.984339`.

### Citation integrity note

A final academic-search and reference-verification pass is mandatory for causal abstraction, certified abstraction, proof-carrying reasoning and 2025–2026 agent provenance/governance donors. Contemporary metadata is not invented while the external search service is unavailable.
