# EA-1A analytic closure V1 — exact revision is sufficient when the intervention is explicit

**Date:** 2026-08-23  
**Parent protocol:** `EA1_CAUSAL_BELIEF_SURGERY_PROTOCOL_V1.md`  
**Terminal:** `EA1_DONOR_EXACT_REVISION_SUFFICIENT`  
**Status:** scientific closure for the registered EA-1A learned-value question; exact substrate remains useful for later tests.

## 1. Why this closure exists before model training

The frozen EA-1A protocol gives the full-state arm:

```text
(E_t, I_t)
```

where:

- `E_t` contains every load-bearing V0 coordinate, including dependency types, failure scope, obligation scope and representation semantic key;
- `I_t` explicitly names the primitive intervention kind (`RETRACT`, `ACTIVATE`, `MARK_UNKNOWN`, or `CHANGE_REPRESENTATION`) and its target/new representation;
- the V0 revision rules are deterministic.

The exact evaluator kernel therefore defines a total deterministic function over every registered valid EA-1A case:

```text
K : (E_t, I_t) -> (E_{t+1}, ΔE_t*)
```

The gold delta is not an independently learned latent object once `(E_t, I_t)` is fully supplied. It is the output of `K`.

## 2. Proposition — exact-kernel sufficiency at the full V0 view

For every registered EA-1A exact case `c` satisfying the V0 invariants,

```text
Δ*(c) = K(E(c), I(c)).delta
```

and applying that delta reconstructs the exact post-state:

```text
Apply(E(c), Δ*(c)) = K(E(c), I(c)).post_state.
```

Therefore an exact implementation of `K` achieves:

- delta-operation F1 = `1.0`;
- exact delta match = `1.0`;
- exact post-state reconstruction = `1.0`;
- descendant retraction/preservation = exact under the registered rules;
- false/missed reopen = `0`;
- obligation laundering = `0`;
- UNKNOWN/refutation confusion = `0`.

No learned model can strictly exceed these metrics on the same registered semantics and information.

This is not a statistical claim and requires no protected model outcome.

## 3. Relation to the protocol baseline ladder

The frozen protocol already required:

> If B5/B6/B7 reaches the exact ceiling with no learned residual, terminal `EA1_DONOR_EXACT_REVISION_SUFFICIENT`; do not add a native model.

B5 is `typed serialization + exact kernel`.

Because the protocol exposes `I_t` directly rather than asking a model to infer its epistemic meaning, B5 is not merely *expected* to reach the ceiling: the task definition makes it analytically identical to the evaluator computation.

Thus the stop rule fires **before** B8/B9 execution.

## 4. What EA-1A still establishes

This negative closure does not make the exact substrate useless.

EA-1A remains a valid evaluator/information study for:

1. exact causal state-surgery semantics;
2. over-retraction vs independent-support preservation;
3. `UNKNOWN` vs refutation;
4. material representation change vs identity remint;
5. scoped failure reopening;
6. obligation transportability;
7. hostile view collisions showing which coordinates are load-bearing;
8. cross-domain quantum state-revision test construction.

The exact kernel should therefore remain as **referee/oracle infrastructure**, not be replaced by a neural approximation.

## 5. Root-cause diagnosis

The closed learned-value question failed for a principled reason:

`EXACT_KERNEL_SUFFICIENT / TARGET_IS_DETERMINISTIC_CONSEQUENCE_OF_VISIBLE_STATE`.

It did **not** fail because:

- typed epistemic state is meaningless;
- state revision is unimportant;
- LLMs cannot learn updates;
- native state cannot ever help;
- scoped failure/obligation interactions are donor-complete in every setting.

The benchmark placed the only nontrivial semantic choice — **what epistemic event actually occurred** — inside the supplied intervention object. Once that choice is given, propagation is classical.

## 6. Consequence for ORION-EA architecture research

EA must preserve the P9 doctrine:

> **Do not train a neural model to rediscover a deterministic state transition that an exact algorithm already computes from the same visible information.**

A legitimate successor must move the learned residual to a coordinate the exact kernel does not already receive as gold-equivalent input.

The next candidate object is therefore:

```text
(E_t, raw/source-grounded observation O_t)
        -> proposed primary epistemic interpretation / delta seed
        -> exact kernel propagation
```

rather than:

```text
(E_t, already-typed intervention I_t)
        -> learn deterministic propagation
```

## 7. Successor ownership boundary

Even that successor is heavily donor-pressured:

- Grounded Continuation already learns a bounded update interpretation before symbolic propagation;
- Kumiho/StateMem already provide structured state;
- DGRR already provides dependency-guided repair;
- State Commitment Learning already trains persistent-state sufficiency;
- scientific extraction/grounding systems already map text to structured records.

So the successor may survive only if it tests a bounded residual such as:

- multi-coordinate typed delta grounding rather than a small update class;
- scoped failure + representation + obligation interactions;
- whole-domain / semantic-remint transfer;
- native-vs-serialized causal state use under matched information;
- protected observation semantics where the correct delta cannot be recovered from surface/template identity.

A new protocol must be frozen before any outcome-bearing execution.

## 8. Scientific terminal

`EA1_DONOR_EXACT_REVISION_SUFFICIENT`

This is a **successful negative scientific result**: it prevents unnecessary model training and narrows ORION-EA to the actual learning problem.

It does not close #957. It closes only the registered EA-1A claim that a learner should add value when the exact intervention and full state are already supplied.
