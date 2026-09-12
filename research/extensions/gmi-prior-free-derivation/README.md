# GMI prior-free derivation lane

## Authority and status

This directory contains the current prior-free GMI formalization programme. The authoritative theorem package is `FORMAL_CORE_V3.md` together with the explicitly cited companion notes and executable hostile witnesses below.

`FORMAL_CORE_V1.md` and `FORMAL_CORE_V2.md` are retained as provenance. They are superseded wherever v3 or a later companion note changes a definition, theorem, proof obligation, or claim boundary. They must not be cited as current authority without checking the v3 status.

The programme currently claims **formal framework closure at the declared classical causal-computable level for the stated theorems**, plus architecture-form representation coverage. It does **not** claim full empirical GMI closure, unique named-architecture derivation, prospective unknown-form prediction, complete physical phase-diagram closure, or quantum-interface closure.

## Current theorem stack

### 1. Formal core

- `FORMAL_CORE_V3.md` — authoritative definitions and theorem package.
- `HOSTILE_AUDIT_V1.md` — counterexamples that broke overstrong v1 statements and the repairs required before v2/v3.

The v3 core separates:

1. predictive residual equivalence;
2. immediate control compatibility;
3. rooted-plan compatibility;
4. autonomous dynamic controller state;
5. operational morphology;
6. physical/resource feasibility;
7. developmental reachability.

No theorem may silently promote closure at one layer into closure at the next.

### 2. Control and information

- `CONTROL_INFORMATION_PROFILE_V2.md` — distinct tolerance-indexed information profiles for repeated action disclosure and one-time rooted-plan selection.
- `DYNAMIC_CONTROLLER_CLOSED_COVER_V2.md` — finite autonomous-controller realization via compatible closed covers; donor-aligned with incompletely specified FSM minimization.
- `ROOTED_STRATEGY_COMPLEXITY_V1.md` — prefix-blind rooted-strategy semantics and the hierarchy
  \[
  \chi_{\mathrm{act}}(\varepsilon)
  \le
  \chi_{\mathrm{plan}}(\varepsilon)
  \le
  N^*_{\mathrm{dyn}}(\varepsilon).
  \]
- `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json` — frozen finite witnesses showing both inequalities can be strict.

The machine boundary is part of the theorem statement. Moving memory or computation into an external encoder, clock, retrieval service, tool, or environment channel changes the resource model rather than reducing intrinsic demand for free.

### 3. Channel laws

- `CHANNEL_LAW_RECOVERY_V1.md` — derives the registered one-channel and two-channel capability laws from explicit coverage/reveal assumptions, while separating stochasticity internal to one environment from a prior over environments.

These are architecture-free conditional capability laws, not claims that every ecology has the same channel model.

### 4. Morphology and architecture neutrality

- `REDUCTION_VOCABULARY_V1.md` — frozen architecture-neutral R0–R8 reduction vocabulary.
- `KNOWN_FORM_REDUCTION_V1.md` — reduction of 26 known machine-intelligence form families using that vocabulary.
- `FORMAL_CORE_V3.md` — necessity/construction sandwich for morphology closure and the distinction between profile-frontier closure and morphology-fiber identification.

Coverage means a form maps into the vocabulary. Recovery means its region is derived without using its label. Prospective prediction means an unoccupied region is frozen before a realization is known. Only the latter two are strong architecture-prediction evidence.

### 5. Executable hostile witnesses

- `finite_hostile_checks_v1.py`
- `FINITE_HOSTILE_CHECKS_RESULTS_V1.json`
- `CONTROL_COMPLEXITY_HIERARCHY_RESULTS_V1.json`

The finite hostile checks cover at least the following failure classes:

- scalarization missing improvements on prior-null environments;
- false finite-alphabet cut claims for stochastic channels;
- predictive equivalence being confused with control mergeability;
- reachable/global frontier intersection being confused with the best reachable frontier;
- zero-error conflict coloring;
- strict separation between repeated action information, rooted-plan information, and autonomous state complexity.

## The formal target

For declared causal structure `C`, obligation `Omega`, ecology `E`, physical/resource specification `P`, and operational probe/gauge specification `G`, the programme seeks a derivation of the form

\[
(C,\Omega,\mathcal E,P,G)
\Longrightarrow
\text{predictive/control residual structure}
\Longrightarrow
\text{necessary information and control bounds}
\Longrightarrow
\text{constructive realizations}
\Longrightarrow
\text{certified morphology/profile frontier regions}.
\]

A prior over `E` is not required to define the pointwise dominance order or the robust residual/control objects. Priors may be introduced later as optional scalarizers or selectors, with their support assumptions stated explicitly.

## Closure rule

A morphology region is **not closed merely because a feasible set or Pareto frontier has been defined**.

For a declared region, maintain:

- a proved outer set of all possible realizations from necessity theorems;
- an explicit inner set generated by constructions;
- the unknown physical set between them.

Closure requires the constructive envelope to meet the necessary envelope at the claim level being asserted. If only performance/resource profiles meet, then profile-frontier closure is justified; morphology identity additionally requires a fiber-identification theorem.

This rule prevents universal computability, expressive equivalence, or an abstract feasibility definition from being misreported as a physical morphology theorem.

## Claim ladder

The lane uses the following claim order:

1. **definition** — object is well typed;
2. **finite witness** — registered counterexample or construction;
3. **finite-domain closure** — exhaustive declared finite domain;
4. **theorem** — quantified statement under explicit assumptions;
5. **representation coverage** — known/future form maps into the invariant language;
6. **held-out recovery** — morphology region derived without architecture label leakage;
7. **prospective prediction** — unoccupied region frozen before discovery;
8. **physical closure** — necessity and construction envelopes meet under a substrate model;
9. **developmental closure** — a declared search/development process reaches the region under proved or measured bounds.

Higher labels must not be inferred from lower ones.

## Current open obligations

The programme remains open on:

- held-out architecture recovery under a frozen reduction vocabulary;
- a preregistered prospective morphology prediction;
- substrate-specific necessity/construction equality for nontrivial morphology regions;
- a complete characterization of dynamic controller complexity beyond finite closed-cover specializations;
- developmental/search-law neutrality and reachability bounds;
- quantum-input/output generalization using instruments/channels rather than classical histories alone.

## Review discipline

When modifying this lane:

1. state quantifiers before theorem prose;
2. state the machine/composition boundary;
3. distinguish structural environment parameters from a probability measure over environments;
4. identify donor-owned special cases;
5. construct a hostile countermodel for every removed assumption where possible;
6. preserve negative results;
7. do not convert representation coverage into recovery or prediction;
8. do not convert an outer-bound definition into a closed phase law;
9. prefer additive successor notes or a new numbered core over silently rewriting historical evidence.
