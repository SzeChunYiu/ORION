# ORION-16–ORION-18 bounded mathematical check results V2

**Date:** 2026-08-17  
**Environment:** CPython 3.13.5, Linux 6.18.35 x86_64 / glibc 2.41  
**Authority:** local deterministic support only; clean-CI/independent reproduction remains open  
**Relationship to V1:** additive successor. V1 is retained unchanged as historical evidence.

The synchronization pass repaired theorem boundaries in ORION-16/ORION-17 and widened ORION-18 timing/revocation cases. The updated checker logic was rerun in the active analysis environment. No network, provider, model, judge or LLM API was used by the checker logic.

## ORION-16 — history-aware effect/repair checks

Script: `orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py`

Observed deterministic counts retained from the exhaustive bounded core:

- DAGs over four labeled nodes: **543**;
- reopening/certification cases: **130,320**;
- scientific-projection separated-commutation cases: **1,536**;
- two-step non-escalating authority compositions: **8,192**.

New V2 boundary fixtures:

- same current scientific state under two independent execution orders: confirmed;
- ordered histories differ: confirmed;
- two-event histories are equivalent under the intended independent-event swap fixture: confirmed;
- later computational success does not erase an unresolved hard residual obligation: confirmed;
- explicit authorized discharge positive control: confirmed.

The commutation result is **not** evidence of whole-state equality. Audit chronology is intentionally retained.

## ORION-17 — extension ambiguity and atlas-transport checks

Script: `orion-17-epistemic-navigation-open-worlds/formal/check_countermodels.py`

Observed deterministic results:

- all **8** undirected edge subsets on the three visible nodes were used to construct extension-ambiguous complete/incomplete world pairs with the same observed signature;
- counterexample with **no closure-certificate token and no extension ambiguity**: confirmed;
- route-stop without task-stop authorization: confirmed;
- equal-output/independent-route and disjoint-output/dependent-route counterexamples: confirmed;
- fixed-chart unreachable / reframed-chart reachable instance: confirmed;
- complete support-map transport and incomplete-map reopening fixtures: confirmed;
- content-bound evidence preserved while a changed objective is not covered by the old closure scope: confirmed;
- mandatory-open obligation blocks task stop: confirmed;
- fixed-chart negative control in which reframing is unnecessary: confirmed.

The first result applies to the deliberately rich constructed admissible class; it is not a claim that every certificate-free model class is extension-ambiguous.

## ORION-18 — cross-domain authority, timing and revocation checks

Script: `orion-18-epistemic-authority-autonomous-science/formal/check_authority_calculus.py`

Observed deterministic results:

- domain-pair authorization cases without coercions: **36**; only same-domain pairs authorize;
- explicit `route_stop -> task_stop` conversion authorizes only with the required coverage obligation satisfied;
- scope narrowing accepted and scope widening rejected;
- stale-epoch authorization replay rejected;
- additive evidence counterexamples generated for every finite blocker penalty `0..100`: **101**;
- revoking one evidence path reaches its dependent authorization node while leaving a second independent support path intact, allowing re-derivation in the toy semantics;
- single-path authorization loses its only support under revocation: confirmed;
- post-hoc refusal after an irreversible commit is non-preventive: confirmed;
- candidate-controlled constant-accept admission countermodel: confirmed;
- clean authorized action with all hard obligations satisfied remains allowed: confirmed;
- ORION-11–ORION-15 toy embedding vocabulary remains representable.

## Interpretation

V2 strengthens the executable correspondence between the claim ledgers and current formal cores. It does **not** establish:

- unbounded theorem correctness;
- semantic soundness of real cross-domain coercions;
- exact ORION-11–ORION-15 decision equivalence;
- donor-faithful embeddings;
- empirical advantage;
- novelty or publication readiness.

## Next reproducibility gates

1. run the repository scripts themselves in clean GitHub Actions rather than only active analysis/local environments;
2. capture immutable stdout/result hashes;
3. add exhaustive bounded generation for ORION-17/ORION-18 dimensions beyond the current fixtures;
4. map ORION-11–ORION-15 exact protocol decisions into executable fixtures;
5. add donor-native ETAS/FAVA/planning/rollback fixtures where licensing/code permits;
6. independently replay and attest the results.