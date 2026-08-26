# ORION-16–ORION-18 mathematical completion path

**Status:** active candidate-paper programme.  
**External LLM API requirement:** **none**.  
**Breadth policy:** assimilate strong donor mechanisms before narrowing; preserve donor-native semantics; claim only cross-donor residuals that survive falsification.

The three candidate papers can be advanced as theorem-led formal-methods papers with prospective cross-domain experiments. Internet access is required for current literature closure and source verification, and independent scholarly review is required before peer-review readiness can be claimed. No theorem, proof, novelty verdict or completion gate may depend on a proprietary LLM judge.

## 1. What “complete” means

Three terminals remain distinct.

1. **Mathematically complete manuscript** — definitions, semantics, theorem statements, proofs/countermodels, examples, limitations, bibliography and reproducibility instructions are present.
2. **Novelty-bounded manuscript** — the surviving residual has passed donor assimilation (#352), nearest-work review (#334/#337/#340), novelty (#287) and ORION-11–ORION-15 ownership (#343).
3. **Peer-review ready** — mathematical arguments have independent review, deterministic/mechanized checks reproduce where applicable, prospective evaluations are complete, final literature closure is current, and the claim ledger authorizes every headline sentence.

A manuscript may reach (1) while terminating as `MERGE_INTO_EXISTING_PAPER`, `PROCESS_ONLY_NOT_NOVEL`, `ALREADY_SOLVED`, `REFUTED` or `CANNOT_CHECK` at (2). That counts as a successful research outcome.

## 2. Non-LLM toolchain

Default completion path:

- Markdown/LaTeX for manuscripts;
- Python standard-library finite-model enumerators and counterexample generators;
- Lean 4/Isabelle/HOL or another proof assistant for selected structural theorems where formalization cost is justified;
- SAT/SMT/model checking when useful and reproducible;
- BibTeX plus DOI/arXiv/source-identity checks;
- Git/GitHub Actions for immutable execution and artifact hashes.

## 3. Expert-role review model

Every material finding is pressure-tested from five review functions. These are analytical roles, not claims of human participation.

- **Formal logician:** syntax, semantics, quantifiers, soundness, countermodels and theorem strength.
- **Formal-methods engineer:** executable correspondence, finite-model checks, proof-assistant targets, effect/process semantics and reproducibility.
- **Epistemic-navigation theorist:** partial observability, orientation, route identity, planning/representation abstractions, stopping and support transfer.
- **Authorization/governance logician:** obligation, permission, delegation, revocation, non-interference, laundering, epochs and protected roots.
- **Scientific editor/novelty auditor:** ORION-11–ORION-15 ownership, donor uniqueness, nonclaims, external literature breadth, transfer discriminators and claim authority.

A proposed result is retained only when the relevant roles agree on both what it establishes and what it does **not** establish.

## 4. Assimilation-first research architecture

The broad common scaffold under test is an epistemic transition contract

\[
\mathcal C=(S,Req,Eff,Dep,Prov,Auth,Obs,Hist,Inv),
\]

covering typed state, residual requirements, requested/committed effects, dependency, provenance, authority, observations/coverage, retained history and invariants.

This scaffold is not itself a novelty claim. #352 requires donor-faithful embeddings. If a strong donor cannot be embedded without changing its native verdicts, ORION's generalization is rejected or revised.

Current wide parent-field map: `PARENT_FIELD_PRESSURE_MAP_2026-08-17.md`.  
Current atomic donor map: `DONOR_ASSIMILATION_MATRIX_2026-08-17.md`.  
Internal ownership map: `P1_P5_OWNERSHIP_MATRIX_V1.md`.

## 5. ORION-16 theorem programme — Formal Epistemic Structures and Mechanics

### Current widened object
A **history-aware epistemic effect/repair algebra** combining typed effects, residual obligations, provenance, scoped commit authority, dependency repair, frame/separation conditions, retained audit traces and recursive audit under protected roots.

Native ORION-11 mechanic cells, recursive audit and reconstruction reopening remain ORION-11-owned special cases.

### Primary theorem targets

**ORION-16.T1 — Minimal sound reopening.** Under a dependency relation sound for the admissible semantic class, reopening every certified descendant of a changed coordinate is sufficient to prevent stale dependent certification and inclusion-minimal among graph-only strategies that must be uniformly sound for every compatible semantics.

**ORION-16.T2 — History-aware commutation under strong separation.** Two deterministic strongly separated mechanics commute on the current scientific-state projection, while ordered histories need only be equivalent under swaps of independent events:

\[
\pi_{sci}(m;n(E))=\pi_{sci}(n;m(E)),
\qquad H_{mn}\equiv_I H_{nm}.
\]

Literal equality of whole states is **not** claimed because audit chronology is retained.

**ORION-16.T3 — Sequential non-escalation.** Sequential composition of mechanics that can only retain/narrow authority or receive trusted-root grants cannot mint stronger untrusted authority.

**ORION-16.T4 — Residual-obligation preservation.** A hard residual obligation emitted by one mechanic survives composition until an authorized discharge rule closes it; later computational success cannot silently erase it.

**ORION-16.T5 — Recursive-audit termination.** Recursive audit terminates when each recursive call strictly decreases a well-founded rank; a self-loop gives the finite nontermination countermodel when no such condition exists.

**ORION-16.T6 — No internal self-authorization guarantee.** If a candidate can rewrite both its admission predicate and all evidence read by that predicate, external promotion soundness cannot be guaranteed without a protected authority root/invariant.

**ORION-16.T7 — Conservative donor embedding.** When ORION-16-only dimensions are inert, adopted donor systems retain their native update/allow/rollback/locality judgments.

### Priority donor embeddings

- Dynamic Epistemic Logic/action models;
- AGM/iterated belief revision and belief bases;
- TMS/ATMS/dependency-directed repair;
- separation/process/event-structure semantics;
- CoALA and mechanism-level agent architectures;
- ETAS typed effects/residual obligations/traces;
- FAVA evidence-backed permission graphs/pre-effect authorization;
- AgentTether transition-unit failure localization;
- dependency-guided rollback/selective replay.

### Existing deterministic artifact
`checkers/p6_finite_falsifiers_v1.py` — current bounded sanity pass: **5/5 PASS**. It is supporting evidence only, not a proof.

### Next proof/engineering artifacts

- exhaustive bounded enumeration rather than only hand fixtures;
- explicit donor-native conservative-embedding fixtures;
- partial-order/trace-equivalence checker;
- proof assistant target for ORION-16.T2 or ORION-16.T4 after semantics freeze;
- cross-domain exact-ground-truth transfer from #353.

## 6. ORION-17 theorem programme — Epistemic Navigation in Open Worlds

### Current widened object
An **open-world epistemic atlas**

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal M,\Xi),
\]

where local charts can differ in representation, world model, route structure and objective/obligation semantics, and partial maps specify what may transport between them.

ORION-11 owns native responsibility-triggered representation reconstruction; ORION-12 owns route independence, route/task stopping and fail-closed coverage. ORION-17 may only generalize their interaction with external navigation/planning donors.

### Primary theorem targets

**ORION-17.T1 — Stopping impossibility under extension ambiguity.** If a finite history admits two observationally equivalent admissible completions with different mandatory-task completion truth values, no history-only rule can soundly certify task completion for both.

**Correction:** absence of a closure certificate alone is **not** logically sufficient in every world class. A separate richness premise is needed to infer extension ambiguity from certificate absence.

**ORION-17.T2 — Strict expressivity of admissible chart change.** There exists a task family whose goal is unreachable under every policy restricted to the initial chart but reachable after an admissible chart change. This is an expressivity lemma, not a novelty claim by itself.

**ORION-17.T3 — Support/obligation transport.** A closed obligation transports across a reframe only when its complete support, semantic predicates/relations, evidence identities and relevant obligation meaning are preserved; otherwise it reopens or becomes `CANNOT_CHECK`.

**ORION-17.T4 — Evidence can survive while closure fails.** Objective/obligation change may preserve content-bound evidence while invalidating the prior task-closure judgment.

**ORION-17.T5 — Output overlap does not identify route independence.** Equal observed output can arise from structurally independent routes; disjoint output can arise from structurally dependent routes.

**ORION-17.T6 — Fail-closed task stopping.** Route exhaustion, low utility, budget depletion or reframing cannot by themselves derive `TASK_STOP` while a mandatory-open obligation remains.

**ORION-17.T7 — Conservative donor embedding.** Fixed-chart/standard-model specializations reproduce donor-native navigation/update/stop judgments.

### Priority donor/parent embeddings

- Search-on-Graph;
- Mind-ParaWorld / MPW-Bench;
- Initial Exploration Problem;
- POMDP/belief-space information gathering;
- planning abstractions, representation-language and plan-preserving homomorphism work;
- learned/adaptive planning representations;
- SAGA objective evolution;
- self-evolving/graph world models;
- scientific-exploration breadth/concentration work;
- ORION-12 native route/stop mechanics.

### Existing deterministic artifact
`checkers/p7_finite_falsifiers_v1.py` — current bounded sanity pass: **7/7 PASS**.

### Next proof/engineering artifacts

- exhaustive bounded atlas generator;
- explicit counterexample where no closure certificate exists but extension ambiguity is absent;
- plan/goal-preservation map fixtures from planning-abstraction donors;
- objective-change fixtures where evidence transports but closure reopens;
- non-retrieval exact-ground-truth benchmark from #353;
- negative controls penalizing unnecessary chart changes.

## 7. ORION-18 theorem programme — Epistemic Authority for Autonomous Science

### Current widened object
A **typed cross-domain epistemic authority calculus** over effect requests, hard obligations, content-bound judgments, grants, explicit cross-domain coercions, epochs, dependency-grounded revocation, `CANNOT_CHECK` and protected roots.

All five within-domain gates remain ORION-11–ORION-15-owned. Generic permission/effect/provenance/abstention machinery is donor-owned.

### Primary theorem targets

**ORION-18.T1 — Typed anti-laundering.** If all ordinary derivation rules preserve authority domain and only registered coercions may change it, a judgment rooted in `d` cannot authorize an effect in `d'` without a valid coercion path.

**ORION-18.T2 — Absolute blockers and extensible additive evidence.** With unbounded/extensible positive evidence and a finite blocker penalty, sufficiently much positive evidence can cross any fixed threshold while the blocker remains active. Absolute blockers therefore need explicit veto/conjunctive/lexicographic semantics or an externally bounded score space.

**ORION-18.T3 — Dependency-grounded revocation.** Revoking an evidence/grant ancestor invalidates certificates whose derivations necessarily depend on it while permitting a certificate with a complete independent valid derivation to survive.

**ORION-18.T4 — Pre-effect authorization.** A post-hoc refusal cannot retroactively prevent an already committed irreversible effect.

**ORION-18.T5 — Self-promotion boundary.** Candidate-controlled admission policy + candidate-controlled admission evidence cannot establish an externally defined promotion property.

**ORION-18.T6 — Conservative ORION-11–ORION-15 gate embedding.** The general calculus reproduces frozen native decisions for reframe, search/stop, map/merge, assert and self-modify domains.

**ORION-18.T7 — Conservative external donor embedding.** ETAS/FAVA-style native policy decisions are preserved when cross-epistemic-domain coercions are inactive.

**ORION-18.T8 — Cross-domain composition discriminator.** There exist compositions in which all producing modules issue locally valid judgments but an untyped composition authorizes an invalid downstream epistemic action; the typed-coercion calculus blocks the transport without blocking a matched valid-coercion control.

ORION-18.T8 is the decisive candidate-paper discriminator. If it collapses to standard authorization/non-interference theory with renamed domains and no scientific transfer value, ORION-18 should merge into ORION-14/programme synthesis.

### Priority donor/parent embeddings

- Delegation Logic / trust management;
- SecPAL;
- authorization logics including NAL/belief semantics/flow-limited authorization;
- deontic/input-output/action logics;
- ETAS;
- FAVA;
- Policy Cards/user-permission systems;
- AgentAbstain;
- ProvenanceGuard/execution provenance;
- Agent-Sentry;
- information-flow/non-interference systems;
- ORION-11–ORION-15 native gates.

### Existing deterministic artifact
`checkers/p8_finite_falsifiers_v1.py` — current bounded sanity pass: **7/7 PASS**.

### Next proof/engineering artifacts

- exact ORION-11–ORION-15 decision fixtures;
- ETAS/FAVA-style donor fixtures;
- cross-domain laundering dataset with matched valid-coercion controls;
- temporal/epoch and revocation exhaustive cases;
- proof assistant target for anti-laundering or revocation theorem after rule freeze;
- protected cross-capability evaluation from #341/#353.

## 8. Cross-paper theorem programme

The width pass suggests several common statements that may become lemmas, synthesis results or reasons to merge papers rather than force separation.

### G1 — Donor-faithful conservative extension
Adding ORION dimensions that are inert on a donor's native problem must not change that donor's native verdict.

### G2 — Dependency invalidation skeleton
ORION-16 state reopening, ORION-17 closure reopening and ORION-18 authority revocation all use a dependency-closure skeleton but have different semantic terminals. Investigate a common theorem parameterized by domain-specific validity semantics.

### G3 — Evidence/authority non-fungibility
Content-bound evidence or authority from one semantic/action domain is not automatically substitutable for a hard premise in another domain.

### G4 — History-sensitive equivalence
Current-state equivalence does not imply history equivalence. Later policy may legitimately depend on chronology, issuer identity, provenance or revocation lineage.

### G5 — Width with negative controls
A more expressive formalism must not automatically dominate: on tasks where simple fixed-chart navigation, local gates or full/simple repair suffice, ORION should avoid unnecessary reframing, refusal and reopening.

## 9. Literature and novelty obligations

The programme must explicitly disposition, not merely cite:

- dynamic epistemic/action logics and belief change;
- AGM/iterated revision and belief-base formalisms;
- TMS/ATMS/dependency-directed repair;
- process/separation/event/temporal/effect systems;
- provenance/audit/accountability;
- planning abstraction, representation languages and representation learning;
- graph navigation, exploratory search, information foraging and POMDP information acquisition;
- goal/objective revision/evolution and world-model adaptation;
- deontic/input-output/action/authorization/trust-management logics;
- delegation, revocation, non-interference and information-flow control;
- abstention/selective prediction, provenance guardrails, runtime shielding and agent permission systems;
- current language-agent architecture and repair work.

After each `ADOPT`, `ADAPT` or `COMPOSE`, recompute the surviving theorem/benchmark residual. A larger bibliography is not evidence of a larger contribution.

## 10. Current completed artifacts in this pass

- [x] widened donor-assimilation programme opened as #352;
- [x] cross-domain width/transfer programme opened as #353;
- [x] `DONOR_ASSIMILATION_MATRIX_2026-08-17.md`;
- [x] `PARENT_FIELD_PRESSURE_MAP_2026-08-17.md`;
- [x] `P1_P5_OWNERSHIP_MATRIX_V1.md`;
- [x] ORION-16/ORION-17/ORION-18 formal cores widened;
- [x] ORION-16 history-aware commutation theorem repaired;
- [x] ORION-17 stopping-impossibility premise repaired;
- [x] ORION-18 cross-domain formal core expanded;
- [x] first deterministic ORION-16/ORION-17/ORION-18 finite falsifier scripts committed;
- [x] current bounded runs: ORION-16 5/5, ORION-17 7/7, ORION-18 7/7;
- [x] ORION-16/ORION-17/ORION-18 Markdown manuscripts rewritten around the wider donor-faithful objects.

These completions do **not** close novelty or empirical gates.

## 11. Remaining completion order

1. Finish the broad parent-field/donor saturation until two consecutive passes yield no material change to the formal objects.
2. Implement conservative donor + ORION-11–ORION-15 embedding fixtures.
3. Upgrade hand fixtures to exhaustive bounded generators/model checks.
4. Formalize one high-value theorem per surviving candidate in a proof assistant if feasible.
5. Freeze #353 cross-domain transfer benchmarks and strongest donor baselines prospectively.
6. Execute protected/fresh evaluations; route positives through #283.
7. Complete sentence-level claim ledgers #346 and final overlap dispositions #343.
8. Convert surviving candidates into LaTeX journal packages with verified bibliographies.
9. Run final literature refresh #344 and venue gate #345.
10. Promote only a candidate whose independent paper-level residual still survives.

## 12. Current authority

All three papers remain candidates and all external novelty/superiority terminals remain `CANNOT_CHECK`. The work completed so far strengthens the formal objects and falsification programme; it does not authorize promotion to Papers VI–VIII.