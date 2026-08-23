# EA-1 information-sufficiency closure V1

**Date:** 2026-08-23  
**Scope:** exact finite hostile-pair information result only.  
**Terminal:** `EA1_TYPED_SCOPE_COORDINATES_LOAD_BEARING__FULL_V0_IDENTIFIES`.

## Question

Before asking whether any learned architecture is useful, are the V0 coordinates introduced specifically for ORION-EA revision — representation semantic identity, failure scope/reopen semantics and obligation transportability — actually load-bearing for the target state transition?

The answer on the frozen exact hostile pairs is **yes**.

## Exact method

Two pair generators hold the weaker `TYPED` model payload fixed while changing one evaluator-defined load-bearing coordinate:

1. **representation hostile pair** — the same old state and same new representation occurrence id are presented, but one case is a pure remint with unchanged semantic key while the other is a material semantic representation change;
2. **obligation hostile pair** — the same typed nodes/edges/representation transition are presented, but one obligation is nontransportable while the other is transportable.

The `TYPED` view hides:

- representation semantic key;
- failure scopes;
- obligation scopes / transportability.

The `FULL` view exposes them.

Gold is the exact minimal `EpistemicDelta` produced independently by the V0 kernel.

## Result 1 — representation semantic change is load-bearing

For the remint/material pair:

```text
fingerprint_TYPED(remint) == fingerprint_TYPED(material)
gold_delta(remint) != gold_delta(material)
```

Therefore no deterministic predictor restricted to the exact `TYPED` fingerprint can solve both members.

On the balanced pair:

```text
TYPED deterministic accuracy ceiling = 1/2
FULL deterministic accuracy ceiling  = 1
```

The difference is not “more graph topology”. It is the semantic distinction required to know whether old scoped failure knowledge remains applicable.

## Result 2 — obligation transportability is load-bearing

For the transportable/nontransportable pair:

```text
fingerprint_TYPED(transportable) == fingerprint_TYPED(nontransportable)
gold_delta(transportable) != gold_delta(nontransportable)
```

Again:

```text
TYPED deterministic accuracy ceiling = 1/2
FULL deterministic accuracy ceiling  = 1
```

Without the transportability coordinate, the learner cannot know whether the old obligation remains active or must become `UNKNOWN`, nor whether dependent claims remain entitled.

## Result 3 — combined panel

Combining the two hostile pairs gives four cases and two `TYPED` fingerprint classes, each containing two different targets:

```text
sample count                 = 4
unique TYPED fingerprints    = 2
TYPED deterministic ceiling  = 1/2
TYPED collision classes      = 2
unique FULL fingerprints     = 4
FULL deterministic ceiling   = 1
FULL collision classes       = 0
```

This is an exact finite information result. It does not depend on model capacity or training.

## What is supported

Within the frozen V0 semantics:

- **semantic representation identity** can be decision-relevant beyond occurrence/label identity;
- **scoped failure applicability across representation change** cannot be reconstructed from typed topology/status alone in the hostile pair;
- **obligation transportability** can be necessary to distinguish preserve from reopen/UNKNOWN;
- a state representation hiding these coordinates is non-identifying on the protected pair construction.

## What is not supported

This result does **not** establish:

- that V0 is a universal epistemic ontology;
- that every LLM needs explicit representation/failure/obligation coordinates;
- that a native neural state is better than serialization;
- that ORION invented belief revision, proof transport or provenance;
- that the exact coordinates will add value in natural language or real science;
- any LLM performance improvement.

## Relation to EA-1A analytic closure

The information result and learned-value result point in different directions and must both remain visible:

1. hiding the load-bearing coordinates creates exact non-identifiability;
2. once the **full** coordinates plus the exact intervention are visible, deterministic revision is sufficient and neural escalation is unjustified.

This is the desired ORION diagnosis:

```text
MISSING INFORMATION != MISSING MODEL CAPACITY
```

and:

```text
INFORMATION PRESENT + EXACT MECHANIC KNOWN
    -> exact mechanic gets first right of refusal.
```

## Scientific terminal

`EA1_TYPED_SCOPE_COORDINATES_LOAD_BEARING__FULL_V0_IDENTIFIES`

Together with `EA1_DONOR_EXACT_REVISION_SUFFICIENT`, this closes the exact EA-1 study without a learned-model positive.
