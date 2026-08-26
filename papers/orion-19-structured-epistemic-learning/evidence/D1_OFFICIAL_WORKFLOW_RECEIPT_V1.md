# ORION-19 D1 official workflow receipt V1 — pending merge authority

This receipt preserves the completed official D1 workflow result before its Actions artifact expires. It is **not yet a merged-evidence authorization**: PR #519 must still pass its exact-head repository and protected ORION-16–ORION-18 gates and merge before the manuscript evidence builder may promote these numbers.

## Execution identity

- PR: #519 — `ORION-19 D1: exact whole-domain method-structure transfer`;
- result-bearing head: `b82451da53bebd095b5a5b225781cef209c8339b`;
- workflow: `p9-d1-method-transfer`;
- workflow run: `32235110762`;
- merge-ref executed by Actions: `e69606d5ee7e5e035ab6374202f9e62c154579ae`;
- focused tests: `11 passed`;
- Actions artifact id: `9363345932`;
- artifact ZIP SHA-256: `bcf9d73c56c481e63c7acbaba00a0ca16c255db11b9e9d393b17f32d39f939ed`;
- official result digest: `sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a`;
- dataset manifest digest: `sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c`;
- official terminal: `D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED`.

## Frozen protected test

Held-out domain: `transactional_workflows`.

Protected test sample count: `128`.

| Arm | Selected model | Dev accuracy | Test accuracy | Macro F1 | Double corruption | UNRESOLVED |
|---|---:|---:|---:|---:|---:|---:|
| `TRANSCRIPT_BAG` | logistic-C0.1 | 0.3333333333333333 | 0.25 | 0.13333333333333333 | 0.0 | 0.0 |
| `UNTYPED_PAIR` | logistic-C0.1 | 0.875 | 0.90625 | 0.9128856624319419 | 1.0 | 1.0 |
| `TYPED_RELATIONAL` | logistic-C0.1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| `TYPED_SERIALIZED_BAG` | logistic-C1 | 0.9583333333333334 | 0.5 | 0.2222222222222222 | 1.0 | 0.0 |

Exact typed-relational comparator: `1.0` accuracy / `1.0` macro-F1 / `1.0` double-corruption / `1.0` UNRESOLVED.

Headline bounded contrasts:

- typed relational minus transcript: `+0.75` absolute accuracy;
- typed relational minus same-information typed serialization: `+0.50` absolute accuracy.

## Independent pre-artifact comparison

The independent verifier/expectation object was frozen on main before the official D1 artifact was read:

`research/extensions/p9-structured-neural/verification/INDEPENDENT_REPLAY_EXPECTATIONS_V1.json`.

Coordinate-by-coordinate comparison between the official artifact and that frozen independent reimplementation produced:

`MATERIAL_DISCREPANCIES = 0`.

The independent expectation predicted every selected arm/model and every headline D1 metric above, including the two protected contrasts and exact comparator result.

## Exact claim ceiling

Supported only if #519 merges unchanged:

> On this prospectively frozen exact authored/procedural benchmark, typed relational method coordinates transfer across the held-out transactional-workflow domain and unseen corruption combinations better than reminted transcript, untyped-pair, and same-information typed-serialization controls.

This does **not** establish:

- natural-science paper understanding;
- general graph-neural-network superiority;
- a universal structural representation;
- LLM reasoning improvement;
- causal mechanism discovery;
- scientific authority.

## Current authority

`OFFICIAL_WORKFLOW_GREEN__MERGE_AUTHORITY_PENDING`.

Do not replace the D1 `PENDING_OFFICIAL_RECEIPT` manuscript placeholders from this receipt alone. Promotion requires #519 merged at the same scientific content, followed by the final ORION-19 evidence builder / independent verification / novelty gates.
