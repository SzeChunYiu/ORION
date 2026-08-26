# ORION-16–ORION-18 donor assimilation matrix — 2026-08-17

**Status:** active research ledger; not a novelty verdict.  
**Owner:** #352, with dispositions feeding #334/#337/#340 and overlap gate #343.  
**Rule:** nearest work is treated as a donor of mechanisms before it is treated as a novelty boundary.

## 1. Assimilation protocol

For each donor, ORION records five things separately:

1. **atomic mechanism** — what the work actually does;
2. **protected uniqueness** — what the donor owns and ORION must not relabel;
3. **assimilation disposition** — `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER`, or `REJECT`;
4. **generalization hypothesis** — the larger structure suggested when the donor is combined with others;
5. **discriminator** — a theorem, countermodel, transfer test, or benchmark result that would show the generalization is more than juxtaposition.

A donor remains identifiable after assimilation. If ORION can only subsume a work by erasing the condition that makes it strong, the embedding is invalid.

## 2. Cross-paper common structure under test

The broad candidate common structure is an **epistemic transition contract**:

\[
\mathcal C=(S,Req,Eff,Dep,Prov,Auth,Obs,Hist,Inv),
\]

where a system has typed state `S`, residual requirements `Req`, requested/committed effects `Eff`, dependency structure `Dep`, provenance `Prov`, authority `Auth`, observations/coverage `Obs`, retained history `Hist`, and invariants `Inv`.

The papers study different projections:

- **ORION-16:** how contracts compose, invalidate/reopen dependent state, and recurse;
- **ORION-17:** how the represented state/route/objective space itself changes during inquiry;
- **ORION-18:** when a requested epistemic effect is authorized to commit, especially across domains.

This tuple is a research scaffold, not a claim that prior work lacks any of these fields.

## 3. ORION-16 donors — structures, effects, dependencies, repair

| Donor | Atomic mechanism / protected uniqueness | Disposition | ORION absorption | Required discriminator |
|---|---|---|---|---|
| Dynamic Epistemic Logic / action models | Formal semantics for information-changing actions and epistemic model update. | ADOPT | Use action/update semantics as a parent language for epistemic change. | ORION-16 must add a property involving authority/obligations/dependency reopening or composition that DEL alone does not settle. |
| AGM + iterated belief revision | Rational postulates for expansion/contraction/revision and iterated change. | ADOPT | Treat belief-state change as one mechanic family, not the whole mechanic theory. | Exhibit non-belief coordinates/effects whose correctness depends on authority/provenance/dependency contracts. |
| Truth-maintenance / dependency-directed revision | Justification/dependency tracking and selective retraction are established. | ADOPT | Use dependency closure as donor machinery for reopening and rollback. | Show a typed mechanic composition property beyond generic TMS reachability. |
| Epistemic separation/action logics | Locality and compositional reasoning for epistemic actions. | ADOPT | Reuse separation intuition for disjoint read/write footprints and frame-style preservation. | ORION-16 commutation must be stated modulo trace/history semantics rather than falsely claiming ordered histories are equal. |
| CoALA (arXiv:2309.02427) | Modular memory/action/decision architecture for language agents. | ADOPT | Use as architectural embedding target; do not claim modules are new. | Demonstrate that two same-module architectures can differ under explicit commit/reopen/authority contracts. |
| Mechanism-level cognitive/language-agent review (arXiv:2607.23942) | Reconstructs mechanisms via state, control, transition, persistence, failure, learning, resource governance; identifies residual mechanism bundles. | ADOPT | Use its decomposition axes as a completeness checklist for ORION-16 mechanic signatures. | ORION must explain a coupling/invariant not already one of the review's retained bundles. |
| ETAS (arXiv:2607.17780) | Agent programming language with typed effects, requested/handled/denied/committed events, persistent action traces, residual obligations, policy safety and trace transparency. | ADOPT + COMPOSE | Add requested-vs-committed effects, residual obligations and trace-visible authorization to ORION-16/ORION-18 semantics. | ORION-16 cannot claim effect typing; it must show a cross-mechanic epistemic property such as dependency-minimal reopening or history-aware composition. |
| FAVA (arXiv:2607.27267) | Permission IR lowered to an evidence-backed permission graph; SMT authorization before effectful actions; runtime counterexamples. | ADOPT + COMPOSE | Treat evidence-backed authorization graphs and deterministic pre-effect enforcement as a concrete authority implementation. | Generalization must cover epistemic effects/closure/revocation across domains, not merely reproduce permission checking. |
| AgentTether (arXiv:2607.06273) | Transition Units + dependency-aware Critical Transition Graph for failure localization and guarded runtime repair. | ADOPT | Use transition-unit granularity and failure-critical dependency paths as repair donors. | ORION-16 must distinguish diagnosis/local repair from contract-level invalidation and authorization. |
| Dependency-Guided Rollback Repair (arXiv:2608.10502) | Typed memory-to-action graph, downstream dependency tracing, preservation of independently supported state, selective replay after faulty memory. | ADOPT + COMPOSE | This is a direct donor for dependency-scoped reopening, preservation, and selective replay. | ORION-16 must not claim selective rollback itself; test a more general theorem covering heterogeneous coordinates/mechanics and authority-bearing commits. |

### ORION-16 widened residual under test

Not “typed mechanics” by itself. The stronger candidate is a **history-aware epistemic effect/repair algebra** in which:

- effects are requested before they are committed;
- hard residual obligations and authority are explicit;
- committed effects induce dependency-scoped reopening/rollback;
- unaffected state is preserved under a frame condition;
- independent mechanics commute on the scientific projection while their ordered audit traces remain distinguishable;
- recursive audit cannot rewrite the protected authority root that licenses its own promotion.

A valid ORION-16 must embed donor mechanisms as specializations and still leave at least one theorem or transfer result that is not a renamed donor result.

## 4. ORION-17 donors — exploration, partial observability, changing representations

| Donor | Atomic mechanism / protected uniqueness | Disposition | ORION absorption | Required discriminator |
|---|---|---|---|---|
| Search-on-Graph (arXiv:2510.08825) | Observe-then-navigate KG traversal rather than precompiled paths or large subgraph retrieval. | ADOPT | Fixed-chart iterative navigation baseline. | ORION-17 topology/atlas change must solve instances unreachable under every fixed-chart policy, not merely improve prompting. |
| Mind-ParaWorld / MPW-Bench (arXiv:2603.04751) | Dynamic parallel-world evaluation with atomic ground truth; exposes evidence collection/coverage, sufficiency and stopping failures. | ADOPT | Use atomic hidden-world construction and coverage/stopping probes as benchmark donors. | ORION-17 must add representation-change and support-transfer cases absent from fixed-world search evaluation. |
| Initial Exploration Problem (arXiv:2602.21066) | Scope uncertainty, ontology opacity and query incapacity at first contact; scope-revelation problem. | ADOPT | Add explicit orientation/scope-revelation state before ordinary route optimization. | Show that orientation obligations alter admissible navigation/stopping, rather than just UI/query quality. |
| POMDP / belief-space information gathering | Planning under partial observability and information acquisition are mature. | ADOPT | Use belief over locations/models and value-of-information as utility machinery. | ORION-17 must separate resource/value decisions from scientific completion authority and representation validity. |
| SAGA (arXiv:2512.21782) | Outer-loop autonomous objective evolution with inner-loop optimization across scientific design domains. | ADOPT + COMPOSE | Treat objective change as one kind of chart/obligation transformation, not as generic edge traversal. | ORION-17 must specify when old evidence/closures transport across objective change and when they reopen. |
| Self-Evolving World Models (arXiv:2606.30639) | Test-time world-model revision from prediction/observation mismatch with selective foresight. | ADOPT | World-model revision becomes a donor for topology/model evolution. | ORION-17 must cover explicit map/preservation obligations and task-stop authority, not only better prediction/planning. |
| Graph World Models (arXiv:2604.27895) | Structured graph representations; dynamic graph adaptation identified as an open direction. | ADOPT | Use multi-granularity graph/world-model views as chart families. | Benchmark must include cross-chart transformations, not only graph updates inside one representation. |
| AI Research Agents Narrow Scientific Exploration (arXiv:2605.27905) | Large empirical result: AI-generated research ideas are more concentrated and closer to seed literature than human follow-on work. | ADOPT | Exploration breadth/concentration becomes a ORION-17 outcome, not just final success. | Demonstrate whether atlas-changing mechanisms broaden useful reachable regions without uncontrolled reframing. |

### ORION-17 widened residual under test

Replace a single mutable graph with an **epistemic atlas**:

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal M,\Omega,\mathcal C),
\]

where `T_i` are local representations/charts, `\mathcal M` is a set of partial preservation/translation maps, `\Omega` is the obligation/objective family, and `\mathcal C` records coverage/censoring contracts.

Navigation can therefore include:

- motion inside a chart;
- route discovery and orientation;
- belief update under partial observability;
- chart/world-model revision;
- objective/obligation transformation;
- transport, reopening, or `CANNOT_CHECK` for prior closures;
- local stopping without unauthorized global completion.

The key discriminator is not “dynamic graph.” It is whether changing representation/objective alters reachability and obligation semantics while preserving only the old evidence whose complete support transports through a valid map.

## 5. ORION-18 donors — permission, abstention, provenance, enforcement

| Donor | Atomic mechanism / protected uniqueness | Disposition | ORION absorption | Required discriminator |
|---|---|---|---|---|
| ETAS (arXiv:2607.17780) | Typed effect rows, trace policies, residual obligations, committed-event semantics and policy safety. | ADOPT + COMPOSE | Make effect requests and commit-time authorization first-class. | ORION-18 cannot claim typed effects/policies; test cross-epistemic-domain coercions, revocation and laundering. |
| FAVA (arXiv:2607.27267) | Evidence-backed permission graphs + deterministic SMT authorizer before effectful actions. | ADOPT + COMPOSE | Use permission graphs/solver as a strongest enforcement baseline. | ORION-18 must outperform or strictly generalize FAVA-style single-policy authorization on cross-domain epistemic authority cases. |
| AgentAbstain (arXiv:2607.10059) | Paired should-act/should-abstain executable benchmark; abstention competence distinct from task competence; post-hoc abstention failure. | ADOPT | Use paired action/inaction cases and pre-effect timing. | ORION-18 must distinguish abstention from `CANNOT_CHECK`, revocation, and typed authorization rather than rebranding refusal. |
| ProvenanceGuard (arXiv:2606.18037) | Source-aware claim routing and support/attribution verification with allow/block and repair/reverify. | ADOPT | Treat source identity as a non-substitutable evidence dimension for assertion authority. | Cross-source support cannot authorize unrelated source attribution; generalize this as typed evidence-domain non-fungibility. |
| Execution-provenance survey (arXiv:2606.04990) | Unified taxonomy of trace/evidence units, provenance relations, granularity, timing, trust functions, recovery. | ADOPT | Use as provenance completeness checklist across ORION-16/ORION-18. | ORION-18 must add derivational authority properties, not just richer trace schemas. |
| Agent-Sentry (arXiv:2603.22868) | Learns behavioral bounds from execution traces and blocks out-of-bounds/misaligned tool calls. | ADOPT | Treat behavioral-bounds enforcement as another authority source/baseline. | Cross-capability scientific authorization must not collapse to anomaly detection. |
| Policy Cards (arXiv:2510.24383) | Machine-readable allow/deny rules, obligations, evidentiary requirements and runtime governance mapping. | ADOPT | Use policy artefacts as one external authority/root representation. | ORION-18 must formalize derivation/composition/revocation across epistemic domains rather than only encode policies. |
| User-permission systems survey (arXiv:2607.13718) | Taxonomy of permission specification, internal policy derivation and runtime enforcement across 21 proposals + commercial systems. | ADOPT | Use taxonomy to prevent ORION-18 from claiming generic permissions/governance novelty. | Identify a scientific-epistemic authorization problem not covered by ordinary user-intent permission systems. |
| ORION-14 Verified Scientific Discovery | Protected, content-bound, non-escalating scientific-authority promotion already exists inside ORION. | ADOPT, DO NOT RELABEL | Embed ORION-14 as the `ASSERT` domain instance. | ORION-18 exists only if cross-domain composition/anti-laundering predicts failures that isolated ORION-14 does not. |
| ORION-15 Self-ORION | Protected evaluation, fresh transfer, negative history and no self-promotion already exist inside ORION. | ADOPT, DO NOT RELABEL | Embed ORION-15 as the `SELF_MODIFY` domain instance. | ORION-18 must not claim self-promotion safety; it must show why authority cannot be silently transported from other domains into self-modification. |

### ORION-18 widened residual under test

The broad target is a **typed epistemic authority calculus over effect domains**. A valid authorization derivation records:

- effect domain and scope;
- content-bound support and provenance;
- hard obligations and defeaters;
- the issuer/root of any grant;
- explicit cross-domain coercions;
- commit-time validity/epoch;
- dependency lineage for later revocation;
- terminal `ALLOW`, `DENY`, `DEFER`, or `CANNOT_CHECK`.

**Authority laundering** is then a formal derivation error: a judgment in domain `d` contributes to authorization in `d'` without an explicit registered coercion whose premises are satisfied.

This is intentionally broader than access control but must absorb access-control/effect-system machinery rather than compete with it on its home ground.

## 6. New cross-donor theorem obligations

The following are *research targets*, not established results.

### G1 — Donor-faithful embedding
For each adopted donor, define a structure-preserving embedding into the relevant ORION projection that preserves the donor's decisive allow/deny, update, route, or rollback judgments on its native cases.

**Falsifier:** an embedding that changes a donor's native verdict merely to make ORION look more general is rejected.

### G2 — Conservative extension
When the additional ORION dimensions are inert, the generalized calculus should reduce to the donor behavior rather than invent new actions or authority.

### G3 — Cross-domain non-fungibility
Evidence/utility/permission valid for one action domain is not substitutable for a hard obligation in another domain except through an explicit sound coercion.

### G4 — Reframe transport theorem
A certified result transports across a representation/objective change only when its full support and closure scope are preserved by the chart/obligation map; otherwise it reopens or becomes `CANNOT_CHECK`.

### G5 — History-aware commutation
Independent mechanics may commute on the scientific state projection while producing different ordered audit histories. Equality should therefore be quotient/trace equivalence, not literal whole-state equality.

### G6 — Selective repair conservation
A sound dependency repair should invalidate every affected descendant while preserving independently supported state; full reset and no-reset are limiting baselines, not default semantics.

### G7 — Width-with-negative-controls
A more expressive generalization must not automatically dominate: on tasks where fixed topology, local gates, or simple repair are sufficient, ORION should avoid unnecessary reframing, refusal, or reopening.

## 7. Benchmark consequences

#353 owns cross-domain transfer. Minimum families:

- **ORION-16:** finite symbolic transition systems; memory/state repair; workflow dependency rollback; authorization-bearing mechanics;
- **ORION-17:** dynamic graph/ontology exploration; objective-evolving optimization; non-retrieval scientific design; negative fixed-chart controls;
- **ORION-18:** tool authorization, scientific assertion, merge/integration, stopping/closure, and self-change paired cases, with cross-domain laundering attacks.

Every family must include the strongest relevant donor baseline rather than only an untyped/scalar strawman.

## 8. Current disposition

The programme is deliberately wider after assimilation. Width does not authorize novelty. Current terminal for ORION-16, ORION-17 and ORION-18 remains `CANNOT_CHECK` until the donor embeddings, external saturation, overlap matrix, deterministic falsifiers, and protected evaluations close.