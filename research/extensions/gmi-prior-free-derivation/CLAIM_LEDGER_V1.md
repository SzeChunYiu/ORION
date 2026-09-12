# Prior-free GMI claim ledger v1

## Status vocabulary

- **THEOREM** — proved under explicitly stated assumptions.
- **FINITE EXACT** — exhaustively established on a declared finite object/domain.
- **CONSTRUCTIVE** — explicit realization exists; no optimality claim unless paired with a lower bound.
- **COVERAGE** — object maps into the frozen representation vocabulary.
- **DONOR SPECIALIZATION** — theorem/mechanism is inherited from prior theory and specialized to the GMI setting.
- **OPEN** — a named proof, construction, recovery, or empirical obligation remains.
- **REFUTED / REPAIRED** — an earlier stronger statement has a registered counterexample and must not be revived without new assumptions.

This ledger controls claim strength for the files in this directory. Historical notes may contain stronger language; the rows below are authoritative unless superseded by a later ledger.

---

## A. Foundations

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| F1 | A nontrivial action ordering cannot be derived without an obligation/preference structure or an equivalent discriminator. | THEOREM by deletion countermodel | At least two admissible actions/outcomes. | `FORMAL_CORE_V3.md` minimal-premise section. | A formulation deriving preference from strictly weaker premises without smuggling in an order. |
| F2 | A nontrivial universally preferred learner/machine cannot be selected over an unrestricted ecology by pointwise dominance alone. | THEOREM / boundary | Ecology includes mutually adversarial/opposite-action worlds. | `FORMAL_CORE_V3.md`; standard NFL/decision-theoretic boundary. | A declared restriction on ecology changes the quantifiers. |
| F3 | A prior over admissible environments is not required to define pointwise dominance or robust worst-case residual/control objects. | THEOREM / definition-level closure | Risk/performance is defined pointwise for each admitted environment. | `FORMAL_CORE_V3.md`. | A later theorem silently integrates over environments without declaring a measure. |
| F4 | Bayesian/probabilistic scalarizations may select points on the prior-free order but are not the foundational definition of that order. | THEOREM with support qualifications | Scalarization weights and environment measure declared. | `FORMAL_CORE_V3.md`, repaired after `HOSTILE_AUDIT_V1.md`. | Claim that every nondominated point is Bayes-supported without convexity/closure conditions. |
| F5 | Strict pointwise improvement need not become strict expected improvement if it occurs only on a prior-null environment. | FINITE EXACT counterexample | Two or more environments; measure with null support on strict coordinate. | `finite_hostile_checks_v1.py`, `FINITE_HOSTILE_CHECKS_RESULTS_V1.json`. | None unless expected-risk theorem adds support assumptions. |

---

## B. Predictive state

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| P1 | Histories with identical rooted, action-conditional future obligation-relevant response laws under all admitted environments define a predictive residual equivalence relation. | THEOREM / construction | Rooted continuation strategies are prefix-blind except for declared side information. | `FORMAL_CORE_V3.md`, `ROOTED_STRATEGY_COMPLEXITY_V1.md`. | A counterexample to equivalence or to well-defined quotient transition under declared semantics. |
| P2 | The quotient by predictive residual equivalence is the coarsest exact predictive-response representation up to reachable-state isomorphism. | THEOREM | Exact response preservation; declared ecology and rooted intervention class. | `FORMAL_CORE_V3.md`; donor-aligned with predictive-state/causal-state ideas. | Generalization to weaker task-specific control state must not be conflated with P2. |
| P3 | Predictive equivalence is generally stronger than control mergeability. | FINITE EXACT + theorem boundary | Multiple continuations/actions may satisfy the same obligation. | `HOSTILE_AUDIT_V1.md`, finite witnesses. | A restricted domain where optimal/acceptable continuation is unique. |

---

## C. Control complexity

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| C1 | Immediate-action compatibility need not form an equivalence relation and therefore need not define a canonical quotient. | THEOREM / finite witnesses | Incompletely specified control: multiple actions may be admissible. | `FORMAL_CORE_V3.md`, `DYNAMIC_CONTROLLER_CLOSED_COVER_V2.md`. | Domain restricted to complete deterministic outputs. |
| C2 | A plan-compatible class must share one rooted prefix-blind continuation strategy; a policy that can inspect the forgotten root leaks state and invalidates the compression claim. | THEOREM / semantic repair | Root identity absent from downstream side information. | `ROOTED_STRATEGY_COMPLEXITY_V1.md`. | Root identity is explicitly included in machine boundary/side information. |
| C3 | For aligned finite residual semantics, \(\chi_{act}(\varepsilon) \le \chi_{plan}(\varepsilon) \le N^*_{dyn}(\varepsilon)\). | THEOREM | Finite residual specification; aligned tolerance and machine boundary. | `ROOTED_STRATEGY_COMPLEXITY_V1.md`. | Stochastic controllers or variable-length coding require separately stated generalization. |
| C4 | Both inequalities in C3 can be strict. | FINITE EXACT | Registered finite deterministic examples. | `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json`. | Stronger restrictions collapse the hierarchy. |
| C5 | Minimum autonomous deterministic controller state for a finite incompletely specified residual machine is a compatible closed-cover problem, not merely a coloring problem. | DONOR SPECIALIZATION + theorem | Finite residual machine; local admissibility Markovized; clock/side information declared. | `DYNAMIC_CONTROLLER_CLOSED_COVER_V2.md`; classical ISFSM minimization donor. | Generalization beyond finite deterministic controllers. |
| C6 | A finite signal alphabet of size \(|Y|\) does not by itself limit stochastic-channel information to \(\log_2|Y|\) in the naive deterministic pigeonhole sense used by v1. | REFUTED / REPAIRED | Stochastic encoders/channels allowed. | `HOSTILE_AUDIT_V1.md`, finite witness. | A theorem adds zero-error/deterministic support-separation conditions. |
| C7 | Zero-error control conflict induces a valid coloring lower bound on required distinguishable messages/states under the declared communication model. | THEOREM / FINITE EXACT witness | Zero-error, declared machine boundary, conflict relation defined on residual control demands. | `FORMAL_CORE_V3.md`, finite hostile checks. | Approximate-error claims require separate coding bounds. |

---

## D. Channel capability laws

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| L1 | The one-channel law \(\mathrm{acc}\le 1/2+r/(2L)\) follows when a uniformly located decisive item is perfectly resolved on primary-channel hit and unrevealed misses permit no advantage over chance. | THEOREM, conditional | Frozen coverage model; stochasticity belongs to structural environment/input generation, not to a prior over model classes. | `CHANNEL_LAW_RECOVERY_V1.md`. | Different miss information or nonuniform decisive-location model. |
| L2 | The two-channel law \(\mathrm{acc}\le 1-(1-r/L)(1-p)/2\) follows when a secondary channel independently reveals a primary miss with probability \(p\) and residual misses remain chance-limited. | THEOREM, conditional | Same as L1 plus stated secondary reveal semantics. | `CHANNEL_LAW_RECOVERY_V1.md`. | Dependence/interaction between channels or informative residual misses. |
| L3 | L1/L2 are architecture-free capability laws, not universal laws for all intelligence tasks. | BOUNDARY | Only declared coverage/reveal ecology. | `CHANNEL_LAW_RECOVERY_V1.md`. | None; any extension needs new assumptions. |

---

## E. Operational morphology

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| M1 | Named architecture syntax is not identifiable from premises invariant under the declared operational probe/gauge equivalence. | THEOREM | Premises descend to the operational quotient. | `FORMAL_CORE_V3.md`. | Premises include additional operationally meaningful distinctions. |
| M2 | Resource/machine-boundary changes can change morphology without changing task semantics. | THEOREM / construction boundary | Resource evaluator and composition boundary are explicit. | `FORMAL_CORE_V3.md`, reduction vocabulary. | None; this is part of morphology definition. |
| M3 | Universal behavioural simulability does not imply equal time/memory/energy/communication morphology. | THEOREM boundary | Universal simulation may have overhead. | `FORMAL_CORE_V3.md`. | A substrate-specific overhead equivalence theorem. |
| M4 | A defined feasible set or Pareto frontier is not by itself a derived physical phase law. | THEOREM methodological boundary | Physical realizability is not assumed known. | `FORMAL_CORE_V3.md`. | None. |
| M5 | Let constructive inner realizations lie inside the true physical set, itself inside a proved necessary outer set. If a constructive antichain dominates the entire necessary outer envelope at the declared profile level, the true profile frontier is certified there. | THEOREM | Correct inner/outer inclusions; same profile order. | `FORMAL_CORE_V3.md` necessity-construction sandwich. | Failure of either inclusion or unmodeled resource coordinate. |
| M6 | Profile-frontier closure does not imply unique morphology; exact morphology requires a fiber-identification theorem over the optimal profile. | THEOREM | Operational signature map may be many-to-one in profile coordinates. | `FORMAL_CORE_V3.md`. | Fiber proven singleton modulo gauge. |

---

## F. Known-form coverage and prediction

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| K1 | The frozen R0--R8 vocabulary maps the registered 26 known machine-intelligence form families without requiring a new classical primitive. | COVERAGE | Classical causal-computable external interface; genuinely quantum I/O explicitly outside scope. | `REDUCTION_VOCABULARY_V1.md`, `KNOWN_FORM_REDUCTION_V1.md`. | A form cannot be represented without extending the vocabulary. |
| K2 | K1 is not held-out recovery because the major known forms were historically visible during vocabulary construction. | THEOREM about evidence status | Historical exposure. | `RECOVERY_AND_PROSPECTIVE_TEST_PROTOCOL_V1.md`. | Never upgraded retroactively; only successor blind tests can strengthen evidence. |
| K3 | A valid recovery claim requires a frozen theory/problem/derivation bundle and an architecture-neutral predicted region before reveal. | PROTOCOL | See recovery protocol. | `RECOVERY_AND_PROSPECTIVE_TEST_PROTOCOL_V1.md`. | Protocol revision must create a successor version. |
| K4 | No time-held-out architecture recovery has yet been registered under this lane. | OPEN | R2 protocol. | Current ledger. | First valid R2 run. |
| K5 | No prospective empty-region prediction followed by later realization has yet been registered under this lane. | OPEN | R3 protocol. | Current ledger. | First valid R3 run. |

---

## G. Development and search

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| D1 | The globally optimal physical frontier and the best frontier reachable within a development budget are different objects. | THEOREM / finite witness | Explicit developmental process and budget. | `FORMAL_CORE_V3.md`, finite hostile checks. | None. |
| D2 | Intersecting the global frontier with a reachable set does not generally equal the nondominated set within the reachable set. | FINITE EXACT counterexample | Multiobjective/ordered profile setting. | `HOSTILE_AUDIT_V1.md`, finite witness. | Restricted cases may coincide and need proof. |
| D3 | A search/development law that distinguishes operationally equivalent implementations by syntax introduces a search prior. | THEOREM / definition-level neutrality test | Operational equivalence fixed first. | `FORMAL_CORE_V3.md`, recovery protocol. | An equivariance proof shows the distinction disappears at quotient level. |
| D4 | General developmental closure for GMI is not established. | OPEN | Nontrivial search laws and finite budgets. | Current ledger. | Reachability theorem or registered finite-budget bound. |

---

## H. Domain boundaries

| ID | Claim | Status | Domain / assumptions | Evidence / authority | Reopen trigger |
|---|---|---|---|---|---|
| B1 | Current theorem stack is classical at the external history/action/observation interface. | BOUNDARY | Classical stochastic kernels/transducers. | `FORMAL_CORE_V3.md`. | Quantum-instrument extension. |
| B2 | Genuinely quantum input/output channels are not covered merely by relabeling a quantum implementation as a classical stochastic transducer. | OPEN boundary | Quantum side information/coherent interaction may be operationally relevant. | `KNOWN_FORM_REDUCTION_V1.md`, current core non-claim. | Formal quantum-channel analogue. |
| B3 | Infinite/uncountable measurable spaces require regularity/measurability assumptions beyond finite examples. | OPEN generalization | Standard Borel/regular conditional probability conditions likely needed. | Formal core boundary. | Measurable-space theorem package. |
| B4 | Effectively samplable kernels are sufficient for the stated universal behavioural realization argument; generic lower-semicomputable or merely pointwise-computable descriptions require separate treatment. | THEOREM boundary | Effective sampler / precision procedure specified. | `FORMAL_CORE_V3.md`, hostile repair. | Stronger computability theorem. |

---

## Current terminal

The strongest justified summary is:

\[
\boxed{
\begin{array}{l}
\text{prior-free formal core: substantially hardened within declared domain;}\\
\text{predictive/control/resource layers: separated and theorem-gated;}\\
\text{known-form representation coverage: broad but retrospective;}\\
\text{prospective architecture prediction: OPEN;}\\
\text{nontrivial physical morphology phase closure: OPEN;}\\
\text{general developmental closure: OPEN.}
\end{array}
}
\]

No stronger terminal should be reported from this lane until the corresponding OPEN row is discharged by its registered gate.
