# Certificate Control Plane Theorems R9

**Date:** 2026-08-26  
**Status:** analytic application theorem note

This note formalizes the cross-paper `NORMALIZE -> IDENTIFY -> AUTHORIZE -> VERIFY` control plane. The result is a composition contract, not yet an empirical systems contribution.

# 1. Objects

Let `X` be a set of problem instances. For each `x in X`, let `Ans(x)` be the nonempty set of semantically correct outputs for the registered query. Let `Act` be a set of executable actions, and let `use(a,y)` mean that action `a` operationalizes output `y`.

A policy instance also contains an evidence graph `E` and a required authority coordinate `rho(a)` for each executable action.

## 1.1 Normalization layer

A normalizer returns `(x', c_N)` or fails closed. Its checker satisfies

`Check_N(x,x',c_N)=true  =>  Ans(x')=Ans(x)`.

The normalizer may additionally expose a support/search cap, but cap soundness is part of `Check_N`.

## 1.2 Identification layer

A representation `Phi` induces the fibre

`F(x')={z: Phi(z)=Phi(x')}`.

The identification layer returns one of:

- `EXACT(Y,c_I)`, where `Y` is a nonempty set of candidate outputs;
- `REFINE(r,c_I)`;
- `ROUTE(solver,c_I)`;
- `ABSTAIN(c_I)`.

Its checker satisfies

`Check_I(x',Y,c_I)=true  =>  union_{z in F(x')} Ans(z) subseteq Y`.

A fully automatic representation-only action is allowed only when `Y` is a singleton. A non-singleton `Y` may be exposed as an exact action set or interval, but it may not be silently collapsed to one element.

## 1.3 Authority layer

The typed authority evaluator returns `ALLOW(a,c_A)` or `DENY(a,c_A)`. Its checker satisfies

`Check_A(E,a,c_A)=true  =>  rho(a) in Lic_E(a)`.

Here `Lic_E` is the declared typed least fixed point after all registered refutations, merges, origins, and authorized bridges.

## 1.4 Verification layer

An exact solver or proposer returns `(y,c_V)`. Its independent checker satisfies

`Check_V(x',y,c_V)=true  =>  y in Ans(x')`.

The checker is independent of model confidence. An unverified model output is not an exact output.

# 2. Fail-closed pipeline

The pipeline may emit:

- `EXECUTE(a,y,C)`;
- `RETURN_SET(Y,C)`;
- `REFINE(r,C)`;
- `ROUTE(solver,C)`;
- `ABSTAIN(C)`;
- `DENY(a,C)`;
- `CANNOT_CHECK(C)`.

It emits `EXECUTE(a,y,C)` only when all of the following hold:

1. `Check_N(x,x',c_N)=true`;
2. either the identification layer certifies the singleton `{y}`, or an exact solver supplies `c_V` with `Check_V(x',y,c_V)=true`;
3. `use(a,y)`;
4. `Check_A(E,a,c_A)=true`;
5. every required certificate and input digest is present.

# 3. Composition theorem

## Theorem 1 — exact authorized execution

Assume all four checkers are sound and the pipeline follows the fail-closed rule. Then every emitted `EXECUTE(a,y,C)` satisfies:

1. `y in Ans(x)`;
2. the available representation either exactly identified `y` or the exact verifier established it;
3. `rho(a) in Lic_E(a)`;
4. the certificate bundle contains a checkable witness for each conclusion.

### Proof

From normalization soundness, `Ans(x')=Ans(x)`. If identification supplied a singleton `{y}`, its soundness gives `Ans(x') subseteq {y}`; because `Ans(x')` is nonempty, `y in Ans(x')`. Otherwise verification soundness directly gives `y in Ans(x')`. Therefore `y in Ans(x)`. Authority-checker soundness gives `rho(a) in Lic_E(a)`. The emission rule requires all certificates to be present, so the bundle witnesses each step. ∎

## Corollary 2 — exact ambiguity cannot become an unqualified action

If the visible representation fibre contains two instances with disjoint correct-output sets, a sound identification layer cannot authorize a representation-only singleton output. The pipeline must return a set/interval, refine, route, abstain, deny, or cannot-check.

## Corollary 3 — mathematically correct but unauthorized outputs do not execute

Even when `y in Ans(x)`, the pipeline cannot emit `EXECUTE(a,y,C)` unless the required typed authority coordinate reaches `a` after merge and retraction.

# 4. Independent necessity of the four layers

## Theorem 4 — layer-separation witnesses

For each layer `L` among `NORMALIZE`, `IDENTIFY`, `AUTHORIZE`, and `VERIFY`, there exists a finite instance in which the other three layers are sound but deleting `L` permits an invalid `EXECUTE` event.

### Normalization witness

Let a claimed search cap exclude the unique optimum because an unregistered cross move invalidates the abstract normal form. Identification sees a singleton in the truncated search state, authority permits the action, and verification checks only the truncated problem. Without a sound normalization/equivalence certificate, the executed output is not in `Ans(x)`.

### Identification witness

Take two instances in one representation fibre with different unique outputs. Let the predictor select one endpoint with high confidence. Normalization is the identity, authority permits the action, and the chosen output can be verified only for one endpoint. If verification is deferred until after an irreversible action or is scoped to a predicted surrogate, omitting the exact identification gate permits the wrong endpoint action. Under the full pipeline, the non-singleton fibre forces refinement, routing, or abstention.

### Authority witness

Let the solver return and verify the mathematically correct output, but let the action require a prospective or jurisdictional coordinate absent from every valid proof path. Normalization and identification are exact. Without the authority gate, a correct answer triggers an unauthorized action.

### Verification witness

Let normalization be sound, the representation identify a singleton predicted output, and authority permit the action, but let the implementation or model serialize the wrong value. Without an independent exact checker, the wrong output executes.

Each construction is finite and can be implemented as a hostile unit fixture. ∎

# 5. Monotonicity and information flow

## Proposition 5 — representation refinement

If `Psi` refines `Phi`, then every `Psi`-fibre is contained in a `Phi`-fibre. Hence the exact candidate-output set and scalar fibre diameter cannot increase after refinement.

## Proposition 6 — authority retraction

Adding direct refutations or removing seed/cap coordinates cannot enlarge any typed license set in the positive calculus.

## Proposition 7 — safe intervention direction

Under Propositions 5 and 6, additional representation information may change `ABSTAIN/ROUTE/RETURN_SET` into `EXACT`, whereas additional refutation may change `ALLOW` into `DENY`; the converse changes require an explicit new feature, seed, cap, or authorized bridge. The two monotonicities are distinct and must not be conflated.

# 6. Certificate bundle

A minimal execution bundle contains:

- instance and representation digests;
- move-registry digest;
- normalization certificate and checker version;
- fibre/refinement certificate or exact-solver route record;
- typed authority proof, policy digest, refutation epoch, and origin/bridge record;
- exact result proof and checker version;
- action, destination, and outcome receipt.

The bundle is a product of separately owned certificates. Composition does not transfer theorem, novelty, or external-validation authority among the component papers.

# 7. Experimental consequences

Theorem 4 determines the mandatory ablations for issue #1411. Every component ablation must include its separation witness, and the full system must attribute each prevented failure to the layer whose certificate rejected it.

A top-tier systems claim additionally requires:

- at least two external task families;
- matched model/tool/compute budgets;
- strong component and current-system baselines;
- quantitative route/cost/overhead results;
- external or structurally independent replay;
- current-source subtraction.

# 8. Authority

`CERTIFICATE_CONTROL_PLANE_COMPOSITION_PROVED__EMPIRICAL_CROSS_DOMAIN_VALUE_OPEN`
