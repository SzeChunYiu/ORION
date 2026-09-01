# ORION03.NATIVE_TYPED_MERGE_TRANSFER.v1

**Status:** `DESIGN_ONLY__NO_NATIVE_OUTCOME_AUTHORITY`  
**Scientific authority delta:** `NONE`

## Scientific question

Does the typed-merge obstruction observed in the bounded X.509 campaign occur under the **native authorization semantics of unrelated real trust systems**, or is it specific to that certificate setting?

The successor deliberately does **not** score the typed parent-witness rule as an empirical detector. Current ORION-03 already proves that this rule authorizes exactly the parent-authorized set; its zero unsafe merges / zero needless rejections relative to that target are analytic identities. The empirical questions here are instead:

1. whether a naive cross-parent merge creates native-authorized **hybrids** in real third-party systems; and
2. what real valid authority strict baselines discard to avoid those hybrids.

## Three native systems

Freeze **30 independent project/policy families**, 10 per system, before protected verifier outcomes:

1. **SIGSTORE_COSIGN** — real Sigstore/cosign verification material and policies under a pinned native cosign verifier. Parent configurations must expose at least two typed authority components whose naive set-union can be tested natively, for example trust-root/key material and signer/identity or attestation constraints.
2. **TUF_PYTHON_TUF** — real TUF metadata lineages under a pinned python-tuf verifier, with typed root/role/key/threshold/delegation components.
3. **IN_TOTO** — real in-toto layout/link/signing material under a pinned native in-toto verifier, with typed functionary/step/threshold/rule components.

A family must come from an independently maintained public lineage with immutable source/version identifiers. Synthetic toy families may be used as calibration controls but cannot count toward the 10-per-system confirmatory N.

If a system cannot supply ten independent eligible families without inventing ORION-authored authority semantics, return `CANNOT_CHECK_INSUFFICIENT_NATIVE_FAMILIES` for that system.

## Common adapter contract

For each family freeze two valid **parent authority contexts** `A` and `B` and a set of candidate objects/tasks before protected verification.

Every adapter must expose exactly these native decisions:

- `V_A(x)` — pinned native verifier accepts `x` under parent A;
- `V_B(x)` — pinned native verifier accepts `x` under parent B;
- `V_U(x)` — pinned native verifier accepts `x` under the registered **flat typed-component union** `U(A,B)`;
- optionally strict baselines such as native intersection/common-authority or reject-all where the native semantics permit an unambiguous implementation.

A **native hybrid** is a candidate satisfying

`V_U(x)=1 and V_A(x)=0 and V_B(x)=0`.

The typed parent-witness decision is the analytic target

`V_T(x) = V_A(x) or V_B(x)`.

`V_T` must be computed from the two native parent decisions, not by a third ORION-authored semantic engine. Consequently its agreement with the parent-authorized set is not an empirical endpoint.

## Flat-union registration

The naive union is fixed separately for each system **before** protected candidate verification. It may union only typed components that the native verifier actually consumes. It may not weaken a threshold, delete a rule, or introduce a new authorization primitive unless that transformation is itself the registered native meaning of union for that component type.

Every union adapter must emit:

- exact parent component inventory;
- component provenance `A`, `B`, or shared;
- merged native configuration bytes;
- pinned native verifier version and command/API call;
- a structural diff proving which components changed.

If there is no semantically defensible flat-union operation for a system, that system terminates `CANNOT_CHECK_NO_NATIVE_FLAT_UNION` rather than forcing a synthetic merge.

## Candidate construction without outcome leakage

For each family freeze at least **20 candidate tasks** before protected native outcomes, yielding a target of >=200 tasks/system and >=600 overall.

Candidate generation may use public structure and typed component provenance but may not query `V_A`, `V_B`, or `V_U` to decide whether a candidate is retained. Freeze the generator, RNG seeds or deterministic enumeration order, candidate hashes, and stopping rule first.

The frozen set should deliberately include:

- parent-valid positive controls from A and B;
- structurally cross-parent composites capable of exercising multiple typed components;
- known-malformed negative controls;
- untouched naturally occurring objects where available.

No candidate replacement is allowed after any protected native decision is opened.

## Hybrid localization

For every observed hybrid, emit a **cross-parent witness** that identifies at least one load-bearing typed contribution from A and at least one from B. Re-run the native verifier after ablating each claimed contribution separately.

A hybrid is `LOCALIZED` only when both parent provenance and ablation sensitivity are verified. Otherwise retain the native hybrid count but mark mechanism localization `CANNOT_CHECK_LOCALIZATION`.

This prevents a configuration bookkeeping error from being narrated as a typed cross-parent mechanism.

## Primary empirical endpoints

The family is the inference unit. Candidate tasks are not independent replicates.

Report per system and family:

1. number of native flat-union hybrids;
2. number of localized hybrids;
3. fraction of families with >=1 hybrid;
4. strict-baseline needless rejections among objects accepted by at least one parent;
5. native verifier failures/timeouts separately from rejections;
6. component counts and union deltas as descriptive covariates only.

The typed parent-witness arm is reported as the analytic reference `V_A OR V_B`, not as measured precision/recall.

## Cross-system support gate

A broad `NATIVE_CROSS_SYSTEM_HYBRID_NONVACUITY_SUPPORTED` terminal requires:

- all 30 registered families executed or an explicit fail-closed system terminal;
- at least **3/10 independent families with >=1 native hybrid in each of all three systems**;
- at least one `LOCALIZED` hybrid in each system;
- zero unresolved verifier-version/source-binding drift;
- all malformed controls rejected by the expected native layer;
- no post-outcome family/candidate deletion.

If only one or two systems show hybrids, report the exact bounded system-specific result; do not promote it to all-system generality. If no system meets the 3-family condition, the cross-system non-vacuity claim fails even if isolated candidate-level hybrids exist.

The `3/10` threshold is a breadth requirement, not a significance test. Exact family-level confidence intervals and the raw denominators must be reported separately.

## Strict-baseline utility gate

The paper may claim a safety/utility tradeoff for strict baselines only when, in every system supporting the hybrid claim, at least one strict baseline rejects parent-authorized objects in >=3 independent families. Cost or convenience metrics cannot substitute for native authorization loss.

## Adverse and CANNOT_CHECK outcomes

Retain without rescue:

- `NO_NATIVE_HYBRID_OBSERVED`;
- `HYBRID_ONLY_IN_ONE_SYSTEM`;
- `CANNOT_CHECK_NO_NATIVE_FLAT_UNION`;
- `CANNOT_CHECK_INSUFFICIENT_NATIVE_FAMILIES`;
- `CANNOT_CHECK_LOCALIZATION`;
- `CANNOT_CHECK_NATIVE_VERIFIER_REPRODUCTION`;
- `ADVERSE_PARENT_CONTEXT_INVALID`;
- `ADVERSE_CONTROL_FAILURE`.

No new threshold, component type, family replacement, or alternative union semantics may be chosen after protected outcomes under this identity.

## Claim boundary

A favourable result would establish that the ORION-03 obstruction is empirically non-vacuous under the registered native semantics of three distinct trust/policy ecosystems. It would not show that typed witness is a statistically learned detector, would not prove prevalence in all deployments, and would not establish human/institutional usability.