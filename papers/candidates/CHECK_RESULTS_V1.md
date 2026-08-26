# ORION-16–ORION-18 bounded mathematical check results V1

**Date:** 2026-08-17  
**Environment:** CPython 3.13.5, Linux x86_64  
**Authority:** local deterministic support only; clean-CI/independent reproduction remains open

The scripts use only Python's standard library and make no network, provider, model, judge, or LLM API call.

## ORION-16

Script: `orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py`

Observed deterministic counts:

- directed acyclic graphs enumerated over four labeled nodes: **543**;
- reopening/certification cases checked: **130,320**;
- separated-mechanic commutation cases checked: **1,536**;
- two-step non-escalating authority compositions checked: **8,192**;
- recursive self-loop countermodel: detected;
- candidate-controlled authorization countermodel: detected.

The enumeration checks implementation-level instances of downstream reopening, unaffected-state preservation, separated commutation and non-escalation. The general claims rely on the proofs in `manuscript/FORMAL_CORE_V1.md`.

## ORION-17

Script: `orion-17-epistemic-navigation-open-worlds/formal/check_countermodels.py`

Observed deterministic results:

- finite visible histories varied over all eight undirected edge subsets on three observed nodes;
- for every visible history, a complete and an incomplete hidden extension with identical observable signature was constructed;
- route-stop without task-stop authorization: confirmed;
- equal-output/independent-route counterexample: confirmed;
- disjoint-output/dependent-route counterexample: confirmed;
- fixed topology unreachable / reframed topology reachable instance: confirmed;
- complete preservation-map transfer and incomplete-map reopening fixtures: confirmed;
- mandatory-open obligation blocks task stop: confirmed.

## ORION-18

Script: `orion-18-epistemic-authority-autonomous-science/formal/check_authority_calculus.py`

Observed deterministic results:

- domain-pair authorization cases without coercions: **36**; only same-domain pairs authorized;
- explicit route-stop to task-stop coercion authorized only with a satisfied coverage obligation;
- scope narrowing accepted and scope widening rejected;
- additive evidence counterexamples generated for every finite blocker penalty from 0 through 100: **101**;
- dependency-grounded revocation propagated to the exact descendant closure;
- candidate-controlled constant-accept policy authorized externally false candidates;
- toy ORION-11–ORION-15 authority-gate embeddings represented the intended hard-obligation behavior.

## Limitations and next authority gates

- The scripts were exercised in the active analysis environment, not yet in repository CI.
- The finite enumerations do not prove unbounded theorems.
- The ORION-11–ORION-15 embeddings are toy fixtures until checked against exact current registry/protocol decisions.
- No result here establishes novelty or empirical value.
- Clean GitHub Actions execution, independent reproduction, proof-assistant formalization where useful, and nearest-work saturation remain required.
