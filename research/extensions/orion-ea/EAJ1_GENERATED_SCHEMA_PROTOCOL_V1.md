# EAJ-1 Generated Coordinate / Schema Synthesis — protocol V1

**Status:** FROZEN BEFORE LEARNED-PROPOSER OUTCOMES  
**Parent:** #963  
**Preconditions:** `EAJ_FINITE_MENU_CLASS_CLOSED`, `EAJ0_BOUNDED_RESIDUAL_SURVIVES__HIGH_RISK`.

## 1. Narrow scientific question

Can a learned proposer synthesize a **new executable epistemic coordinate program** from source-grounded counterexamples when the current state schema is exactly non-identifying, and does that program retain value on fresh held-out tasks beyond strong symbolic/program/library-learning baselines under the same meta-language and verifier budget?

The first study intentionally tests only **proposal value**. The downstream state compiler, program interpreter and task verifier are exact.

## 2. Why the target is a generated program, not a candidate id

`EAJ_FINITE_MENU_CLASS_CLOSED` proves that choosing from a fully enumerable finite schema-edit menu cannot yield higher solve rate than exhaustive verification.

EAJ-1 therefore uses a typed expression meta-language whose bounded candidate count is much larger than the frozen verifier-call budget. A proposer emits an AST/program; candidates are not supplied as a list.

This does not make learned proposal automatically novel. Program synthesis/CEGIS/evolutionary search receives the same language and budget.

## 3. Old epistemic schema `R0`

Each exact world contains evaluator-owned raw observations `O` and a model/downstream visible compiled state `S0 = Compile_R0(O)`.

`R0` exposes:

- object identities only as opaque per-world symbols;
- a frozen set of primitive unary/binary observable facts;
- no derived coordinate from the EAJ meta-language;
- no target/gold/family identifier.

For every positive family, the evaluator constructs at least one hostile pair:

```text
Compile_R0(O_a) == Compile_R0(O_b)
Target(O_a) != Target(O_b)
```

This collision is the exact old-schema insufficiency witness. The claim is only that the **compiled state interface** is non-identifying; a raw-observation oracle is not declared incapable.

## 4. Candidate new schema

A valid edit adds one derived coordinate:

```text
z := p(O)
```

where `p` is a typed AST from `SchemaExpr.v0`.

The new compiler is:

```text
Compile_R1(O) = (Compile_R0(O), z=p(O)).
```

The frozen downstream solver consumes `R1` but is not retrained per candidate. Candidate value therefore comes from the schema coordinate, not a changed downstream model.

## 5. `SchemaExpr.v0` meta-language

Start deliberately small but combinatorial. All operators have exact executable semantics.

### Types

```text
Bool
Int
Entity
Set[Entity]
```

### Terminals

- declared primitive observable booleans/integers;
- entity-role variables;
- finite entity sets supplied by the world;
- small integer constants from a frozen set independent of protected targets.

### Boolean operators

```text
NOT(x)
AND(x,y)
OR(x,y)
XOR(x,y)
EQ(x,y)
LT(x,y)
LE(x,y)
```

### Integer/set operators

```text
COUNT(set)
ADD(x,y)
SUB(x,y)
MOD(x,k)
```

### Quantification / relational lifting

```text
EXISTS(entity, predicate)
FORALL(entity, predicate)
COUNT_WHERE(entity, predicate)
```

### Composition

Programs may call previously declared base observable predicates but may not call evaluator target/gold or protected test functions.

The final candidate coordinate must evaluate to `Bool` or a bounded categorical `Int` for V1.

## 6. Complexity / search budget

Freeze before execution:

- maximum AST cost `L`;
- cost per operator/terminal;
- maximum verifier calls `B_v`;
- wall-clock/CPU budget for symbolic/evolutionary baselines;
- LLM token/call budget;
- same permitted raw observations for all proposers.

Before protected outcomes, mechanically count or lower-bound the number of syntactically well-typed ASTs at cost `<=L` and require:

```text
candidate_count(L) > B_v
```

by a large declared factor.

This only escapes **complete** enumeration; it does not weaken program-synthesis baselines.

## 7. Atomic exact families

V1 includes at least three families so a proposer cannot memorize one operator class.

### G1 — relational interaction

The old state contains object-local facts but collapses two worlds whose target differs by a generated relation over two or more observations.

Protected variants randomize object ids and primitive predicate names.

### G2 — parity / invariant coordinate

The target depends on a global invariant such as parity/modular count derived from a varying-size set. The old schema retains local facts in a form that does not expose the invariant to the frozen downstream interface.

Fresh tests extrapolate entity count beyond origin examples.

### G3 — higher-order interaction

Every registered unary/pairwise summary in `R0` matches across a hostile pair, while a three-way/global combination changes the target. Candidate must synthesize a coordinate from the raw allowed observations; hypergraph/higher-order feature baselines are mandatory.

## 8. No-Jump / fake-Jump controls

### N1 — old schema sufficient

`R0` already identifies the target. Any added coordinate is unnecessary. Correct proposer terminal is `NO_SCHEMA_EDIT`.

### N2 — lexical remint

Surface/primitive names change while semantics do not. A new schema must not be proposed merely because names are unfamiliar.

### N3 — definitional sugar

A candidate program is extensionally identical on the complete declared world class to an already exposed `R0` coordinate and adds no bounded reach.

### N4 — origin-only overfit

A short program fits proposal examples but fails the fresh held-out structural family.

### N5 — stronger-information laundering

Candidate references a primitive or statistic not in the allowed raw observation contract. Reject before scoring.

### N6 — unresolved equivalence

Two candidate coordinates remain indistinguishable on all admissible evidence and neither is licensed as uniquely correct. Correct terminal can remain `UNRESOLVED`.

## 9. Origin/fresh split — load-bearing

A schema edit does not earn positive credit solely by fitting the examples used to invent it.

For each family:

1. **origin set** supplies insufficiency witnesses and proposal evidence;
2. candidate proposal is sealed;
3. origin examples are removed from utility scoring;
4. candidate is compiled on a disjoint fresh set with reminted identities and new structural sizes/combinations;
5. the same frozen downstream solver is evaluated.

The primary endpoint uses fresh tasks only.

## 10. Baselines

### B0 nulls

- `NO_SCHEMA_EDIT`;
- random well-typed AST;
- shortest AST prior;
- always-edit broken control.

### B1 symbolic enumeration/search

Typed enumerative search under the same `L` and verifier budget.

### B2 CEGIS / constraint synthesis

Counterexample-guided program synthesis where mapping is faithful.

### B3 evolutionary/grammar search

Search over `SchemaExpr.v0` programs under matched evaluator calls/compute.

### B4 library/abstraction learner

DreamCoder/Stitch/LILO/TheoryCoder-style reusable abstraction baseline where faithful implementation is possible. If official code is unavailable, label protocol adaptation honestly.

### B5 feature / representation construction

Generic nonlinear feature-construction or representation-learning baseline receiving the same raw observations and fresh split.

### B6 raw LLM program proposer

Frontier/current LLM given the same origin packet and AST grammar; emits executable schema program.

### B7 EAJ proposer

A learned proposer trained across disjoint prior schema-invention families/tasks. It receives no protected family outcome before freeze.

### B8 oracle coordinate

Evaluator gold program/coordinate for diagnostic ceiling only; never a runnable proposal baseline.

## 11. Candidate verification pipeline

For every proposed AST:

1. parse / type-check;
2. confirm allowed primitive-access contract;
3. compute AST cost;
4. execute on origin examples for diagnostic only;
5. test old-domain preservation/no-Jump controls;
6. seal candidate digest;
7. execute on fresh protected set;
8. compile `R1` states;
9. run frozen downstream solver;
10. record all failures/nulls.

The exact verifier cannot rewrite/repair the candidate AST for the proposer. A malformed candidate is a proposer failure.

## 12. Primary endpoints

Report a non-compensatory vector:

- **fresh valid schema-edit rate**;
- **fresh protected downstream solve/reach gain over R0**;
- **false-Jump rate on N1/N2/N3**;
- **origin-to-fresh transfer gap**;
- **stronger-information violation rate**;
- **candidate program cost**;
- **verifier/evaluator calls and compute**;
- **correct `UNRESOLVED` rate**.

A candidate cannot compensate an information/authority violation with higher solve rate.

## 13. Primary promotion rule

`EAJ_LEARNED_SCHEMA_PROPOSAL_INCREMENTAL_VALUE` requires all of:

1. old-schema collision/insufficiency certificates are valid for every positive item;
2. EAJ beats the strongest applicable program/library/feature baseline on the frozen fresh endpoint by the preregistered margin;
3. false-Jump rate stays below the frozen bound;
4. no stronger-information leakage;
5. effect survives complete identity/primitive-name reminting;
6. effect survives at least one structural-size/composition extrapolation;
7. exact verifier credits only candidate validity, not hidden repair;
8. independent rerun reproduces the promoted result.

If B1–B5 match EAJ, terminal is a donor-sufficiency result.

## 14. Hostile attacks

- grammar contains a single conspicuous operator matching each family;
- target family inferable from AST terminal names;
- protected primitive name leaks formula;
- EAJ gets more origin examples;
- program-synthesis baseline denied counterexamples available to EAJ;
- candidate-count claim ignores symmetry/dedup and exhaustive search is actually feasible;
- downstream solver secretly retrained after candidate proposal;
- fresh set differs only by seed, not structural composition;
- proposal examples directly reveal exact truth table over the full protected domain;
- evaluator silently simplifies/repairs candidate program;
- no-Jump controls omitted;
- only successful candidate attempts retained.

## 15. Scientific boundaries

A positive V1 result would establish only:

> under the frozen exact generated-program schema language and budgets, the learned proposer improves fresh schema-edit proposal utility over the tested donor-complete baselines.

It would not establish:

- general concept invention;
- scientific creativity;
- a new reasoning language for LLMs generally;
- a better quantum method;
- universal superiority over symbolic synthesis;
- self-authorized schema adoption.

## 16. Quantum handoff

Only after V1 produces a nontrivial proposal residual may the same proposer interface be tested on a frozen QG/ORION-Q missing-coordinate or noncanonical representation residual. The quantum owner defines semantics/gold and the EAJ proposer never sees protected continuation outcomes before candidate freeze.

## 17. Allowed terminals

- `EAJ_SYMBOLIC_OR_LIBRARY_SYNTHESIS_SUFFICIENT`;
- `EAJ_FEATURE_CONSTRUCTION_SUFFICIENT`;
- `EAJ_LEARNED_SCHEMA_PROPOSAL_INCREMENTAL_VALUE`;
- `EAJ_ORIGIN_OVERFIT_NO_FRESH_VALUE`;
- `EAJ_FALSE_JUMP_FAILURE`;
- `EAJ_INVALID_BENCHMARK`;
- `CANNOT_CHECK`.
